# 确保脚本抛出遇到的错误
set -e

# 获取提交信息，如果没有提供则使用默认信息
COMMIT_MSG=${1:-"更新代码和部署"}

echo "提交代码到main分支..."
git add .
git commit -m "$COMMIT_MSG"
git push -f origin main
echo "===== 代码已上传到main分支 ====="