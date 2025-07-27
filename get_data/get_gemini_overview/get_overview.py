"""
并发执行，减少git action 的执行时间
"""

from datetime import datetime
from logging import log
from dotenv import load_dotenv
import json
from tqdm import tqdm
from google import genai # 修正：使用推荐的导入别名
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
        ### 修正：更保守的默认设置 ###
        "max_concurrency": 10,  # 并发数，从一个很小的值开始，比如2
        "rate_limit_sleep": 20, # 每次API调用后等待的秒数，用于控制RPM
        "max_api_retries": 3,  # 单个API请求失败后的最大重试次数
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

# ... (check_ghostscript, compress_pdf等函数保持不变，这里省略以保持简洁) ...
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
    import subprocess
    import tempfile
    try:
        if output_path is None: output_path = input_path
        temp_file = None
        if output_path == input_path:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_output = temp_file.name
            temp_file.close()
        else: temp_output = output_path
        cmd = ['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', f'-dPDFSETTINGS=/{quality}', '-dNOPAUSE', '-dQUIET', '-dBATCH', f'-sOutputFile={temp_output}', input_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            if temp_file:
                import shutil
                shutil.move(temp_output, output_path)
            return True
        else:
            print(f"Ghostscript压缩失败：{result.stderr}")
            if temp_file and os.path.exists(temp_output): os.unlink(temp_output)
            return False
    except Exception as e:
        print(f"Ghostscript压缩失败：{e}")
        return False

def compress_pdf(input_path, output_path=None, quality="screen"):
    if not GHOSTSCRIPT_AVAILABLE: return False, 0, 0
    if not os.path.exists(input_path): return False, 0, 0
    original_size = os.path.getsize(input_path)
    success = compress_pdf_with_ghostscript(input_path, output_path, quality)
    if success:
        compressed_size = os.path.getsize(output_path if output_path else input_path)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        print(f"PDF压缩成功(ghostscript): {original_size//1024}KB -> {compressed_size//1024}KB (压缩率: {compression_ratio:.1f}%)")
        return True, original_size, compressed_size
    else: return False, original_size, original_size

def get_response(file_path, api_key, args):
    update_info = CONFIG.update_info[args.update]
    prompt = update_info.prompt
    model = CONFIG.gemini.model
    
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
        # 打印更详细的错误信息
        print(f"线程 {threading.get_ident()} 报错：{e}  api_key: ...{api_key[-4:]}")
        raise e

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

def worker(paper_slice, api_keys_for_thread, semaphore, file_dir, lock, thread_idx, args):
    field = CONFIG.update_info[args.update].field
    count = 0
    progress_bar = tqdm(paper_slice, desc=f"线程{thread_idx+1} key=...{api_keys_for_thread[0][-4:]}", position=thread_idx)
    for paper in progress_bar:
        if paper.get(field):
            continue

        pdf_url = paper.get("pdf_url")
        if not pdf_url:
            continue

        pdf_file = f"{paper.get('order', 'temp')}_thread{thread_idx+1}.pdf"
        if not download_file_with_progress(url=pdf_url, filename=pdf_file):
            continue

        file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
        if GHOSTSCRIPT_AVAILABLE and file_size_mb > CONFIG.ghostscript.compress_threshold_mb:
            compress_pdf(pdf_file, quality=CONFIG.ghostscript.quality)

        res = ""
        # 使用信号量来严格控制并发
        with semaphore:
            api_key = api_keys_for_thread[count % len(api_keys_for_thread)]
            progress_bar.set_description(f"线程{thread_idx+1} key=...{api_key[-4:]}")
            try:
                for attempt in range(CONFIG.gemini.max_api_retries):
                    try:
                        res = get_response(file_path=pdf_file, api_key=api_key, args=args)
                        break
                    except Exception as e:
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            wait_time = (2 ** attempt) + 1
                            progress_bar.set_description(f"线程{thread_idx+1} key=...{api_key[-4:]} 遇429, 第{attempt+1}次重试, 等待{wait_time}s")
                            time.sleep(wait_time)
                        else:
                            print(f"线程{thread_idx+1} 遇到不可恢复错误: {e}")
                            break
                paper[field] = res
                time.sleep(CONFIG.gemini.rate_limit_sleep)
            finally:
                pass
        os.remove(pdf_file)
        count += 1
        if res:
            with lock:
                with open(file_dir, "w", encoding="utf-8") as f:
                    json.dump(file_data_global, f, ensure_ascii=False, indent=4)

# 修正：将n_threads的计算移到process_file内部，使其更合理
def process_file(file_dir, args, _):
    global file_data_global
    try:
        with open(file_dir, "r", encoding="utf-8") as f:
            file_data_global = json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_dir}")
        return []
    
    papers = file_data_global
    if not papers: return []
    
    api_key_list = [k for k in CONFIG.gemini.api_key_lists if k]
    field = CONFIG.update_info[args.update].field

    unprocessed_papers = [paper for paper in papers if not paper.get(field)]
    if not unprocessed_papers:
        print(f"{os.path.basename(file_dir)} 所有论文均已处理。")
        return []
        
    print(f"{os.path.basename(file_dir)} 共有 {len(unprocessed_papers)}/{len(papers)} 篇论文未处理。")
    
    n_threads = min(CONFIG.gemini.max_concurrency, len(api_key_list), len(unprocessed_papers))
    if n_threads == 0:
        print("API key或待处理论文不足，无法启动线程。")
        return unprocessed_papers

    semaphore = threading.Semaphore(n_threads)
    threads = []
    lock = threading.Lock()

    # 均分论文
    paper_slices = [[] for _ in range(n_threads)]
    for idx, paper in enumerate(unprocessed_papers):
        paper_slices[idx % n_threads].append(paper)
    # 均分key
    key_slices = [[] for _ in range(n_threads)]
    for idx, key in enumerate(api_key_list):
        key_slices[idx % n_threads].append(key)

    for i in range(n_threads):
        print(f"线程 {i+1} 使用 API key: ...\n{('__').join(k[-4:] for k in key_slices[i])}\n")
        t = threading.Thread(target=worker, args=(paper_slices[i], key_slices[i], semaphore, file_dir, lock, i, args))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    with open(file_dir, "w", encoding="utf-8") as f:
        json.dump(file_data_global, f, ensure_ascii=False, indent=4)
    print(f"最终文件已保存 -> {file_dir}")
    
    final_unprocessed_papers = [paper.get("order") for paper in papers if not paper.get(field)]
    return final_unprocessed_papers

def main():
    parser = argparse.ArgumentParser(description="使用Gemini API处理论文摘要")
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument('--task', type=str, default="conference", help='任务类型')
    parser.add_argument('--date', type=str, default=today_str, help='需要处理的日期文件名 (例如 2025-07-17)')
    # 修正：让命令行参数可以覆盖配置文件，方便调试
    parser.add_argument('--file', type=str, default="CVPR.2023", help='需要处理的文件名')
    parser.add_argument('--update', type=str, default="gemini", help='需要更新的字段名')
    parser.add_argument('--concurrency', type=int, help='覆盖并发数设置')
    parser.add_argument('--sleep', type=int, help='覆盖速率限制延时')
    
    args = parser.parse_args()

    # 允许命令行覆盖配置
    if args.concurrency:
        CONFIG.gemini.max_concurrency = args.concurrency
    if args.sleep:
        CONFIG.gemini.rate_limit_sleep = args.sleep

    print(f"当前配置: 最大并发数={CONFIG.gemini.max_concurrency}, 请求间隔={CONFIG.gemini.rate_limit_sleep}s")

    # ... (构建 file_list 的逻辑保持不变) ...
    if args.task == "conference":
        file_list = [os.path.join(CONFIG.data.base_dir, f"{args.file}.json")]
    elif args.task == "arxiv":
        date = args.date
        year = date[:4]
        month = date[5:7]
        categories = ["cs.CV", "cs.AI", "cs.LG"]
        file_list = [os.path.join(CONFIG.data.base_dir, year, month, f"{date}_{category}.json") for category in categories]
    else: file_list = []

    api_key_list = [key for key in CONFIG.gemini.api_key_lists if key]
    if not api_key_list:
        print("错误：未找到任何有效的GEMINI_API_KEYS。")
        return
        
    key_queue = queue.Queue()
    for k in api_key_list:
        key_queue.put(k)

    max_file_retries = 3 # 文件级别的大重试
    for file_dir in file_list:
        if not os.path.exists(file_dir):
            print(f"警告：文件 {file_dir} 不存在，跳过。")
            continue
            
        for i in range(max_file_retries):
            res = process_file(file_dir, args, key_queue)
            if not res: # 如果返回空列表，说明全部处理完成
                print(f"文件 {file_dir} 全部处理完成。")
                break
            
            print(f"文件 {file_dir} 第{i+1}/{max_file_retries}轮处理后，仍有 {len(res)} 篇未成功。")
            if i < max_file_retries - 1:
                print("5秒后进行下一轮处理...")
                time.sleep(5)
        else: # for-else 循环，如果循环正常结束（没有被break），则执行
            print(f"警告：文件 {file_dir} 经过 {max_file_retries} 轮处理后，仍有未完成的论文。")


if __name__ == "__main__":
    main()