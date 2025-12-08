<template>
  <div class="pipeline-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>流水线列表</span>
          <el-button type="primary" @click="$router.push('/pipelines/new')">
            <el-icon><Plus /></el-icon>
            新建流水线
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="pipelines"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="流水线名称" />
        <el-table-column prop="code" label="流水线编码" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_scans" label="识别次数" width="120" align="center" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="handleView(row.id)"
            >
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button
              type="success"
              link
              @click="handleExport(row.id)"
            >
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && pipelines.length === 0" description="暂无流水线，请创建新流水线" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, View, Download } from '@element-plus/icons-vue'
import { getPipelines, exportExcel } from '@/api/pipeline'

const router = useRouter()
const loading = ref(false)
const pipelines = ref([])

const loadPipelines = async () => {
  loading.value = true
  try {
    pipelines.value = await getPipelines()
  } catch (error) {
    ElMessage.error('加载流水线列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleView = (id) => {
  router.push(`/pipelines/${id}`)
}

const handleExport = async (id) => {
  try {
    const blob = await exportExcel(id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `pipeline_${id}_export.xlsx`
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
  loadPipelines()
})
</script>

<style scoped>
.pipeline-list {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

