```yaml
openapi: 3.0.3
info:
  title: MatriQ 物料标签识别助手 API
  version: 1.0.0
  description: |
    自动识别电子元器件盘卷标签信息，并结构化输出关键字段。
    支持多流水线管理、OCR 识别、Excel 存储及外部系统对接。
servers:
  - url: http://localhost:8000/api/v1
    description: 本地开发环境
  - url: https://matriq.example.com/api/v1
    description: 生产环境

paths:
  /pipelines:
    get:
      summary: 获取所有流水线列表
      tags:
        - 流水线管理
      responses:
        '200':
          description: 成功返回流水线列表
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/PipelineSummary'
    post:
      summary: 创建新流水线
      tags:
        - 流水线管理
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: "SMT-A线"
                  description: 流水线名称
              required: [name]
      responses:
        '201':
          description: 创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PipelineDetail'

  /pipelines/{pipeline_id}:
    get:
      summary: 获取指定流水线详情
      tags:
        - 流水线管理
      parameters:
        - name: pipeline_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: 返回流水线详情
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PipelineDetail'
        '404':
          description: 流水线不存在

  /pipelines/{pipeline_id}/scan:
    post:
      summary: 上传图像并执行标签识别
      tags:
        - 图像识别
      parameters:
        - name: pipeline_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                image:
                  type: string
                  format: binary
                  description: 支持 JPG/PNG 格式
      responses:
        '200':
          description: 识别成功，返回结构化结果
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ScanResult'
        '400':
          description: 图像格式错误或非目标物体
        '500':
          description: OCR 或后处理失败

  /pipelines/{pipeline_id}/export:
    get:
      summary: 下载该流水线的完整 Excel 文件
      tags:
        - 数据导出
      parameters:
        - name: pipeline_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Excel 文件下载
          content:
            application/vnd.openxmlformats-officedocument.spreadsheetml.sheet:
              schema:
                type: string
                format: binary
        '404':
          description: 流水线或文件不存在

  /scan-result:
    post:
      summary: （预留）外部系统推送识别结果（用于集成）
      tags:
        - 系统集成
      security:
        - ApiKeyAuth: []
      parameters:
        - name: pipeline_id
          in: query
          required: false
          schema:
            type: integer
          description: 流水线ID（与 pipeline_code 二选一）
        - name: pipeline_code
          in: query
          required: false
          schema:
            type: string
          description: 流水线编码（与 pipeline_id 二选一）
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ScanResult'
      responses:
        '201':
          description: 接收成功，结果已存储到指定流水线
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "accepted"
                  pipeline_id:
                    type: integer
                    example: 1
                  pipeline_code:
                    type: string
                    example: "line_001_20251130"
                  result_id:
                    type: integer
                    example: 123
        '400':
          description: 参数错误（缺少 pipeline_id 或 pipeline_code）
        '401':
          description: 未授权
        '404':
          description: 指定的流水线不存在

components:
  schemas:
    PipelineSummary:
      type: object
      properties:
        id:
          type: string
          example: "line_001"
        name:
          type: string
          example: "SMT-A线"
        created_at:
          type: string
          format: date-time
          example: "2025-11-30T06:00:00Z"
        total_scans:
          type: integer
          example: 127

    PipelineDetail:
      type: object
      allOf:
        - $ref: '#/components/schemas/PipelineSummary'
        - type: object
          properties:
            excel_path:
              type: string
              example: "/data/line_001_MatriQ.xlsx"

    ScanResult:
      type: object
      properties:
        material_code:
          type: string
          nullable: true
          example: "SL-IND-1008-100"
        quantity:
          type: integer
          nullable: true
          example: 4000
        batch:
          type: string
          nullable: true
          example: "B2511A"
        date:
          type: string
          format: date
          nullable: true
          example: "2025-11-30"
        brand:
          type: string
          nullable: true
          example: "Sunlord"
        electrical_characteristics:
          type: string
          nullable: true
          example: "10uH ±10%"
        raw_ocr_text:
          type: string
          example: "Sunlord SL-IND-1008-100 Qty:4000 Batch:B2511A Date:30/11/2025 L=10uH±10%"
        image_filename:
          type: string
          example: "upload_20251130_064512.jpg"
        scan_time:
          type: string
          format: date-time
          example: "2025-11-30T06:45:12Z"
      required:
        - raw_ocr_text
        - image_filename
        - scan_time

  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

---

### 
