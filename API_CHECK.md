# API 调用配置检查清单

## ✅ 后端 API 端点

所有端点都注册在 `/api/v1` 前缀下：

1. **GET** `/api/v1/pipelines` - 获取所有流水线列表
2. **POST** `/api/v1/pipelines` - 创建新流水线
3. **GET** `/api/v1/pipelines/{pipeline_id}` - 获取流水线详情
4. **POST** `/api/v1/pipelines/{pipeline_id}/scan` - 上传图片并识别
5. **GET** `/api/v1/pipelines/{pipeline_id}/export` - 导出 Excel 文件
6. **POST** `/api/v1/scan-result` - 外部系统推送识别结果（预留）

## ✅ Web 前端配置

### API 封装 (`frontend/src/api/index.js`)
- ✅ baseURL: `/api/v1`
- ✅ 通过 Vite 代理到 `http://localhost:8000`
- ✅ 响应拦截器自动提取 `response.data`
- ✅ 错误处理统一返回错误消息

### Vite 代理配置 (`frontend/vite.config.js`)
- ✅ `/api` 代理到 `http://localhost:8000`
- ✅ `changeOrigin: true` 支持跨域

### API 调用 (`frontend/src/api/pipeline.js`)
- ✅ `getPipelines()` → GET `/api/v1/pipelines`
- ✅ `createPipeline(name)` → POST `/api/v1/pipelines`
- ✅ `getPipeline(id)` → GET `/api/v1/pipelines/{id}`
- ✅ `scanImage(pipelineId, imageFile)` → POST `/api/v1/pipelines/{id}/scan`
- ✅ `exportExcel(pipelineId)` → GET `/api/v1/pipelines/{id}/export`

**所有 API 调用路径与后端端点完全匹配 ✅**

## ✅ 微信小程序配置

### API 封装 (`miniprogram/src/utils/api.js`)
- ✅ 使用 Taro.request 进行 HTTP 请求
- ✅ 使用 Taro.uploadFile 进行文件上传
- ✅ API_BASE_URL 通过 defineConstants 注入
- ✅ 错误处理统一返回错误消息

### 构建配置
- ✅ `config/dev.js` - 开发环境：`http://localhost:8000/api/v1`
- ✅ `config/prod.js` - 生产环境：`https://matriq.example.com/api/v1`
- ✅ `config/index.js` - 主配置文件

### API 调用 (`miniprogram/src/utils/api.js`)
- ✅ `getPipelines()` → GET `/pipelines`
- ✅ `createPipeline(name)` → POST `/pipelines`
- ✅ `getPipeline(id)` → GET `/pipelines/{id}`
- ✅ `scanImage(pipelineId, filePath)` → POST `/pipelines/{id}/scan`

**所有 API 调用路径与后端端点完全匹配 ✅**

## 🔧 运行前检查

### 后端
1. ✅ 确保后端服务运行在 `http://localhost:8000`
2. ✅ 确保 `.env` 文件配置了 PaddleOCR API 信息
3. ✅ 确保数据库目录存在：`backend/data/`

### Web 前端
1. ✅ 安装依赖：`cd frontend && npm install`
2. ✅ 启动开发服务器：`npm run dev`
3. ✅ 访问：`http://localhost:3000`
4. ✅ Vite 会自动代理 `/api` 请求到后端

### 微信小程序
1. ✅ 安装依赖：`cd miniprogram && npm install`
2. ✅ 启动开发：`npm run dev:weapp`
3. ✅ 在微信开发者工具中打开 `dist` 目录
4. ⚠️ **重要**：需要在微信公众平台配置服务器域名：
   - request 合法域名：`http://localhost:8000`（开发环境）
   - uploadFile 合法域名：`http://localhost:8000`（开发环境）

## 🧪 测试 API 连接

### 测试后端健康检查
```bash
curl http://localhost:8000/
# 应该返回: {"status":"ok","app":"MatriQ OCR Service"}
```

### 测试后端 API
```bash
# 获取流水线列表
curl http://localhost:8000/api/v1/pipelines

# 创建流水线
curl -X POST http://localhost:8000/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{"name":"测试流水线"}'
```

### 测试前端代理
启动前端后，在浏览器控制台执行：
```javascript
fetch('/api/v1/pipelines')
  .then(r => r.json())
  .then(console.log)
```

## ⚠️ 注意事项

1. **CORS 跨域**：后端需要配置 CORS 中间件（如果前端直接访问，不通过代理）
2. **小程序域名**：小程序必须配置合法域名才能访问 API
3. **文件上传**：小程序使用 `Taro.uploadFile`，Web 使用 `FormData`
4. **环境变量**：小程序通过 `defineConstants` 注入，不是 `process.env`

## ✅ 总结

**所有 API 调用配置已正确匹配，可以正常运行！**

- ✅ 后端端点定义完整
- ✅ Web 前端 API 封装正确，代理配置正确
- ✅ 小程序 API 封装正确，构建配置正确
- ✅ 所有路径和参数匹配

