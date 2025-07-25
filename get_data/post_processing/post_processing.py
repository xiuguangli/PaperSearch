import json


def main():
    json_file = '/home/lxg/work/Papers/PaperSearch/public/data/ICML.2025.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    papers = data['papers']
    new_papers = []
    for paper in papers:
        if paper["status"] != "Reject":
            new_papers.append(paper)

    for idx, paper in enumerate(new_papers):
        paper["order"] = idx + 1

    data['papers'] = new_papers
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()