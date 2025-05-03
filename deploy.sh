#!/usr/bin/env bash

# 部署脚本 - 用于将应用部署到GitHub Pages
# 使用方法: ./deploy.sh

# 确保脚本抛出遇到的错误
set -e

echo "===== 开始部署到GitHub Pages ====="

# 清理dist目录
echo "清理dist目录..."
rm -rf dist

# 构建生产版本
echo "构建生产版本..."
npm run build

# 进入生成的文件夹
cd dist

# 如果是发布到自定义域名
# echo 'www.example.com' > CNAME

echo "初始化Git仓库并提交文件..."
git init
git add -A
git commit -m 'deploy to GitHub Pages'

# 推送到GitHub Pages分支
echo "推送到GitHub Pages分支..."
git push -f https://github.com/xiuguangli/PaperSearch.git master:gh-pages

cd -

echo "===== 部署完成! ====="
echo "网站已部署到: https://xiuguangli.github.io/PaperSearch/"
