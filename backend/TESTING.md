# MatriQ 后端测试指南

## 环境准备

1. **安装依赖**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **配置环境变量**
在项目根目录创建 `.env` 文件（参考 `.env.example`）：
```bash
PADDLEOCR_API_URL=https://gfc197xb35lb0274.aistudio-app.com/layout-parsing
PADDLEOCR_TOKEN=your-actual-token-here
```

## 启动服务

```bash
cd backend
uvicorn app.main:app --reload
```

服务将在 `http://127.0.0.1:8000` 启动。

## API 测试

### 1. 健康检查
```bash
curl http://127.0.0.1:8000/
```

### 2. 创建流水线
```bash
curl -X POST http://127.0.0.1:8000/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{"name": "SMT-A线"}'
```

### 3. 获取流水线列表
```bash
curl http://127.0.0.1:8000/api/v1/pipelines
```

### 4. 上传图片进行识别（替换 {pipeline_id} 和图片路径）
```bash
curl -X POST http://127.0.0.1:8000/api/v1/pipelines/{pipeline_id}/scan \
  -F "image=@/path/to/your/image.jpg"
```

### 5. 导出 Excel
```bash
curl -O http://127.0.0.1:8000/api/v1/pipelines/{pipeline_id}/export
```

## 使用 Swagger UI 测试

访问 `http://127.0.0.1:8000/docs` 可以查看并测试所有 API 接口。

## 常见问题

### OCR 服务调用失败
- 检查 `.env` 中的 `PADDLEOCR_TOKEN` 是否正确
- 确认网络可以访问 `https://gfc197xb35lb0274.aistudio-app.com`
- 查看后端日志中的详细错误信息

### 字段提取不准确
- 检查 `backend/app/services/parser_service.py` 中的提取规则
- 可以根据实际标签格式调整正则表达式模式
