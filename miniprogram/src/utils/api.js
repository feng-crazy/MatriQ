import Taro from '@tarojs/taro'

// API 基础 URL，通过 Taro defineConstants 注入
// Taro 会在编译时将 defineConstants 中的值直接替换到代码中
// 开发环境：http://localhost:8000/api/v1
// 生产环境：https://matriq.example.com/api/v1
// eslint-disable-next-line
const API_BASE_URL = API_BASE_URL || 'http://localhost:8000/api/v1'

/**
 * 通用请求方法
 */
function request(options) {
  return new Promise((resolve, reject) => {
    Taro.request({
      url: `${API_BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': options.contentType || 'application/json',
        ...options.header,
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(new Error(res.data?.detail || '请求失败'))
        }
      },
      fail: (err) => {
        reject(err)
      },
    })
  })
}

/**
 * 获取所有流水线列表
 */
export function getPipelines() {
  return request({ url: '/pipelines' })
}

/**
 * 获取流水线详情
 */
export function getPipeline(id) {
  return request({ url: `/pipelines/${id}` })
}

/**
 * 创建新流水线
 */
export function createPipeline(name) {
  return request({
    url: '/pipelines',
    method: 'POST',
    data: { name },
  })
}

/**
 * 上传图片并识别
 */
export function scanImage(pipelineId, filePath) {
  return new Promise((resolve, reject) => {
    Taro.uploadFile({
      url: `${API_BASE_URL}/pipelines/${pipelineId}/scan`,
      filePath,
      name: 'image',
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          resolve(data)
        } catch (e) {
          reject(new Error('解析响应失败'))
        }
      },
      fail: reject,
    })
  })
}

