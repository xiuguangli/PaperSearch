"""
并发执行，减少git action 的执行时间
"""

from datetime import datetime
from logging import log
from dotenv import load_dotenv
import json
from tqdm import tqdm
from google import genai
import time
import os
import requests
from google.genai import types
import pathlib
import argparse
from box import Box
import threading
import queue

load_dotenv()
PROMPT1 = "用中文讲一下这篇文章的内容，并举一个例子说明问题和方法流程。"

PROMPT2 = """
请以文章作者的身份，深入剖析这篇文章，详细回顾您从选题到提出方法解决问题整个思维决策过程。最好是通过一个具体的例子进行说明。
请着重阐述：
0.您为什么选择这个研究内容。
1.您是如何一步步构思和界定研究问题的。
2.为了解决该问题，您在选择理论框架、研究方法和数据分析策略时，经历了怎样的思考、权衡和取舍。
3.在研究的每个关键阶段，您做出了哪些重要决策，并能解释这些决策背后的逻辑和依据。
"""

# 配置参数
CONFIG = Box({
    "ghostscript": {
        "quality": "screen",
        "compress_threshold_mb": 20,
    },
    "gemini": {
        "model": "gemini-2.5-flash",
        "api_key_lists": os.environ.get("GEMINI_API_KEYS", "").split(","),
    },
    "data": {
        "base_dir":"public/data",
    },
    "processing": {
        "save_interval": 10,
    },
    "update_info":{
         "gemini":{
            "field": "gemini2.5flash",
            "prompt": PROMPT1,
         },
         "overall":{
            "field": "overall_idea",
            "prompt": PROMPT2,
         }
    }
    
})

# 检查是否有Ghostscript可用
def check_ghostscript():
    """检查系统是否安装了Ghostscript"""
    import subprocess
    try:
        subprocess.run(['gs', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

GHOSTSCRIPT_AVAILABLE = check_ghostscript()
if GHOSTSCRIPT_AVAILABLE:
    print("Ghostscript已安装，PDF压缩功能可用")
else:
    print("未安装Ghostscript，将跳过压缩步骤")

def compress_pdf_with_ghostscript(input_path, output_path=None, quality="screen"):
    """
    使用Ghostscript压缩PDF文件，通常能获得最佳压缩效果
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径，如果为None则覆盖原文件
        quality: 压缩质量 "screen"(最高压缩), "ebook"(中等), "printer"(低压缩)
    
    Returns:
        bool: 压缩是否成功
    """
    import subprocess
    import tempfile
    
    try:
        if output_path is None:
            output_path = input_path
            
        temp_file = None
        if output_path == input_path:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_output = temp_file.name
            temp_file.close()
        else:
            temp_output = output_path
        
        cmd = [
            'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS=/{quality}', '-dNOPAUSE', '-dQUIET', '-dBATCH',
            '-dColorImageResolution=72', '-dGrayImageResolution=72',
            '-dMonoImageResolution=150', '-dColorImageDownsampleType=/Bicubic',
            '-dGrayImageDownsampleType=/Bicubic', '-dMonoImageDownsampleType=/Bicubic',
            '-dAutoFilterColorImages=false', '-dAutoFilterGrayImages=false',
            '-dColorImageFilter=/DCTEncode', '-dGrayImageFilter=/DCTEncode',
            '-dEncodeColorImages=true', '-dEncodeGrayImages=true',
            '-dEncodeMonoImages=true', '-dJPEGQ=25',
            '-dDownsampleColorImages=true', '-dDownsampleGrayImages=true',
            '-dDownsampleMonoImages=true', f'-sOutputFile={temp_output}',
            input_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if temp_file:
                import shutil
                shutil.move(temp_output, output_path)
            return True
        else:
            print(f"Ghostscript压缩失败：{result.stderr}")
            if temp_file and os.path.exists(temp_output):
                os.unlink(temp_output)
            return False
            
    except Exception as e:
        print(f"Ghostscript压缩失败：{e}")
        return False

def compress_pdf(input_path, output_path=None, quality="screen"):
    """
    使用Ghostscript压缩PDF文件
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径，如果为None则覆盖原文件
        quality: 压缩质量 "screen"(最高压缩), "ebook"(中等), "printer"(低压缩)
    
    Returns:
        tuple: (是否成功, 压缩前大小, 压缩后大小)
    """
    if not GHOSTSCRIPT_AVAILABLE:
        print("Ghostscript不可用，跳过压缩")
        return False, 0, 0
    
    if not os.path.exists(input_path):
        print(f"文件不存在: {input_path}")
        return False, 0, 0
    
    original_size = os.path.getsize(input_path)
    
    success = compress_pdf_with_ghostscript(input_path, output_path, quality)
    
    if success:
        compressed_size = os.path.getsize(output_path if output_path else input_path)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        print(f"PDF压缩成功(ghostscript): {original_size//1024}KB -> {compressed_size//1024}KB (压缩率: {compression_ratio:.1f}%)")
        return True, original_size, compressed_size
    else:
        return False, original_size, original_size

def get_response(file_path, api_key_list, count,args):
    update_info = CONFIG.update_info[args.update]
    prompt = update_info.prompt
    model = CONFIG.gemini.model
    index = count % len(api_key_list)
    api_key = api_key_list[index]
    
    client = genai.Client(api_key=api_key)
    file = pathlib.Path(file_path).read_bytes()
    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(
                    data=file,
                    mime_type='application/pdf',
                ),
                prompt
                ],
        )
        if response.text == None:
            return ""
        return response.text
    except Exception as e:
        print(f"报错：{e}  api_key: {api_key}")
        return ""

def download_file_with_progress(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            for data in response.iter_content(chunk_size=8192):
                file.write(data)
        return True
    except Exception as e:
        print(f"下载失败: {url}, 原因: {e}")
        return False

def process_file(file_dir, args, key_queue):
    def worker(paper_slice, key_queue, field, file_dir, lock, thread_idx):
        count = 0
        for paper in tqdm(paper_slice, desc=f"线程{thread_idx+1} 处理论文: {os.path.basename(file_dir)}"):
            if paper.get(field) != None and paper.get(field)!="":
                continue

            pdf_url = paper.get("pdf_url")
            if not pdf_url:
                print(f"跳过没有PDF链接的论文: {paper.get('order', '未知标题')}")
                continue

            pdf_file = f"{paper.get('order', 'temp')}_thread{thread_idx+1}.pdf"

            if not download_file_with_progress(url=pdf_url, filename=pdf_file):
                continue

            file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
            if GHOSTSCRIPT_AVAILABLE and file_size_mb > CONFIG.ghostscript.compress_threshold_mb:
                print(f"文件大小 {file_size_mb:.2f}MB，启用压缩...")
                compress_pdf(pdf_file, quality=CONFIG.ghostscript.quality)

            # 从全局 key 队列获取 key，处理后20秒再放回
            api_key = key_queue.get()
            try:
                res = get_response(file_path=pdf_file, api_key_list=[api_key], count=0, args=args)
            finally:
                threading.Timer(20, key_queue.put, args=(api_key,)).start()
            count += 1
            paper[field] = res
            os.remove(pdf_file)

            # 线程安全保存
            if count % CONFIG.processing.save_interval == 0:
                with lock:
                    with open(file_dir, "w", encoding="utf-8") as f:
                        json.dump(file_data, f, ensure_ascii=False, indent=4)
                        print(f"线程{thread_idx+1} 已处理 {count} 篇论文，文件已保存。")
            # break

    try:
        with open(file_dir, "r", encoding="utf-8") as f:
            file_data = json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_dir}")
        return []
    if args.task == "conference":
        papers = file_data.get("papers", [])
    elif args.task == "arxiv":
        papers = file_data
    if not papers:
        print(f"{file_dir}文件中没有找到 'papers' 列表。")
        return []

    api_key_list = CONFIG.gemini.api_key_lists
    field = CONFIG.update_info[args.update].field
    n_threads = min(8, len(api_key_list))  # 限制最大线程数，防止线程过多
    if n_threads == 0:
        print("API key数量不足，请检查API key配置。")
        return []
    threads = []
    lock = threading.Lock()

    # 只分配未处理的论文，每个线程处理 unprocessed_papers[i] for i % n_threads == thread_idx
    unprocessed_papers = [paper for paper in papers if paper.get(field) is None or paper.get(field) == ""]
    if not unprocessed_papers:
        print(f"{file_dir} 所有论文均已处理，无需分配。")
        return []
    print(f"{file_dir} 共有 {len(unprocessed_papers)} 篇论文未处理。")
    paper_slices = [[] for _ in range(n_threads)]
    for idx, paper in enumerate(unprocessed_papers):
        paper_slices[idx % n_threads].append(paper)
    for i in range(n_threads):
        t = threading.Thread(target=worker, args=(paper_slices[i], key_queue, field, file_dir, lock, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # 全部线程结束后保存一次
    with open(file_dir, "w", encoding="utf-8") as f:
        json.dump(file_data, f, ensure_ascii=False, indent=4)
    print(f"最终文件已保存 -> {file_dir}")
    final_unprocessed_papers = [paper.get("order") for paper in papers if paper.get(field) is None or paper.get(field) == ""]
    return final_unprocessed_papers


def main():
    parser = argparse.ArgumentParser(description="使用Gemini API处理论文摘要")
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument('--task', type=str, default="conference", help='任务类型 (例如 conference 或 arxiv)。arxiv 和 date 相关，conference 和 file 相关')
    parser.add_argument('--date', type=str, default=today_str, help='需要处理的日期文件名 (例如 2025-07-17)')
    parser.add_argument('--file', type=str, default="CVPR.2025", help='需要处理的文件名 (例如 CVPR.2025)')
    parser.add_argument('--update', type=str, default="overall", help='需要更新的字段名 (例如 overall 和 gemini)')

    args = parser.parse_args()

    # 构建 file_list
    if args.task == "conference":
        file_list = [os.path.join(CONFIG.data.base_dir, f"{args.file}.json")]
    elif args.task == "arxiv":
        date = args.date
        year = date[:4]
        month = date[5:7]
        categories = ["cs.CV", "cs.AI", "cs.LG"]
        file_list = [os.path.join(CONFIG.data.base_dir, year, month, f"{date}_{category}.json") for category in categories]
    else:
        file_list = []
        print("file_list为空，无效的任务")
        return

    api_key_list = CONFIG.gemini.api_key_lists
    key_queue = queue.Queue()
    for k in api_key_list:
        key_queue.put(k)

    max_retry = 3
    retry_count = 0
    for file_dir in file_list:
        res = process_file(file_dir, args, key_queue)
        while len(res)>0 and retry_count < max_retry:
            print(f"第{retry_count+1}/{max_retry}次重试，未处理成功的论文数：{len(res)}, 论文列表：{res}")
            res = process_file(file_dir, args, key_queue)
            retry_count += 1
        print(f"经历过{retry_count}次重试，文件 {file_dir} 处理完成，未处理论文数：{len(res)}，论文列表：{res}")
        

if __name__ == "__main__":
    main()
    # python 1.py --task conference --file CVPR.2025 --update overall
    # python 1.py --task arxiv --date 2025-07-18