<template>
  <div id="app">
    <header class="app-header">
      <div class="header-container">
        <div class="logo-container" @click="goHome">
          <h1 class="app-title">PaperSearch</h1>
        </div>
        <div class="nav-container">
          <router-link to="/papers" class="nav-link" :class="{ 'active-link': $route.path === '/papers' }">
            <span>论文列表</span>
          </router-link>
          <router-link to="/advanced-search" class="nav-link" :class="{ 'active-link': $route.path === '/advanced-search' }">
            <span>高级搜索</span>
          </router-link>
          <router-link to="/stats" class="nav-link" :class="{ 'active-link': $route.path === '/stats' }">
            <span>数据统计</span>
          </router-link>
        </div>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p class="copyright">&copy; {{ new Date().getFullYear() }} PaperSearch</p>
    </footer>
  </div>
</template>

<script>
import { Document, Search, Collection, HomeFilled } from '@element-plus/icons-vue';

export default {
  name: 'App',
  components: {
    Document,
    Search,
    Collection,
    HomeFilled
  },
  methods: {
    goHome() {
      this.$router.push('/papers');
    }
  }
};
</script>

<style>
:root {
  /* Layout variables */
  --content-width: 80%;
  --content-max-width: 1200px;

  /* Font variables */
  --font-family-serif: Georgia, serif;

  /* Font size variables */
  --font-size-small: 18px;
  --font-size-medium: 20px;
  --font-size-large: 22px;
  --font-size-xlarge: 26px;
  --font-size-xxlarge: 30px;

  /* Font weight variables */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 600;

  /* Color variables - Warm Reading Mode */
  --bg-color-primary: #f8f5f1;
  --bg-color-secondary: #f3efe9;
  --bg-color-tertiary: #fffaf3;
  --text-color-primary: #5c4b3c;
  --text-color-regular: #7a6a5b;
  --text-color-secondary: #9c8c7d;
  --border-color: #e8e0d5;
  --highlight-color: #d2a76a;
  --link-color: #a06e3b;
  --shadow-color: rgba(92, 75, 60, 0.1);

  /* Form element variables */
  --form-element-height: 40px;
  --form-element-border-radius: 6px;
  --form-element-padding: 0 15px;

  /* Spacing variables */
  --spacing-small: 10px;
  --spacing-medium: 20px;
  --spacing-large: 30px;
}

/* 设置全局背景色 */
html, body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-color-tertiary);
  font-family: var(--font-family-serif);
}

/* Apply serif font to all Element Plus components */
.el-message-box,
.el-dialog,
.el-dropdown-menu,
.el-select-dropdown,
.el-tooltip__popper,
.el-popover,
.el-menu,
.el-table {
  font-family: var(--font-family-serif) !important;
}

#app {
  font-family: var(--font-family-serif);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: var(--font-size-medium);
  background-color: var(--bg-color-tertiary);
  color: var(--text-color-primary);
}

.app-header {
  padding: 10px 0;
  background-color: #f5f1e8;
  border-bottom: 1px solid #e8e0d5;
  width: 100%;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 15px;
  box-sizing: border-box;
}

.logo-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0;
  height: 40px;
  flex-shrink: 0;
}

.logo-icon-container {
  margin-right: 10px;
  background-color: #f5f1e8;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  border: 1px solid #6d5c4d;
  box-sizing: border-box;
  padding: 0;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 30px;
  color: #6d5c4d;
}

.app-title {
  margin: 0;
  margin-left: 35%;
  font-size: 1.125rem;
  color: #6d5c4d;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.nav-container {
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  flex-wrap: nowrap;
  margin-right: 3.7%;
}

.nav-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--text-color-primary);
  padding: 4px 10px;
  transition: all 0.3s;
  font-size: 1.125rem;
  margin-left: 8px;
  white-space: nowrap;
}

.nav-link:hover {
  color: var(--highlight-color) !important;
}

.active-link {
  color: var(--highlight-color) !important;
  font-weight: bold;
}

.nav-icon {
  margin-right: 5px;
}

.app-main {
  padding: var(--spacing-medium) var(--spacing-large);
  min-height: calc(100vh - 80px);
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin: 0 auto;
  background-color: var(--bg-color-tertiary);
  margin-top: 5px;
  margin-bottom: var(--spacing-small);
  box-sizing: border-box;
}

.app-footer {
  text-align: center;
  padding: var(--spacing-medium);
  background-color: var(--bg-color-tertiary);
  border-top: 1px solid var(--border-color);
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin: 0 auto;
  box-sizing: border-box;
}

.copyright {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: var(--font-size-small);
}

/* Global Element Plus component styles for consistent heights and warm theme */
.el-input__wrapper,
.el-select .el-input__wrapper,
.el-button,
.el-radio-group,
.el-radio-button,
.el-pagination-editor {
  font-family: var(--font-family-serif) !important;
  height: var(--form-element-height) !important;
  line-height: var(--form-element-height) !important;
  box-sizing: border-box !important;
  background-color: var(--bg-color-tertiary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color-primary) !important;
  box-shadow: 0 0 0 1px var(--border-color) !important;
}

.el-input__inner {
  height: 100% !important;
  line-height: var(--form-element-height) !important;
  color: var(--text-color-primary) !important;
  background-color: transparent !important;
  font-family: var(--font-family-serif) !important;
}

.el-select {
  width: 100%;
}

.el-select__wrapper {
  height: var(--form-element-height) !important;
}

.el-radio-button__inner {
  height: var(--form-element-height) !important;
  line-height: calc(var(--form-element-height) - 2px) !important;
  padding: var(--form-element-padding) !important;
  background-color: transparent !important;
  border: none !important;
  color: var(--text-color-primary) !important;
  border-radius: var(--form-element-border-radius) !important;
  margin: 0 !important;
  box-shadow: none !important;
  outline: none !important;
}

.el-radio-button.is-active .el-radio-button__inner {
  background-color: var(--highlight-color) !important;
  border: none !important;
  color: white !important;
  box-shadow: none !important;
}

.el-button--small,
.el-button--default {
  height: var(--form-element-height) !important;
  line-height: var(--form-element-height) !important;
  padding: var(--form-element-padding) !important;
  background-color: var(--bg-color-tertiary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color-primary) !important;
}

.el-button--primary {
  background-color: var(--highlight-color) !important;
  border-color: var(--highlight-color) !important;
  color: white !important;
}

/* Pagination controls */
.el-pagination {
  display: flex;
  justify-content: center;
  margin: 20px auto;
  padding: 10px 0;
}

.el-pagination .el-select .el-input,
.el-pagination button,
.el-pagination span:not([class*=suffix]),
.el-pagination .el-input__wrapper,
.el-pagination .el-input__inner {
  height: var(--form-element-height) !important;
  line-height: var(--form-element-height) !important;
  color: var(--text-color-primary) !important;
}

.el-pagination .el-select .el-input {
  width: auto;
}

.el-pagination button:not(:disabled) {
  color: var(--text-color-primary) !important;
  background-color: var(--bg-color-tertiary) !important;
}

.el-pagination button:disabled {
  color: var(--text-color-secondary) !important;
  background-color: var(--bg-color-secondary) !important;
}

/* 当前页码样式 */
.el-pagination .is-active {
  color: #ffffff !important;
  background-color: var(--highlight-color) !important;
  font-weight: bold;
  border-radius: 4px;
}

/* 页码按钮样式 */
.el-pagination .el-pager li {
  background-color: #f5f1ea !important;
  color: var(--text-color-primary) !important;
  border: 1px solid #e0d6c9 !important;
  margin: 0 3px;
  min-width: 32px;
  height: 32px;
  line-height: 32px;
  border-radius: 4px;
  transition: all 0.3s;
}

/* 页码按钮悬停样式 */
.el-pagination .el-pager li:hover:not(.is-active) {
  color: var(--highlight-color) !important;
  border-color: var(--highlight-color) !important;
}

/* 前进后退按钮样式 */
.el-pagination .btn-prev,
.el-pagination .btn-next {
  background-color: #f5f1ea !important;
  color: var(--text-color-primary) !important;
  border: 1px solid #e0d6c9 !important;
  border-radius: 4px;
  margin: 0 3px;
  padding: 0 10px;
}

/* 前进后退按钮悬停样式 */
.el-pagination .btn-prev:hover,
.el-pagination .btn-next:hover {
  color: var(--highlight-color) !important;
  border-color: var(--highlight-color) !important;
}

/* Fix for select dropdown in pagination */
.el-pagination .el-select .el-input .el-input__wrapper {
  padding-right: 25px !important;
}

/* Responsive design for different screen sizes */
@media (max-width: 1200px) {
  :root {
    --content-width: 90%;
  }
}

@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    align-items: center;
    padding: 10px;
  }

  .logo-container {
    margin-bottom: 10px;
  }

  .nav-container {
    justify-content: center;
    width: 100%;
  }

  .nav-link {
    font-size: 1rem;
    padding: 4px 8px;
    margin-left: 4px;
  }

  .app-title {
    font-size: 1.75rem;
  }
}

/* Ensure content integrity when scaling/zooming */
@media (min-resolution: 1.25dppx) {
  .header-container,
  .app-main,
  .app-footer {
    transform: none;
    transform-origin: top left;
  }
}
</style>


