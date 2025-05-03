#!/usr/bin/env bash

# 构建脚本 - 用于构建生产版本但不部署
# 使用方法: ./build.sh

# 确保脚本抛出遇到的错误
set -e

echo "===== 开始构建生产版本 ====="

# 清理dist目录
echo "清理dist目录..."
rm -rf dist

# 构建生产版本
echo "构建生产版本..."
npm run build

echo "===== 构建完成! ====="
echo "生产版本已构建到dist目录"
echo "您可以使用 'npm run preview' 命令在本地预览生产版本"
