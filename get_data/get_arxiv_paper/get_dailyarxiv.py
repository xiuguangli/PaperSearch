import requests
from bs4 import BeautifulSoup
import argparse
from datetime import datetime
import re
import time
import os
import logging
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def get_papers_from_arxiv(category="cs.CV", date="2025-07-17"):
    url = f"https://arxiv.org/catchup/{category}/{date}?abs=True"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return [] 
    soup = BeautifulSoup(response.text, 'html.parser')
    
    papers = []
    all_dt = soup.find_all('dt')

    idx = 1
    for idx, dt in enumerate(all_dt):
        # 跳过包含(replaced)的论文
        if dt.text and "(replaced)" in dt.text:
            continue

        dd = dt.find_next_sibling('dd')
        if not dd:
            continue

        paper_info = {
            'order': idx + 1,  # 从1开始计数
            'date': date,
            'date_url': url,
        }
        
        # 从 <dt> 中提取 arXiv ID 和链接
        arxiv_id_tag = dt.find('a', id=re.compile(r'^\d+\.\d+$'))
        if arxiv_id_tag:
            paper_info['arxiv_id'] = arxiv_id_tag.get('id', '')
            paper_info['abs_url'] = 'https://arxiv.org' + arxiv_id_tag.get('href', '')
        else:
            continue
        
        pdf_tag = dt.find('a', title='Download PDF')
        if pdf_tag and pdf_tag.get('href'):
            paper_info['pdf_url'] = 'https://arxiv.org' + pdf_tag.get('href')
        else:
            paper_info['pdf_url'] = ''

        # 从 <dd> 中提取详细信息
        meta_div = dd.find('div', class_='meta')
        if meta_div:
            title_div = meta_div.find('div', class_='list-title')
            if title_div:
                title_span = title_div.find('span', class_='descriptor')
                if title_span:
                    title_span.extract() # 移除 'Title:'
                paper_info['title'] = title_div.text.strip()
            else:
                paper_info['title'] = ""

            authors_div = meta_div.find('div', class_='list-authors')
            if authors_div:
                authors = [a.text.strip() for a in authors_div.find_all('a')]
                paper_info['authors'] = authors
            else:
                paper_info['authors'] = []

            comments_div = meta_div.find('div', class_='list-comments')
            if comments_div:
                comments_span = comments_div.find('span', class_='descriptor')
                if comments_span:
                    comments_span.extract()
                paper_info['comments'] = comments_div.text.strip()
            else:
                paper_info['comments'] = ""

            subjects_div = meta_div.find('div', class_='list-subjects')
            if subjects_div:
                subjects_span = subjects_div.find('span', class_='descriptor')
                if subjects_span:
                    subjects_span.extract()
                paper_info['subjects'] = subjects_div.text.strip()
            else:
                paper_info['subjects'] = ""

            abstract_p = dd.find('p', class_='mathjax')
            if abstract_p:
                paper_info['abstract'] = abstract_p.text.strip().replace('\n', ' ')
            else:
                paper_info['abstract'] = ""
        else:
            # Fallback if meta_div is not found
            paper_info['title'] = ""
            paper_info['authors'] = []
            paper_info['comments'] = ""
            paper_info['subjects'] = ""
            paper_info['abstract'] = ""
        paper_info['gemini2.5flash'] = ""
        paper_info['overall_idea'] = ""
        papers.append(paper_info)
            
    return papers

def update_data_json(date,base_dir="public/data"):
    """
    更新 base_dir/data.json，采用嵌套结构：{ "2025": { "07": [18, ...] } }
    参数 date: "YYYY-MM-DD" 字符串
    """
    import json

    year, month, day = date.split('-')
    day = int(day)
    try:
        with open(os.path.join(base_dir, "data.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if year not in data:
        data[year] = {}
    if month not in data[year]:
        data[year][month] = []
    if day not in data[year][month]:
        data[year][month].append(day)
        data[year][month].sort()
    else:
        # 已存在该日期
        print(f"Data for {date} already exists, skipping update.")
        return

    class CompactList(list):
        pass

    def compact_list_repr(obj, indent_level=0):
        """自定义列表序列化为一行"""
        if isinstance(obj, dict):
            items = []
            for k, v in obj.items():
                items.append(' ' * (indent_level + 2) + json.dumps(k, ensure_ascii=False) + ': ' + compact_list_repr(v, indent_level + 2))
            return '{\n' + ',\n'.join(items) + '\n' + ' ' * indent_level + '}'
        elif isinstance(obj, list):
            return '[' + ', '.join(str(x) for x in obj) + ']'
        else:
            return json.dumps(obj, ensure_ascii=False)

    # 将所有月的列表转为 CompactList
    for y in data:
        for m in data[y]:
            data[y][m] = CompactList(data[y][m])

    with open(os.path.join(base_dir, "data.json"), "w", encoding="utf-8") as f:
        f.write(compact_list_repr(data))
    logger.info(f"Updated data.json with date {date}.")

def main():
    parser = argparse.ArgumentParser(description="Fetch papers from arXiv.")
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument("--date", type=str, default=today_str, help="The date to fetch papers from (YYYY-MM-DD).")
    parser.add_argument("--base_dir", type=str, default="public/data", help="Base directory to save arxiv json files.")
    args = parser.parse_args()
    categories = ["cs.CV", "cs.AI", "cs.LG"]
    year = args.date[:4]
    month = args.date[5:7]
    base_dir = os.path.join(args.base_dir, year, month)
    os.makedirs(base_dir, exist_ok=True)
    for category in categories:
        file_name = f"{base_dir}/{args.date}_{category}.json"
        if os.path.exists(file_name):
            logger.info(f"{file_name} 已存在, 跳过下载。")
            continue
        papers = get_papers_from_arxiv(category=category, date=args.date)

        # 当一个类别没有论文时，其余两个类被也不会有论文。就不用创建新文件，也不用更新日期。
        if len(papers) == 0:
            logger.info(f"No papers found for category on {args.date}. Skipping.")
            return
        for paper in papers:
            paper["date"] = args.date
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False, indent=4)
        logger.info(f"Category {category}: Found {len(papers)} papers, saved to {file_name}.")
    update_data_json(args.date,args.base_dir)
    
 
if __name__ == "__main__":
    main()