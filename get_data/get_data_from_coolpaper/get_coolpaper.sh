Conferences=(
  "AAAI"
  "ACL"
  "COLM"
  "COLT"
  "CoRL"
  "CVPR"
  "ECCV"
  "EMNLP"
  "ICCV"
  "ICLR"
  "ICML"
  "IJCAI"
  "INTERSPEECH"
  "IWSLT"
  "MLSYS"
  "NAACL"
  "NDSS"
  "NeurIPS"
  "OSDI"
  "UAI"
  "USENIX-Fast"
  "USENIX-Sec"
)

years=("2022" "2023" "2024" "2025")

for conf in "${Conferences[@]}"; do
  for y in "${years[@]}"; do
    echo "正在处理 $conf $y 的数据..."
    python get_data_from_coolpaper.py --file "${conf}.${y}"
  done
done