import json
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime
from urllib.parse import urljoin
import argparse

def main():
    parser = argparse.ArgumentParser(description="CVPR 2025 Paper Scraper")
    parser.add_argument("--year", type=int, default=2025, help="Year of the conference")
    parser.add_argument("--name", type=str, default="CVPR", help="Name of the conference")
    args = parser.parse_args()

    prefix = "https://openaccess.thecvf.com/"
    url = urljoin(prefix, f"{args.name}{args.year}?day=all")
    response = requests.get(url)
    # html_file = f"{args.name.lower()}{args.year}.html"
    # with open(html_file, "w") as f:
    #     f.write(response.text)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}")
        return
    soup = BeautifulSoup(response.content, "html.parser")
    urls = []
    for dt in soup.find_all('dt', class_='ptitle'):
        a = dt.find('a')
        urls.append(urljoin(prefix, a.get('href')))
        break
    
    for url in urls:
        get_paper_info(url)
    print(f"Found {len(urls)} papers.")

def get_paper_info(url):
    print(url)
    name_and_year = url.split("/papers/")[-8]
    name,year = name_and_year[:4], name_and_year[4:8]
    print(name, year)
    data = {
        "conference": name,
        "year": year,
        
    }
    response = requests.get(url)
    with open(f"1.html", "w") as f:
        f.write(response.text)
    
    

if __name__ == "__main__":
    main()

    