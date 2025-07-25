<template>
  <div class="paper-card">
    <!-- Title and Links Row -->
    <el-row :gutter="0" class="paper-title-row">
      <el-col :span="18" class="paper-title-col">
        <span class="paper-number">{{ index + 1 }}.</span>
        <span class="paper-title" v-html="highlightText(paper.title, titleKeywords)"></span>
      </el-col>
      <el-col :span="6" class="paper-links-col">
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
      </el-col>
    </el-row>

    <!-- Authors Row -->
    <el-row class="paper-authors-row">
      <el-col :span="24" class="paper-authors">
        <span>{{ formatAuthorsDisplay(paper.authors) }}</span>
      </el-col>
    </el-row>

    <!-- Abstract, Gemini2.5flash and Overall_Idea tabs section -->
    <el-row v-if="paper.abstract || (paper['gemini2.5flash'] && paper['gemini2.5flash'].trim()) || (paper['Overall_Idea'] && paper['Overall_Idea'].trim())" class="paper-content-row">
      <el-col :span="24" class="paper-section">
        <!-- Tab headers -->
        <div class="tab-headers">
          <button 
            v-if="paper.abstract"
            :class="['tab-button', { 'active': activeTab === 'abstract' }]"
            @click="setActiveTab('abstract')"
            @dblclick="toggleAbstract(!isAbstractExpanded)"
          >
            Abstract
          </button>
          <button 
            v-if="paper['gemini2.5flash'] && paper['gemini2.5flash'].trim()"
            :class="['tab-button', { 'active': activeTab === 'gemini' }]"
            @click="setActiveTab('gemini')"
            @dblclick="toggleGemini(!isGeminiExpanded)"
          >
            Gemini2.5flash
          </button>
          <button 
            v-if="paper['Overall_Idea'] && paper['Overall_Idea'].trim()"
            :class="['tab-button', { 'active': activeTab === 'overall' }]"
            @click="setActiveTab('overall')"
            @dblclick="toggleOverall(!isOverallExpanded)"
          >
            Overall_Idea
          </button>
        </div>
        
        <!-- Tab content -->
        <div class="tab-content">
          <!-- Abstract content -->
          <div v-if="activeTab === 'abstract' && paper.abstract" class="tab-panel">
            <div :class="['abstract-container', {'expanded': isAbstractExpanded}]">
              <span class="abstract-text"
                v-html="highlightText(paper.abstract, abstractKeywords)"
              ></span>
              <div class="abstract-buttons">
                <button v-if="!isAbstractExpanded" class="toggle-button more-button" @click="toggleAbstract(true)">更多</button>
                <button v-if="isAbstractExpanded" class="toggle-button collapse-button" @click="toggleAbstract(false)">收起</button>
              </div>
            </div>
          </div>
          
          <!-- Gemini content -->
          <div v-if="activeTab === 'gemini' && paper['gemini2.5flash'] && paper['gemini2.5flash'].trim()" class="tab-panel">
            <div :class="['gemini-container', {'expanded': isGeminiExpanded}]">
              <div class="gemini-text" v-html="renderMarkdown(paper['gemini2.5flash'])"></div>
              <div class="abstract-buttons">
                <button v-if="!isGeminiExpanded" class="toggle-button more-button" @click="toggleGemini(true)">更多</button>
                <button v-if="isGeminiExpanded" class="toggle-button collapse-button" @click="toggleGemini(false)">收起</button>
              </div>
            </div>
          </div>
          
          <!-- Overall_Idea content -->
          <div v-if="activeTab === 'overall' && paper['Overall_Idea'] && paper['Overall_Idea'].trim()" class="tab-panel">
            <div :class="['overall-container', {'expanded': isOverallExpanded}]">
              <div class="overall-text" v-html="renderMarkdown(paper['Overall_Idea'])"></div>
              <div class="abstract-buttons">
                <button v-if="!isOverallExpanded" class="toggle-button more-button" @click="toggleOverall(true)">更多</button>
                <button v-if="isOverallExpanded" class="toggle-button collapse-button" @click="toggleOverall(false)">收起</button>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { renderLatex, renderLatexWithHighlight } from '../utils/latex';
import MarkdownIt from 'markdown-it';
import mdKatex from '@iktakahiro/markdown-it-katex';

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
}).use(mdKatex, {
  throwOnError: false,
  errorColor: '#cc0000'
});

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
    },
    forceExpandAbstract: {
      type: Boolean,
      default: null
    },
    forceExpandGemini: {
      type: Boolean,
      default: null
    },
    forceExpandOverall: {
      type: Boolean,
      default: null
    },
    expandAll: {
      type: Object,
      default: () => ({
        abstract: false,
        gemini: false,
        overall: false
      })
    }
  },
  data() {
    return {
      isAbstractExpanded: false,
      isGeminiExpanded: false,
      isOverallExpanded: false,
      activeTab: 'abstract' // 默认显示Abstract标签
    }
  },
  mounted() {
    // 设置默认活跃标签：优先显示Abstract，如果没有Abstract则显示Gemini，最后是Overall_Idea
    if (this.paper.abstract) {
      this.activeTab = 'abstract';
    } else if (this.paper['gemini2.5flash'] && this.paper['gemini2.5flash'].trim()) {
      this.activeTab = 'gemini';
    } else if (this.paper['Overall_Idea'] && this.paper['Overall_Idea'].trim()) {
      this.activeTab = 'overall';
    }
  },
  watch: {
    forceExpandAbstract(newVal) {
      if (newVal !== null) {
        this.isAbstractExpanded = newVal;
        if (newVal) {
          this.activeTab = 'abstract';
        }
      }
    },
    forceExpandGemini(newVal) {
      if (newVal !== null) {
        this.isGeminiExpanded = newVal;
        if (newVal) {
          this.activeTab = 'gemini';
        }
      }
    },
    forceExpandOverall(newVal) {
      if (newVal !== null) {
        this.isOverallExpanded = newVal;
        if (newVal) {
          this.activeTab = 'overall';
        }
      }
    },
    expandAll: {
      handler(newVal) {
        // 更新展开状态
        this.isAbstractExpanded = newVal.abstract;
        this.isGeminiExpanded = newVal.gemini;
        this.isOverallExpanded = newVal.overall;
        
        // 设置正确的活跃标签
        if (newVal.abstract) {
          this.activeTab = 'abstract';
        } else if (newVal.gemini) {
          this.activeTab = 'gemini';
        } else if (newVal.overall) {
          this.activeTab = 'overall';
        }
      },
      immediate: true, // 确保组件创建时立即执行
      deep: true // 深度监听对象变化
    }
  },
  methods: {
    setActiveTab(tab) {
      this.activeTab = tab;
    },

    toggleAbstract(expand) {
      // 如果双击的是Abstract选项卡，先切换到Abstract，然后展开/收起
      if (this.activeTab !== 'abstract') {
        this.activeTab = 'abstract';
      }
      this.isAbstractExpanded = expand;
    },

    toggleGemini(expand) {
      // 如果双击的是Gemini选项卡，先切换到Gemini，然后展开/收起
      if (this.activeTab !== 'gemini') {
        this.activeTab = 'gemini';
      }
      this.isGeminiExpanded = expand;
    },

    toggleOverall(expand) {
      // 如果双击的是Overall选项卡，先切换到Overall，然后展开/收起
      if (this.activeTab !== 'overall') {
        this.activeTab = 'overall';
      }
      this.isOverallExpanded = expand;
    },

    renderMarkdown(text) {
      if (!text) return '';
      
      try {
        return md.render(text);
      } catch (error) {
        console.error('Markdown parsing error:', error);
        // If parsing fails, return the original text with simple HTML escaping
        return text.replace(/&/g, '&amp;')
                  .replace(/</g, '&lt;')
                  .replace(/>/g, '&gt;')
                  .replace(/"/g, '&quot;')
                  .replace(/'/g, '&#039;')
                  .replace(/\n/g, '<br>');
      }
    },

    formatAuthorsDisplay(authors) {
      if (!authors) return '';

      // 如果是字符串，移除可能存在的引号并用连字符处理长名称
      if (typeof authors === 'string') {
        return authors.replace(/['"]/g, '').replace(/([a-zA-Z]{10,})/g, '$1-');
      }

      // 如果是数组，将其连接成字符串，移除引号，并用连字符处理长名称
      if (Array.isArray(authors)) {
        return authors.map(author => author.replace(/([a-zA-Z]{10,})/g, '$1-')).join('; ').replace(/['"]/g, '');
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
    }
  }
}
</script>

<style>
/* 论文卡片主容器 */
.paper-card {
  margin-bottom: 30px;
  width: 100%;
  background-color: var(--bg-color-tertiary);
  padding: 0;
  box-sizing: border-box;
}

/* 标题行样式 */
.paper-title-row {
  margin-bottom: 8px;
  padding: 0;
  margin-left: 0;
  margin-right: 0;
  width: 100%;
  box-sizing: border-box;
}

.paper-title-col {
  padding: 10px var(--content-padding, 0);
}

.paper-links-col {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  padding: 10px var(--content-padding, 0);
}

/* 作者行样式 */
.paper-authors-row {
  margin-bottom: 8px;
}

.paper-authors {
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  line-height: 1.5;
  padding: 8px var(--content-padding, 0);
  font-family: var(--font-family-sans);
  font-style: normal;
  letter-spacing: 0.01em;
  white-space: normal; /* Allow wrapping */
  word-break: break-word; /* Break long words */
  hyphens: auto; /* Add hyphens when breaking words */
  -webkit-hyphens: auto;
  -ms-hyphens: auto;
}

/* 内容区域样式 */
.paper-section {
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  line-height: 1.8;
  padding: 8px var(--content-padding, 0);
}

/* 标题和链接样式 */
.paper-number {
  font-weight: var(--font-weight-bold);
  margin-right: 8px;
  font-size: var(--font-size-large);
  padding: 0;
}

.paper-title {
  font-size: var(--font-size-large);
  color: var(--text-color-primary);
  font-weight: var(--font-weight-bold);
  padding: 0;
  font-family: var(--font-family-serif);
  line-height: 1.4;
  letter-spacing: 0.01em;
}

.paper-links {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
}

.paper-link {
  color: var(--link-color);
  text-decoration: none;
  font-size: calc(var(--font-size-medium) - 2px);
  padding: 3px 8px;
  border-radius: var(--form-element-border-radius);
  white-space: nowrap;
}

.paper-conference {
  color: var(--highlight-color);
  font-size: calc(var(--font-size-medium) - 2px);
  padding: 3px 8px;
  border-radius: var(--form-element-border-radius);
  white-space: nowrap;
}

/* 标签页样式 */
.tab-headers {
  display: flex;
  margin-bottom: 12px;
  gap: 16px;
}

.tab-button {
  background: none;
  border: none;
  padding: 6px 0;
  font-size: calc(var(--font-size-small) - 1px);
  color: var(--text-color-secondary);
  cursor: pointer;
  transition: color 0.2s ease;
  font-family: inherit;
  font-weight: inherit;
}

.tab-button:hover {
  color: var(--text-color-primary);
}

.tab-button.active {
  color: var(--highlight-color);
}

.tab-content {
  min-height: 100px;
}

.tab-panel {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Abstract, Gemini and Overall容器样式 */
.abstract-container, .gemini-container, .overall-container {
  position: relative;
  color: var(--text-color-primary);
  font-size: calc(var(--font-size-small) - 1px);
  line-height: 1.8;
  text-align: justify;
  word-break: break-word;
  hyphens: auto;
  -webkit-hyphens: auto;
  -ms-hyphens: auto;
  font-family: var(--font-family-serif);
  letter-spacing: 0.01em;
}

.abstract-container:not(.expanded) .abstract-text,
.gemini-container:not(.expanded) .gemini-text,
.overall-container:not(.expanded) .overall-text {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  max-height: calc(1.8em * 3);
}

/* 按钮样式 */
.abstract-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 2px;
}

.toggle-button {
  color: var(--link-color);
  border: none;
  background: transparent;
  padding: 2px 8px;
  font-size: var(--font-size-small);
  font-family: inherit;
  font-weight: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-button:hover {
  text-decoration: underline;
}

/* 高亮样式 */
.highlight {
  background-color: rgba(233, 185, 110, 0.3);
  padding: 0 3px;
  border-radius: 4px;
}

/* LaTeX公式样式 */
.katex {
  font-size: 1.1em !important;
  line-height: 1.2 !important;
}

.katex-display {
  margin: 1em 0 !important;
  overflow-x: auto;
}

/* Markdown样式 */
.gemini-text h1, .gemini-text h2, .gemini-text h3,
.overall-text h1, .overall-text h2, .overall-text h3 {
  margin: 0.5em 0;
  font-weight: var(--font-weight-bold);
}

.gemini-text p, .overall-text p {
  margin: 0.5em 0;
}

.gemini-text ul, .gemini-text ol,
.overall-text ul, .overall-text ol {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.gemini-text code, .overall-text code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.1em 0.3em;
  border-radius: 3px;
  font-family: var(--font-family-mono);
  font-size: calc(var(--font-size-small) - 2px);
}

.gemini-text pre, .overall-text pre {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 1em;
  border-radius: 5px;
  overflow-x: auto;
  margin: 0.5em 0;
}

.gemini-text blockquote, .overall-text blockquote {
  border-left: 3px solid var(--highlight-color);
  padding-left: 1em;
  margin: 0.5em 0;
  font-style: italic;
}
</style>
