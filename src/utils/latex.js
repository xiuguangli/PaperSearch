import katex from 'katex';

/**
 * 渲染LaTeX公式
 * @param {string} text 包含LaTeX公式的文本
 * @param {boolean} displayMode 是否使用显示模式（默认为false，即行内模式）
 * @returns {string} 渲染后的HTML
 */
export function renderLatex(text, displayMode = false) {
  if (!text) return '';
  
  // 匹配所有LaTeX公式
  // 支持 $...$ 和 $$...$$ 格式
  const inlineRegex = /\$([^\$]+)\$/g;
  const displayRegex = /\$\$([^\$]+)\$\$/g;
  
  // 先处理显示模式的公式 ($$...$$)
  let result = text.replace(displayRegex, (match, formula) => {
    try {
      return katex.renderToString(formula, {
        displayMode: true,
        throwOnError: false
      });
    } catch (error) {
      console.error('LaTeX渲染错误 (显示模式):', error);
      return match; // 如果渲染失败，返回原始文本
    }
  });
  
  // 再处理行内模式的公式 ($...$)
  result = result.replace(inlineRegex, (match, formula) => {
    try {
      return katex.renderToString(formula, {
        displayMode: false,
        throwOnError: false
      });
    } catch (error) {
      console.error('LaTeX渲染错误 (行内模式):', error);
      return match; // 如果渲染失败，返回原始文本
    }
  });
  
  return result;
}

/**
 * 渲染包含LaTeX公式的文本，同时保留高亮功能
 * @param {string} text 原始文本
 * @param {Array} keywords 需要高亮的关键词
 * @returns {string} 渲染后的HTML
 */
export function renderLatexWithHighlight(text, keywords) {
  if (!text) return '';
  
  // 如果没有关键词，直接渲染LaTeX
  if (!keywords || keywords.length === 0) {
    return renderLatex(text);
  }
  
  // 存储LaTeX公式，以便在高亮后恢复
  const latexPlaceholders = [];
  const inlineRegex = /\$([^\$]+)\$/g;
  const displayRegex = /\$\$([^\$]+)\$\$/g;
  
  // 替换所有LaTeX公式为占位符
  let processedText = text.replace(displayRegex, (match, formula) => {
    const placeholder = `__LATEX_DISPLAY_${latexPlaceholders.length}__`;
    latexPlaceholders.push({
      placeholder,
      original: match,
      formula,
      displayMode: true
    });
    return placeholder;
  });
  
  processedText = processedText.replace(inlineRegex, (match, formula) => {
    const placeholder = `__LATEX_INLINE_${latexPlaceholders.length}__`;
    latexPlaceholders.push({
      placeholder,
      original: match,
      formula,
      displayMode: false
    });
    return placeholder;
  });
  
  // 转义HTML特殊字符
  const escapeHtml = (text) => {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  };
  
  // 对文本进行HTML转义
  processedText = escapeHtml(processedText);
  
  // 高亮关键词
  for (const keyword of keywords) {
    if (keyword.trim() === '') continue;
    
    try {
      // 转义正则表达式中的特殊字符
      const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`(${escapedKeyword})`, 'gi');
      processedText = processedText.replace(regex, '<span class="highlight">$1</span>');
    } catch (e) {
      console.error('高亮关键词错误:', e);
    }
  }
  
  // 恢复LaTeX公式
  for (const item of latexPlaceholders) {
    try {
      const rendered = katex.renderToString(item.formula, {
        displayMode: item.displayMode,
        throwOnError: false
      });
      processedText = processedText.replace(item.placeholder, rendered);
    } catch (error) {
      console.error(`LaTeX渲染错误 (${item.displayMode ? '显示' : '行内'}模式):`, error);
      processedText = processedText.replace(item.placeholder, escapeHtml(item.original));
    }
  }
  
  return processedText;
}
