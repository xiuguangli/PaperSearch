import os
import json


def main(field='Overall_Idea'):
    base_dir = "/home/lxg/work/Papers/PaperSearch/public/data"
    json_files = [os.path.join(base_dir, f) for f in os.listdir(base_dir) if f.endswith('.json')]
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"processing {json_file}")
        papers = data.get('papers')
        for paper in papers:
            paper[field] = ''
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    field = 'Overall_Idea'
    main(field)