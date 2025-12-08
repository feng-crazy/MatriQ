# MatriQ Web 前端

基于 Vue 3 + Element Plus 的物料标签识别助手 Web 前端。

## 功能特性

- ✅ 流水线管理（列表、创建、查看）
- ✅ 图片上传与识别（支持拖拽上传）
- ✅ 识别结果展示（表格形式，包含所有字段）
- ✅ Excel 导出功能
- ✅ 响应式设计，支持主流浏览器

## 技术栈

- Vue 3 (Composition API)
- Vue Router 4
- Pinia (状态管理)
- Element Plus (UI 组件库)
- Axios (HTTP 客户端)
- Vite (构建工具)

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist` 目录。

## 项目结构

```
frontend/
├── src/
│   ├── api/           # API 接口封装
│   ├── components/    # 公共组件
│   ├── views/         # 页面组件
│   ├── router/        # 路由配置
│   ├── utils/         # 工具函数
│   ├── stores/        # Pinia stores
│   ├── App.vue        # 根组件
│   └── main.js        # 入口文件
├── public/            # 静态资源
├── index.html         # HTML 模板
├── vite.config.js     # Vite 配置
└── package.json       # 项目配置
```

## API 配置

前端通过 Vite 代理连接到后端 API（开发环境）。

生产环境需要配置 `vite.config.js` 中的 `server.proxy` 或使用环境变量。

## 浏览器支持

- Chrome (最新版)
- Edge (最新版)
- Safari (最新版)
- Firefox (最新版)

