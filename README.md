# PaperSearch

PaperSearch是一个用于浏览和搜索学术论文的Web应用程序。它允许用户按会议和年份筛选论文，并提供标题和摘要搜索功能。

## 功能

- 按会议和年份筛选论文
- 搜索论文标题和摘要
- 显示论文详细信息，包括作者、摘要等
- 提供PDF和HTML链接
- 支持排序和分页

## 开发指南

### 本地开发

1. 克隆仓库：

```bash
git clone https://github.com/xiuguangli/PaperSearch.git
cd PaperSearch
```

2. 安装依赖：

```bash
npm install
```

3. 启动开发服务器：

```bash
npm run dev
# 或者
./dev.sh
```

开发服务器将在 http://localhost:5173/ 启动（或者其他可用端口）。

### 构建生产版本（不部署）

如果您想构建生产版本但不部署到GitHub Pages，可以使用以下命令：

```bash
npm run build:prod
# 或者
./build.sh
```

构建完成后，生产版本将位于`dist`目录中。您可以使用以下命令在本地预览生产版本：

```bash
npm run preview
```

### 部署到GitHub Pages

当您准备好部署到GitHub Pages时，可以使用以下命令：

```bash
npm run deploy
# 或者
./deploy.sh
```

这将构建生产版本并将其部署到GitHub Pages。部署完成后，您可以在 https://xiuguangli.github.io/PaperSearch/ 访问应用程序。

## 工作流程建议

1. 使用`npm run dev`进行本地开发和测试
2. 使用`npm run build:prod`构建生产版本并在本地预览
3. 确认一切正常后，使用`npm run deploy`部署到GitHub Pages

这种工作流程可以确保您在部署到GitHub Pages之前，在本地充分测试您的更改。

## 技术栈

- Vue 3
- Element Plus
- Vite
