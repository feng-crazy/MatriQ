# MatriQ 快速启动指南

## ✅ API 配置确认

所有前后端 API 调用已正确配置，可以正常运行！

### 后端 API 端点
- ✅ 所有端点注册在 `/api/v1` 前缀
- ✅ 支持 CORS（如果前端直接访问）
- ✅ 健康检查：`GET /`

### Web 前端
- ✅ API baseURL: `/api/v1`
- ✅ Vite 代理：`/api` → `http://localhost:8000`
- ✅ 所有 API 调用路径匹配后端端点

### 微信小程序
- ✅ API baseURL 通过 defineConstants 配置
- ✅ 开发环境：`http://localhost:8000/api/v1`
- ✅ 生产环境：`https://matriq.example.com/api/v1`

## 🚀 启动步骤

### 1. 启动后端服务

```bash
cd backend

# 创建虚拟环境（如果还没有）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
# 参考 .env.example，至少配置 PADDLEOCR_TOKEN

# 启动服务
uvicorn app.main:app --reload
```

后端将在 `http://localhost:8000` 启动

### 2. 启动 Web 前端（可选）

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 启动

**注意**：Vite 会自动代理 `/api` 请求到后端，无需额外配置。

### 3. 启动微信小程序（可选）

```bash
cd miniprogram

# 安装依赖
npm install

# 启动开发
npm run dev:weapp
```

然后在微信开发者工具中：
1. 打开项目
2. 选择 `miniprogram/dist` 目录
3. **重要**：在微信公众平台配置服务器域名：
   - request 合法域名：`http://localhost:8000`（开发环境）
   - uploadFile 合法域名：`http://localhost:8000`（开发环境）

## 🧪 验证 API 连接

### 测试后端

```bash
# 健康检查
curl http://localhost:8000/

# 获取流水线列表
curl http://localhost:8000/api/v1/pipelines
```

### 测试前端代理

在浏览器中访问 `http://localhost:3000`，打开开发者工具，查看网络请求。

## 📝 配置说明

### 后端配置 (.env)

```bash
# 必填：PaddleOCR API
PADDLEOCR_API_URL=https://gfc197xb35lb0274.aistudio-app.com/layout-parsing
PADDLEOCR_TOKEN=your-token-here

# 可选：其他配置
APP_NAME=MatriQ OCR Service
API_PREFIX=/api/v1
```

### 小程序配置

修改 `miniprogram/config/dev.js` 或 `miniprogram/config/prod.js` 中的 `API_BASE_URL`

## ⚠️ 常见问题

1. **前端无法连接后端**
   - 检查后端是否运行在 `http://localhost:8000`
   - 检查 Vite 代理配置是否正确

2. **小程序无法请求 API**
   - 检查微信公众平台是否配置了合法域名
   - 检查 `API_BASE_URL` 配置是否正确

3. **OCR 识别失败**
   - 检查 `.env` 中的 `PADDLEOCR_TOKEN` 是否正确
   - 检查网络是否可以访问 PaddleOCR API

## ✅ 总结

所有 API 配置已正确匹配，按照上述步骤启动即可正常运行！
