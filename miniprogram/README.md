# MatriQ 微信小程序

基于 Taro + React 的物料标签识别助手微信小程序。

## 功能特性

- ✅ 快速扫描识别（拍照或选择图片）
- ✅ 流水线管理（列表、创建、查看）
- ✅ 图片上传与识别
- ✅ 识别结果展示（所有字段）
- ✅ 支持微信小程序和 H5

## 技术栈

- Taro 3.x (多端框架)
- React 18
- Taro UI (UI 组件库)

## 快速开始

### 安装依赖

```bash
cd miniprogram
npm install
```

### 开发模式

#### 微信小程序

```bash
npm run dev:weapp
```

使用微信开发者工具打开 `dist` 目录。

#### H5

```bash
npm run dev:h5
```

访问 http://localhost:10086

### 构建生产版本

```bash
# 微信小程序
npm run build:weapp

# H5
npm run build:h5
```

## 项目结构

```
miniprogram/
├── src/
│   ├── pages/         # 页面
│   │   ├── index/     # 首页
│   │   ├── pipeline-list/    # 流水线列表
│   │   ├── pipeline-new/      # 新建流水线
│   │   └── pipeline-detail/   # 流水线详情
│   ├── components/    # 组件
│   ├── utils/         # 工具函数
│   │   └── api.js     # API 封装
│   ├── app.js         # 应用入口
│   └── app.config.js  # 应用配置
├── config/            # 构建配置
└── package.json
```

## API 配置

在 `config/dev.js` 和 `config/prod.js` 中配置 API 基础 URL。

## 小程序配置

1. 在微信公众平台注册小程序
2. 配置服务器域名（API 地址）
3. 使用微信开发者工具打开项目

## 注意事项

- 小程序需要配置合法域名才能访问 API
- 图片上传需要在小程序后台配置 uploadFile 域名
- 相机权限需要在 app.json 中声明

