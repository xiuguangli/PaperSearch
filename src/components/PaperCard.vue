<template>
  <table class="paper-card">
    <tbody>
      <tr>
        <td class="paper-title-cell">
          <span class="paper-number">{{ index + 1 }}.</span>
          <span class="paper-title" v-html="highlightText(paper.title, titleKeywords)"></span>
        </td>
        <td class="paper-links-cell">
          <div class="paper-links">
            <a
              v-if="paper.pdf_url"
              :href="paper.pdf_url"
              target="_blank"
              class="paper-link"
              title="View PDF"
              rel="noopener"
            >
              PDF
            </a>
            <a
              v-if="paper.original_url"
              :href="paper.original_url"
              target="_blank"
              class="paper-link"
              title="View HTML"
            >
              HTML
            </a>
            <span class="paper-conference">
              {{ paper.conference }}{{ paper.year }}
            </span>
          </div>
        </td>
      </tr>
      <tr class="compact-row">
        <td colspan="2" class="paper-authors">
          <!-- <span class="author-label">Authors: </span> -->
          <span>{{ formatAuthorsDisplay(paper.authors) }}</span>
        </td>
      </tr>
      <tr class="compact-row">
        <td colspan="2" class="paper-abstract">
          <div class="abstract-content">
            <!-- <span class="abstract-label">Abstract: </span> -->
            <div :class="['abstract-container', {'expanded': isExpanded}]">
              <span class="abstract-text"
                v-html="highlightText(paper.abstract, abstractKeywords)"
              ></span>
              <div class="abstract-buttons">
                <button v-if="!isExpanded" class="toggle-button more-button" @click="toggleAbstract(true)">更多</button>
                <button v-if="isExpanded" class="toggle-button collapse-button" @click="toggleAbstract(false)">收起</button>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import { renderLatex, renderLatexWithHighlight } from '../utils/latex';

export default {
  name: 'PaperCard',
  props: {
    paper: {
      type: Object,
      required: true
    },
    index: {
      type: Number,
      required: true
    },
    titleKeywords: {
      type: Array,
      default: () => []
    },
    abstractKeywords: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      isExpanded: false
    }
  },
  methods: {
    toggleAbstract(expand) {
      this.isExpanded = expand;
    },

    formatAuthorsDisplay(authors) {
      if (!authors) return '';

      // 如果是字符串，移除可能存在的引号
      if (typeof authors === 'string') {
        return authors.replace(/['"]/g, '');
      }

      // 如果是数组，将其连接成字符串，并移除引号
      if (Array.isArray(authors)) {
        return authors.join(', ').replace(/['"]/g, '');
      }

      return authors;
    },
    // 高亮显示文本中的关键词，并渲染LaTeX公式
    highlightText(text, keywords) {
      if (!text) return '';

      // 如果没有关键词，只渲染LaTeX
      if (!keywords || keywords.length === 0) {
        return renderLatex(text);
      }

      // 同时处理高亮和LaTeX渲染
      return renderLatexWithHighlight(text, keywords);
    },
    // 转义HTML特殊字符
    escapeHtml(text) {
      const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
      };
      return text.replace(/[&<>"']/g, m => map[m]);
    }
  }
}
</script>

<style>
/* 全局样式，防止表格边框显示轮廓线 */
:root {
  --outline-fix: 0 !important;
  --bg-color-tertiary-rgb: 245, 245, 245; /* 背景色的RGB值 */
  --highlight-color-rgb: 230, 145, 56; /* 高亮色的RGB值，用于按钮悬停效果 */
}

/* 全局样式覆盖，确保所有表格元素不显示轮廓线 */
*:focus {
  outline: none !important;
}

/* 特别针对表格元素的样式 */
table {
  border-collapse: collapse !important;
  border-spacing: 0 !important;
}

table, tbody, tr, td, th {
  border: none !important;
  outline: none !important;
  -webkit-tap-highlight-color: transparent !important;
}

.paper-card {
  margin-bottom: 30px; /* 增加论文之间的间距 */
  width: 100%;
  max-width: 100%;
  table-layout: fixed; /* 固定表格布局 */
  border-collapse: collapse;
  border: none;
  background-color: var(--bg-color-tertiary);
  outline: var(--outline-fix);
  outline-width: var(--outline-fix);
  outline-style: none !important;
  outline-color: transparent !important;
  overflow-x: hidden; /* 防止内容溢出 */
}

.paper-card:focus,
.paper-card:active,
.paper-card:hover {
  outline: var(--outline-fix);
  outline-width: var(--outline-fix);
  outline-style: none !important;
  outline-color: transparent !important;
  border: none !important;
}

.paper-card td:focus,
.paper-card td:active,
.paper-card td:hover {
  outline: var(--outline-fix);
  outline-width: var(--outline-fix);
  outline-style: none !important;
  outline-color: transparent !important;
  border: none !important;
}

.paper-card td {
  padding: 6px var(--spacing-medium);
  border: none !important;
  background-color: var(--bg-color-tertiary);
  outline: var(--outline-fix);
  outline-width: var(--outline-fix);
  outline-style: none !important;
  outline-color: transparent !important;
}

/* 防止表格边框在点击时出现轮廓线 */
table, tr, td, th {
  outline: var(--outline-fix);
  outline-width: var(--outline-fix);
  outline-style: none !important;
  outline-color: transparent !important;
  border-style: none !important;
  -webkit-box-shadow: none !important;
  box-shadow: none !important;
}

table:focus, tr:focus, td:focus, th:focus,
table:active, tr:active, td:active, th:active,
table:hover, tr:hover, td:hover, th:hover {
  outline: var(--outline-fix);
  outline-width: var(--outline-fix);
  outline-style: none !important;
  outline-color: transparent !important;
  border-style: none !important;
  -webkit-box-shadow: none !important;
  box-shadow: none !important;
}

/* 移除通用的compact-row样式，改为更具体的选择器 */
/* .paper-card .compact-row td {
  padding-top: 1px;
  padding-bottom: 1px;
} */

.paper-title-cell {
  width: 75%;
  vertical-align: top;
  padding-right: 10px;
  padding-bottom: 10px !important; /* 适中的底部内边距 */
  padding-top: 10px !important; /* 适中的上方内边距 */
  border-bottom: none !important; /* 移除边框 */
}

.paper-links-cell {
  width: 25%;
  text-align: right;
  vertical-align: top;
  white-space: nowrap;
  padding-bottom: 10px !important; /* 适中的底部内边距 */
  padding-top: 10px !important; /* 适中的上方内边距 */
  border-bottom: none !important; /* 移除边框 */
}

.paper-number {
  font-weight: var(--font-weight-bold);
  margin-right: 8px;
  font-size: var(--font-size-large);
  display: inline;
}

.paper-title {
  font-size: var(--font-size-large);
  color: var(--text-color-primary);
  font-weight: var(--font-weight-bold);
  display: inline;
}

.paper-links {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-wrap: nowrap;
}

.paper-link {
  margin-right: var(--spacing-small);
  color: var(--link-color);
  text-decoration: none;
  font-size: var(--font-size-medium);
  font-weight: var(--font-weight-medium);
  padding: 4px 10px;
  border-radius: var(--form-element-border-radius);
  background-color: var(--bg-color-tertiary);
  white-space: nowrap;
}

.paper-conference {
  color: var(--highlight-color);
  font-size: var(--font-size-medium);
  font-weight: var(--font-weight-medium);
  padding: 4px 10px;
  border-radius: var(--form-element-border-radius);
  background-color: var(--bg-color-tertiary);
  white-space: nowrap;
}

.paper-card td.paper-authors {
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  line-height: 1.5; /* 行高 */
  background-color: var(--bg-color-tertiary);
  padding-top: 8px !important; /* 适中的上方内边距 */
  padding-bottom: 8px !important; /* 适中的下方内边距 */
  margin-bottom: 0; /* 移除外边距 */
  border-top: none !important; /* 移除边框 */
  border-bottom: none !important; /* 移除边框 */
}

.author-label {
  font-weight: var(--font-weight-bold);
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  margin-right: var(--spacing-small);
}

.paper-card td.paper-abstract {
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  line-height: 1.8; /* 行高 */
  background-color: var(--bg-color-tertiary);
  text-align: justify;
  vertical-align: top;
  padding-top: 8px !important; /* 适中的上方内边距 */
  padding-bottom: 12px !important; /* 下方内边距 */
  margin-top: 0; /* 移除外边距 */
}

.abstract-content {
  display: flex;
  align-items: baseline; /* 使文本基线对齐 */
}

.abstract-label {
  font-weight: var(--font-weight-bold);
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  margin-right: 5px;
  white-space: nowrap;
  flex-shrink: 0; /* 防止标签被压缩 */
}

.abstract-container {
  position: relative;
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  line-height: 1.8; /* 行高 */
  letter-spacing: 0.3px; /* 字间距 */
  text-align: justify;
  word-break: break-word;
  hyphens: auto;
  flex-grow: 1; /* 占用剩余空间 */
}

/* 非展开状态下的摘要容器 */
.abstract-container:not(.expanded) .abstract-text {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3; /* 限制为3行 */
  line-clamp: 3; /* 标准属性 */
  -webkit-box-orient: vertical;
  max-height: calc(1.8em * 3); /* 3行的最大高度 */
}

.abstract-container.expanded {
  display: block;
}

/* 按钮容器 */
.abstract-buttons {
  display: flex;
  justify-content: flex-end; /* 靠右对齐 */
  margin-top: 2px; /* 更小的上边距 */
  padding-right: 2px; /* 右侧微调 */
}

.abstract-text {
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  line-height: 1.8; /* 行高 */
  letter-spacing: 0.3px; /* 字间距 */
  text-align: justify;
  word-break: break-word;
  hyphens: auto;
  white-space: normal;
  display: inline; /* 确保文本内联显示 */
}

/* 通用按钮样式 */
.toggle-button {
  color: var(--link-color);
  border: none;
  background-color: transparent;
  padding: 2px 8px;
  font-size: var(--font-size-small); /* 使用与页面一致的字体大小变量 */
  font-family: inherit; /* 继承父元素的字体 */
  cursor: pointer;
  font-weight: var(--font-weight-regular); /* 使用常规字重 */
  transition: all 0.2s;
  line-height: 1.5;
  text-align: right;
}

.toggle-button:hover {
  text-decoration: underline; /* 悬停时添加下划线 */
}

/* 特定按钮样式 */
.more-button, .collapse-button {
  color: var(--link-color); /* 使用与页面链接一致的颜色 */
}

.highlight {
  background-color: rgba(233, 185, 110, 0.3);
  font-weight: normal;
  color: inherit;
  padding: 0 3px;
  border-radius: 4px;
  display: inline-block;
  position: relative;
  line-height: 1.2;
  font-size: inherit;
}

/* LaTeX公式样式 */
.katex {
  font-size: 1.1em !important;
  line-height: 1.2 !important;
}

.katex-display {
  margin: 1em 0 !important;
  overflow-x: auto;
  overflow-y: hidden;
  padding-top: 0.5em;
  padding-bottom: 0.5em;
}

/* 确保公式在小屏幕上可以滚动查看 */
.katex-display > .katex {
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}

/* 修复行内公式与文本的对齐问题 */
.katex-inline {
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
}
</style>
