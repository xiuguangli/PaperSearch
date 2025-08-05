#!/usr/bin/env bash
# run_all.sh

conferences=(
  AAAI ACL COLM COLT CoRL CVPR ECCV EMNLP ICCV ICLR ICML IJCAI
  INTERSPEECH IWSLT MLSYS NAACL NDSS NeurIPS OSDI UAI USENIX-Fast USENIX-Sec
)

years=(2023 2024 2025)
update_fields=(gemini overall)

for conf in "${conferences[@]}"; do
  for year in "${years[@]}"; do
    file="${conf}.${year}"
    for field in "${update_fields[@]}"; do
      echo "===== 更新 ${conf}.${year}.json 的 ${field} 字段 ====="
      python get_data/get_gemini_overview/get_overview.py \
        --file "$file" \
        --update "$field"
    done
  done
done