# 将A文件的内容复制到B文件


import json
import os



def modify(file="CVPR.2025"):
    confrence = file.split('.')[0]
    year = file.split('.')[1]
    src_dir = "public/data0"
    des_dir = "public/data"
    
    src_file = os.path.join(src_dir, f"{confrence}.{year}.json")
    des_file = os.path.join(des_dir, f"{confrence}.{year}.json")
    
    if not os.path.exists(src_file):
        print(f"Source file {src_file} does not exist.")
        return
    if not os.path.exists(des_file):
        print(f"Destination file {des_file} does not exist.")
        return
    with open(src_file, 'r', encoding='utf-8') as f:
        papers_src = json.load(f)
    papers_src = papers_src.get('papers', [])
    if not papers_src:
        print(f"No papers found in {src_file}.")
        return
    
    with open(des_file, 'r', encoding='utf-8') as f:
        papers_des = json.load(f)
    count = 0
    for p_des in papers_des:
        for p_src in papers_src:
            if p_des['title'] == p_src['title']:
                p_des["gemini2.5flash"] = p_src["gemini2.5flash"]
                p_des["overall_idea"] = p_src["overall_idea"]
                # p_des["pdf_url"] = p_src["pdf_url"]
                # p_des["overall_idea"] = p_src["Overall_Idea"]
                count += 1
    print(f"Modified {file} -> {count}/{len(papers_des)} papers.")

    with open(des_file, 'w', encoding='utf-8') as f:
        json.dump(papers_des, f, ensure_ascii=False, indent=4)
    print("Finished")

if __name__ == "__main__":
    modify("NeurIPS.2024")

