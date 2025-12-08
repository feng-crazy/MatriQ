# MatriQ

物料标签识别助手（MatriQ）项目，实现电子元器件盘卷标签的自动识别、结构化输出与流水线管理。

## 当前进展
- ✅ 基于 FastAPI + SQLModel 的后端骨架
- ✅ 流水线管理：创建 / 列表 / 详情 / Excel 导出
- ✅ **已集成 PaddleOCR-VL API**：调用 Baidu AI Studio 的布局解析服务
- ✅ 智能字段提取：从 OCR markdown 文本中自动提取物料编码、数量、批次、日期、品牌、电气特性
- ✅ 图片上传接口：调用 PaddleOCR-VL，解析并写入 SQLite + Excel
- ✅ Excel 表头与数据库结构与需求文档保持一致
- ✅ 预留 `/api/v1/scan-result` 接口便于对接 ERP/MES

## 目录结构
```
MatriQ/
├── backend/          # 后端服务（FastAPI）
│   ├── app/          # 应用代码
│   ├── tests/        # 测试代码
│   └── requirements.txt
├── frontend/         # Web 前端（Vue 3 + Element Plus）
│   ├── src/
│   └── package.json
├── miniprogram/      # 微信小程序（Taro + React）
│   ├── src/
│   └── package.json
└── 文档/              # 项目文档（UI / API / 数据库设计）
```

## 快速启动
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
> 默认监听 `http://127.0.0.1:8000`，API 前缀为 `/api/v1`

## 配置
在项目根目录创建 `.env`（可参考 `.env.example`）：
```bash
# PaddleOCR-VL API 配置（必填）
PADDLEOCR_API_URL=https://gfc197xb35lb0274.aistudio-app.com/layout-parsing
PADDLEOCR_TOKEN=your-token-here

# 应用配置
APP_NAME=MatriQ OCR Service
API_PREFIX=/api/v1

# 数据存储路径
SQLITE_PATH=backend/data/matriq.db
PIPELINES_ROOT=backend/data/pipelines
```

**重要**：请将 `PADDLEOCR_TOKEN` 替换为你的实际 token。更多配置选项详见 `backend/app/core/config.py`。

## OCR 服务说明
系统已集成 **PaddleOCR-VL** API 服务（Baidu AI Studio），支持：
- 布局解析：自动识别文档/图片的布局结构
- 文字识别：提取图片中的全部文字内容（markdown 格式）
- 智能解析：从 OCR 文本中自动提取关键字段（物料编码、数量、批次等）

### 字段提取规则
- **物料编码**：识别如 `SL-IND-1008-100` 等格式
- **数量**：从 "Qty"、"Quantity"、"数量" 等关键词后提取数字
- **批次**：识别 "Batch"、"Lot"、"批次" 等关键词
- **日期**：支持多种日期格式，统一标准化为 `YYYY-MM-DD`
- **品牌**：识别常见品牌（Sunlord、Murata、TDK 等）
- **电气特性**：提取如 `L=10uH±10%` 等规格信息

## 测试

### 运行测试

```bash
cd backend
# 安装依赖（包括测试依赖）
pip install -r requirements.txt

# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

详细测试文档请参考 `backend/tests/README.md`。

## 前端应用

### Web 前端（Vue 3）

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

详细文档请参考 `frontend/README.md`

### 微信小程序（Taro）

```bash
cd miniprogram
npm install
npm run dev:weapp
```

使用微信开发者工具打开 `dist` 目录。

详细文档请参考 `miniprogram/README.md`

## 完整启动流程

1. **启动后端服务**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **启动 Web 前端**（可选）
```bash
cd frontend
npm install
npm run dev
```

3. **启动小程序**（可选）
```bash
cd miniprogram
npm install
npm run dev:weapp
```

## 🚀 部署

### Docker 部署（推荐）

```bash
# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，配置 PADDLEOCR_TOKEN

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

### 传统部署

详细部署文档请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🔄 CI/CD

项目已配置 GitHub Actions CI/CD 工作流：

- ✅ 自动测试（后端、前端、小程序）
- ✅ Docker 镜像自动构建
- ✅ 自动部署到生产环境

详细配置请参考 [.github/workflows/README.md](./.github/workflows/README.md)

## ✅ 项目完成状态

1. ✅ ~~对接实际 OCR/分类模型并补充错误兜底~~（已完成）
2. ✅ ~~编写单元测试与集成测试~~（已完成）
3. ✅ ~~完成 Vue Web 前端 + 小程序界面~~（已完成）
4. ✅ ~~增加 CI/CD、Docker 镜像与部署文档~~（已完成）

## 📚 文档索引

- [快速启动指南](./QUICK_START.md) - 快速开始使用
- [API 配置检查](./API_CHECK.md) - API 调用配置说明
- [部署文档](./DEPLOYMENT.md) - 详细部署指南
- [测试文档](./backend/tests/README.md) - 测试说明
- [前端文档](./frontend/README.md) - Web 前端说明
- [小程序文档](./miniprogram/README.md) - 小程序说明
