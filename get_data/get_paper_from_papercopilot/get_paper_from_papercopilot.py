import requests
import json
import argparse
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import thread_map  # tqdm自带多线程进度条
import logging, colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(asctime)s %(log_color)s[%(filename)-15s]%(reset)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Fetch papers from PaperCopilot")
    parser.add_argument('--conference', type=str, default="iccv", help='Conference name (e.g., iccv)')
    parser.add_argument('--year', type=str, default="2025", help='Conference year')
    args = parser.parse_args()
    
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{args.conference.upper()}.{args.year}.json")
    url = f"https://github.com/papercopilot/paperlists/raw/refs/heads/main/{args.conference}/{args.conference}{args.year}.json"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Failed to fetch data from {url}")
        return 1
    all_papers_src = response.json()
    all_papers = []
    for i, entry in enumerate(all_papers_src):
        paper = {
            'conference': args.conference.upper(),
            'year': args.year,
            'order': i + 1,
            'title': entry["title"],
            'subjects': entry["status"],
            'original_url': entry["site"],
            'pdf_url': "",
            'authors': [a.strip() for a in entry["author"].split(",")],
            'abstract': "",
            'gemini2.5flash': "",
            'overall_idea': ""
        }
        all_papers.append(paper)
    if not os.path.exists(output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_papers, f, indent=4, ensure_ascii=False)
        logger.info(f"{args.conference.upper()}{args.year} paper data is saved to {output_file}")
    else:
        logger.info(f"{args.conference.upper()}{args.year} paper data already exists at {output_file}")

    with open(output_file, 'r', encoding='utf-8') as f:
        all_papers = json.load(f)
    all_unprocessed_papers = [paper for paper in all_papers if paper['abstract']==""]
    from concurrent.futures import ThreadPoolExecutor
    import math
    
    def process_paper_list(paper_list, pbar):
        for paper in paper_list:
            paper['abstract'] = get_abstract(paper)
            pbar.update(1)
    
    num_threads = 32
    total_papers = len(all_unprocessed_papers)
    chunk_size = math.ceil(total_papers / num_threads)
    chunks = [all_unprocessed_papers[i*chunk_size:(i+1)*chunk_size] for i in range(num_threads)]

    
    try:
        with tqdm(total=total_papers, desc="Fetching abstracts") as pbar:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for chunk in chunks:
                    if chunk:  # 跳过空chunk
                        futures.append(executor.submit(process_paper_list, chunk, pbar))
                for future in futures:
                    future.result()  # 等待所有线程结束
    except Exception as e:
        logger.error(f"Exception occurred during abstract fetching: {e}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_papers, f, ensure_ascii=False, indent=4)
        raise
    finally:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_papers, f, ensure_ascii=False, indent=4)
    
def get_abstract(paper):
    try:
        url = paper.get("original_url", "")
        order = paper.get("order", "")
        if not url:
            logger.error(f"{order} --> No original URL provided for the paper")
            return ""
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"{order} --> Failed to fetch abstract from {url}")
            return ""
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.find(id='abstractExample').get_text(strip=True, separator=' ').replace("Abstract: ", "").strip()
        return text
    except Exception as e:
        logger.error(f"{order} --> Exception in get_abstract: {e}")
        return ""


if __name__ == "__main__":
    main()
