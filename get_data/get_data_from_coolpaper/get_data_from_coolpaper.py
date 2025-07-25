import json
import requests
from bs4 import BeautifulSoup
import os
import argparse
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm.contrib.concurrent import thread_map


def get_paper_info(file="CVPR.2025",base_dir="public/data"):
    conference = file.split('.')[0]
    year = file.split('.')[1]
    os.makedirs(base_dir, exist_ok=True)
    file_name = os.path.join(base_dir, f"{conference}.{year}.json")
    if os.path.exists(file_name):
        print(f"{file_name} 已存在, 跳过下载。")
        return file_name
    
    url = f"https://papers.cool/venue/{conference}.{year}/feed"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return []
    soup = BeautifulSoup(response.text, 'xml')
    papers = []
    all_entries = soup.find_all('entry')
    for i, entry in enumerate(all_entries):
        paper = {
            'id': entry.id.text if entry.id else "",
            'conference': conference,
            'year': year,
            'order': i + 1,
            'title': entry.title.text if entry.title else "",
            'subjects': "",
            'original_url': "",
            'pdf_url': "",
            'authors': [author.find('name').text if author.find('name') else "" for author in entry.find_all('author')], 
            'abstract': entry.summary.text if entry.summary else "",
            'gemini2.5flash': "",
            'overall_idea': ""
        }
        papers.append(paper)
    
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=4, separators=(',', ': '))
    print(f"Data saved to {file_name}")
    return file_name



def complete_paper_info(paper):
    cool_url = paper['id']
    response = requests.get(cool_url)
    if response.status_code != 200:
        print(f"Failed to fetch paper details from {paper['order']} {cool_url}. Status code: {response.status_code}")
        return paper
    soup = BeautifulSoup(response.text, 'html.parser')

    # 1. HTML链接
    html_link_tag = soup.find('a', title='1/1')
    paper['original_url'] = html_link_tag['href'] if html_link_tag and html_link_tag.has_attr('href') else ""

    # 2. PDF链接
    pdf_link_tag = soup.find('a', class_='title-pdf')
    pdf_url = ""
    if pdf_link_tag and pdf_link_tag.has_attr('onclick'):
        match = re.search(r"/pdf\?url=([^']+)", pdf_link_tag['onclick'])
        if match:
            pdf_url = match.group(1)
            # 若链接不是完整URL，可补全域名
            if not pdf_url.startswith("http"):
                pdf_url = "https://papers.cool" + pdf_url
    paper['pdf_url'] = pdf_url

    # 3. subject-1 文本
    subject_tag = soup.find('a', class_='subject-1')
    paper['subjects'] = subject_tag.text.strip() if subject_tag else ""

    return paper
    
    

def main():
    parser = argparse.ArgumentParser(description="Fetch paper data from cool papers site.")
    parser.add_argument('--file', type=str, default='CVPR.2025', help='Conference file name (e.g., CVPR.2025)')
    parser.add_argument('--base_dir', type=str, default='public/data', help='Base directory to save the data')
    args = parser.parse_args()
    
    file_name = get_paper_info(file=args.file, base_dir=args.base_dir)
    with open(file_name, "r", encoding="utf-8") as f:
        papers = json.load(f)
    # 多线程处理每个 paper，tqdm 多线程兼容
    import math
    from threading import Thread

    def process_and_remove_id(paper):
        # 只处理 original_url 为空的 paper
        if paper.get('original_url') == "":
            paper = complete_paper_info(paper)
            if 'id' in paper:
                del paper['id']
        return paper

    def worker(paper_chunk, result_list, idx):
        local_result = []
        for paper in tqdm(paper_chunk, desc=f"Thread-{idx+1}", position=idx):
            # print(f"Thread-{idx+1} start paper order={paper.get('order')}")
            local_result.append(process_and_remove_id(paper))
            # print(f"Thread-{idx+1} end paper order={paper.get('order')}")
        result_list[idx] = local_result

    # 先筛选出未处理的paper
    unprocessed_papers = [paper for paper in papers if paper.get('original_url') == ""]
    print(f"Total papers: {len(papers)}, Unprocessed papers: {len(unprocessed_papers)}")

    max_workers = 32
    if len(unprocessed_papers) == 0:
        print("No unprocessed papers, skipping processing.")
    else:
        chunk_size = math.ceil(len(unprocessed_papers) / max_workers)
        paper_chunks = [unprocessed_papers[i*chunk_size:(i+1)*chunk_size] for i in range(max_workers)]
        results = [None] * max_workers
        threads = []

        for idx, chunk in enumerate(paper_chunks):
            t = Thread(target=worker, args=(chunk, results, idx))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 用已处理结果替换原papers中的内容
        processed_papers = [paper for chunk in results if chunk for paper in chunk]
        order_to_paper = {paper['order']: paper for paper in processed_papers}
        for i, paper in enumerate(papers):
            if paper.get('original_url') == "" and paper['order'] in order_to_paper:
                papers[i] = order_to_paper[paper['order']]

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()