# MatriQ 测试文档

## 测试结构

```
tests/
├── conftest.py              # 共享 fixtures 和配置
├── unit/                     # 单元测试
│   ├── test_parser_service.py
│   ├── test_ocr_service.py
│   ├── test_excel_writer.py
│   └── test_pipeline_service.py
└── integration/              # 集成测试
    ├── test_api_pipelines.py
    └── test_api_integration.py
```

## 运行测试

### 安装测试依赖

```bash
cd backend
pip install -r requirements.txt
```

### 运行所有测试

```bash
pytest
```

### 运行单元测试

```bash
pytest tests/unit/
```

### 运行集成测试

```bash
pytest tests/integration/
```

### 运行特定测试文件

```bash
pytest tests/unit/test_parser_service.py
```

### 运行特定测试函数

```bash
pytest tests/unit/test_parser_service.py::TestNormalizeDate::test_standard_formats
```

### 生成覆盖率报告

```bash
pytest --cov=app --cov-report=html
```

覆盖率报告将生成在 `htmlcov/index.html`

## 测试说明

### 单元测试

- **test_parser_service.py**: 测试字段解析逻辑，包括日期标准化、物料编码提取、数量提取等
- **test_ocr_service.py**: 测试 OCR 服务（使用 Mock 模拟外部 API）
- **test_excel_writer.py**: 测试 Excel 文件读写功能
- **test_pipeline_service.py**: 测试流水线服务业务逻辑

### 集成测试

- **test_api_pipelines.py**: 测试流水线相关的所有 API 端点
- **test_api_integration.py**: 测试系统集成 API

### Mock 使用

所有外部依赖（如 PaddleOCR API、数据库）都使用 Mock 进行模拟，确保测试的独立性和速度。

## 持续集成

测试可以在 CI/CD 流程中运行：

```bash
pytest --cov=app --cov-report=xml
```

生成的 `coverage.xml` 可以上传到代码覆盖率服务。

