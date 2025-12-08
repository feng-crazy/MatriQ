<font style="color:rgb(17, 17, 51);">对于 Excel 表格的设计，我们建议如下表结构：</font>

| <font style="color:rgb(17, 17, 51);">序号</font> | <font style="color:rgb(17, 17, 51);">识别时间</font> | <font style="color:rgb(17, 17, 51);">物料编码</font> | <font style="color:rgb(17, 17, 51);">数量</font> | <font style="color:rgb(17, 17, 51);">批次</font> | <font style="color:rgb(17, 17, 51);">日期</font> | <font style="color:rgb(17, 17, 51);">品牌</font> | <font style="color:rgb(17, 17, 51);">电气特性</font> | <font style="color:rgb(17, 17, 51);">原始OCR文本</font> | <font style="color:rgb(17, 17, 51);">图片文件名</font> |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <font style="color:rgb(17, 17, 51);">1</font> | <font style="color:rgb(17, 17, 51);">YYYY-MM-DD HH:mm:ss</font> | <font style="color:rgb(17, 17, 51);">SL-IND-1008-100</font> | <font style="color:rgb(17, 17, 51);">4000</font> | <font style="color:rgb(17, 17, 51);">B2511A</font> | <font style="color:rgb(17, 17, 51);">2025-11-30</font> | <font style="color:rgb(17, 17, 51);">Sunlord</font> | <font style="color:rgb(17, 17, 51);">10uH ±10%</font> | <font style="color:rgb(17, 17, 51);">"Sunlord SL-IND-1008-100 Qty:4000..."</font> | <font style="color:rgb(17, 17, 51);">img_20251130.jpg</font> |


<font style="color:rgb(17, 17, 51);">数据库方面，考虑到初期可以使用 SQLite 或 PostgreSQL 存储流水线信息及配置，后期可扩展支持更多数据存储需求。</font>

#### <font style="color:rgb(17, 17, 51);">数据库表设计示例</font>
**<font style="color:rgb(17, 17, 51);">Pipelines 表</font>**

| <font style="color:rgb(17, 17, 51);">字段名</font> | <font style="color:rgb(17, 17, 51);">类型</font> | <font style="color:rgb(17, 17, 51);">描述</font> |
| --- | --- | --- |
| <font style="color:rgb(17, 17, 51);">id</font> | <font style="color:rgb(17, 17, 51);">INT</font> | <font style="color:rgb(17, 17, 51);">主键，自动递增</font> |
| <font style="color:rgb(17, 17, 51);">name</font> | <font style="color:rgb(17, 17, 51);">VARCHAR</font> | <font style="color:rgb(17, 17, 51);">流水线名称</font> |
| <font style="color:rgb(17, 17, 51);">created_at</font> | <font style="color:rgb(17, 17, 51);">TIMESTAMP</font> | <font style="color:rgb(17, 17, 51);">创建时间</font> |


**<font style="color:rgb(17, 17, 51);">RecognitionResults 表</font>**

| <font style="color:rgb(17, 17, 51);">字段名</font> | <font style="color:rgb(17, 17, 51);">类型</font> | <font style="color:rgb(17, 17, 51);">描述</font> |
| --- | --- | --- |
| <font style="color:rgb(17, 17, 51);">id</font> | <font style="color:rgb(17, 17, 51);">INT</font> | <font style="color:rgb(17, 17, 51);">主键，自动递增</font> |
| <font style="color:rgb(17, 17, 51);">pipeline_id</font> | <font style="color:rgb(17, 17, 51);">INT</font> | <font style="color:rgb(17, 17, 51);">外键，关联流水线</font> |
| <font style="color:rgb(17, 17, 51);">material_code</font> | <font style="color:rgb(17, 17, 51);">VARCHAR</font> | <font style="color:rgb(17, 17, 51);">物料编码</font> |
| <font style="color:rgb(17, 17, 51);">quantity</font> | <font style="color:rgb(17, 17, 51);">INT</font> | <font style="color:rgb(17, 17, 51);">数量</font> |
| <font style="color:rgb(17, 17, 51);">batch</font> | <font style="color:rgb(17, 17, 51);">VARCHAR</font> | <font style="color:rgb(17, 17, 51);">批次</font> |
| <font style="color:rgb(17, 17, 51);">date</font> | <font style="color:rgb(17, 17, 51);">DATE</font> | <font style="color:rgb(17, 17, 51);">日期</font> |
| <font style="color:rgb(17, 17, 51);">brand</font> | <font style="color:rgb(17, 17, 51);">VARCHAR</font> | <font style="color:rgb(17, 17, 51);">品牌</font> |
| <font style="color:rgb(17, 17, 51);">electrical_characteristics</font> | <font style="color:rgb(17, 17, 51);">VARCHAR</font> | <font style="color:rgb(17, 17, 51);">电气特性</font> |
| <font style="color:rgb(17, 17, 51);">raw_ocr_text</font> | <font style="color:rgb(17, 17, 51);">TEXT</font> | <font style="color:rgb(17, 17, 51);">原始 OCR 文本</font> |
| <font style="color:rgb(17, 17, 51);">image_filename</font> | <font style="color:rgb(17, 17, 51);">VARCHAR</font> | <font style="color:rgb(17, 17, 51);">图片文件名</font> |
| <font style="color:rgb(17, 17, 51);">recognized_at</font> | <font style="color:rgb(17, 17, 51);">TIMESTAMP</font> | <font style="color:rgb(17, 17, 51);">识别时间</font> |


