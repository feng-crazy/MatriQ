<template>
  <div class="pipeline-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button @click="$router.push('/pipelines')">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
          <div class="header-info">
            <h3>{{ pipeline.name || '加载中...' }}</h3>
            <span class="pipeline-code">{{ pipeline.code }}</span>
          </div>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出 Excel
          </el-button>
        </div>
      </template>

      <!-- 图片上传区域 -->
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          class="upload-dragger"
          :auto-upload="false"
          :on-change="handleFileChange"
          :show-file-list="false"
          accept="image/jpeg,image/jpg,image/png"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将图片拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 JPG/PNG 格式，文件大小不超过 15MB
            </div>
          </template>
        </el-upload>

        <div v-if="selectedFile" class="selected-file">
          <el-image
            :src="previewUrl"
            style="max-width: 300px; max-height: 300px"
            fit="contain"
          />
          <div class="file-actions">
            <el-button type="primary" @click="handleScan" :loading="scanning">
              <el-icon><Camera /></el-icon>
              开始识别
            </el-button>
            <el-button @click="handleCancelUpload">取消</el-button>
          </div>
        </div>
      </div>

      <!-- 识别结果展示 -->
      <div v-if="scanResults.length > 0" class="results-section">
        <h3>识别结果</h3>
        <el-table
          :data="scanResults"
          style="width: 100%"
          stripe
          border
        >
          <el-table-column prop="scan_time" label="识别时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.scan_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="material_code" label="物料编码" />
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="batch" label="批次" />
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="brand" label="品牌" />
          <el-table-column prop="electrical_characteristics" label="电气特性" />
          <el-table-column prop="image_filename" label="图片文件名" />
          <el-table-column label="原始OCR文本" width="300">
            <template #default="{ row }">
              <el-popover
                placement="top"
                :width="400"
                trigger="hover"
              >
                <template #reference>
                  <el-text truncated>{{ row.raw_ocr_text }}</el-text>
                </template>
                <div style="max-height: 200px; overflow-y: auto">
                  {{ row.raw_ocr_text }}
                </div>
              </el-popover>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-empty
        v-else-if="!loading"
        description="暂无识别结果，请上传图片进行识别"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Download, UploadFilled, Camera } from '@element-plus/icons-vue'
import { getPipeline, scanImage, exportExcel } from '@/api/pipeline'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const scanning = ref(false)
const uploadRef = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const pipeline = reactive({
  id: null,
  name: '',
  code: '',
})
const scanResults = ref([])

const loadPipeline = async () => {
  const id = parseInt(route.params.id)
  if (!id) {
    ElMessage.error('无效的流水线 ID')
    router.push('/pipelines')
    return
  }

  loading.value = true
  try {
    const data = await getPipeline(id)
    Object.assign(pipeline, data)
    pipeline.id = id
  } catch (error) {
    ElMessage.error('加载流水线信息失败: ' + error.message)
    router.push('/pipelines')
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  // 创建预览 URL
  previewUrl.value = URL.createObjectURL(file.raw)
}

const handleCancelUpload = () => {
  selectedFile.value = null
  previewUrl.value = ''
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const handleScan = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }

  scanning.value = true
  try {
    const result = await scanImage(pipeline.id, selectedFile.value)
    scanResults.value.unshift(result)
    ElMessage.success('识别成功')
    handleCancelUpload()
  } catch (error) {
    ElMessage.error('识别失败: ' + error.message)
  } finally {
    scanning.value = false
  }
}

const handleExport = async () => {
  try {
    const blob = await exportExcel(pipeline.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${pipeline.code}_MatriQ.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadPipeline()
})
</script>

<style scoped>
.pipeline-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h3 {
  margin: 0;
  font-size: 18px;
}

.pipeline-code {
  color: #909399;
  font-size: 14px;
}

.upload-section {
  margin-bottom: 32px;
}

.upload-dragger {
  width: 100%;
}

.selected-file {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.file-actions {
  display: flex;
  gap: 12px;
}

.results-section {
  margin-top: 32px;
}

.results-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}
</style>

