import api from './index'

/**
 * 获取所有流水线列表
 */
export function getPipelines() {
  return api.get('/pipelines')
}

/**
 * 获取流水线详情
 */
export function getPipeline(id) {
  return api.get(`/pipelines/${id}`)
}

/**
 * 创建新流水线
 */
export function createPipeline(name) {
  return api.post('/pipelines', { name })
}

/**
 * 上传图片并识别
 */
export function scanImage(pipelineId, imageFile) {
  const formData = new FormData()
  formData.append('image', imageFile)
  return api.post(`/pipelines/${pipelineId}/scan`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 导出 Excel
 */
export function exportExcel(pipelineId) {
  return api.get(`/pipelines/${pipelineId}/export`, {
    responseType: 'blob',
  })
}

