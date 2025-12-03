import { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getPipelines } from '@/utils/api'
import './index.scss'

export default function PipelineList() {
  const [pipelines, setPipelines] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadPipelines()
  }, [])

  const loadPipelines = async () => {
    setLoading(true)
    try {
      const data = await getPipelines()
      setPipelines(data)
    } catch (error) {
      Taro.showToast({
        title: '加载失败: ' + error.message,
        icon: 'none',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    Taro.navigateTo({
      url: '/pages/pipeline-new/index',
    })
  }

  const handleView = (id) => {
    Taro.navigateTo({
      url: `/pages/pipeline-detail/index?id=${id}`,
    })
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <View className="pipeline-list-page">
      <View className="header-bar">
        <Text className="page-title">我的流水线</Text>
        <View className="create-button" onClick={handleCreate}>
          <Text>+ 新建</Text>
        </View>
      </View>

      <ScrollView className="content" scrollY>
        {loading ? (
          <View className="loading">加载中...</View>
        ) : pipelines.length === 0 ? (
          <View className="empty">
            <Text>暂无流水线</Text>
            <Text className="empty-tip">点击右上角"新建"创建流水线</Text>
          </View>
        ) : (
          pipelines.map((pipeline) => (
            <View
              key={pipeline.id}
              className="pipeline-item"
              onClick={() => handleView(pipeline.id)}
            >
              <View className="item-header">
                <Text className="item-name">{pipeline.name}</Text>
                <Text className="item-code">{pipeline.code}</Text>
              </View>
              <View className="item-info">
                <Text className="info-label">创建时间：</Text>
                <Text className="info-value">{formatDate(pipeline.created_at)}</Text>
              </View>
              <View className="item-info">
                <Text className="info-label">识别次数：</Text>
                <Text className="info-value">{pipeline.total_scans || 0}</Text>
              </View>
              <View className="item-arrow">›</View>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  )
}

