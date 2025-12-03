import { useState, useEffect } from 'react'
import { View, Text, ScrollView, Image, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getPipeline, scanImage } from '@/utils/api'
import './index.scss'

export default function PipelineDetail() {
  const router = Taro.useRouter()
  const pipelineId = router.params.id

  const [pipeline, setPipeline] = useState(null)
  const [loading, setLoading] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [selectedImage, setSelectedImage] = useState(null)
  const [scanResults, setScanResults] = useState([])

  useEffect(() => {
    loadPipeline()
  }, [])

  const loadPipeline = async () => {
    setLoading(true)
    try {
      const data = await getPipeline(pipelineId)
      setPipeline(data)
    } catch (error) {
      Taro.showToast({
        title: '加载失败: ' + error.message,
        icon: 'none',
      })
      setTimeout(() => {
        Taro.navigateBack()
      }, 1500)
    } finally {
      setLoading(false)
    }
  }

  const handleChooseImage = () => {
    Taro.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['camera', 'album'],
      success: (res) => {
        setSelectedImage(res.tempFilePaths[0])
      },
      fail: (err) => {
        Taro.showToast({
          title: '选择图片失败',
          icon: 'none',
        })
      },
    })
  }

  const handleScan = async () => {
    if (!selectedImage) {
      Taro.showToast({
        title: '请先选择图片',
        icon: 'none',
      })
      return
    }

    setScanning(true)
    try {
      const result = await scanImage(pipelineId, selectedImage)
      setScanResults((prev) => [result, ...prev])
      setSelectedImage(null)
      Taro.showToast({
        title: '识别成功',
        icon: 'success',
      })
    } catch (error) {
      Taro.showToast({
        title: '识别失败: ' + error.message,
        icon: 'none',
      })
    } finally {
      setScanning(false)
    }
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

  if (loading) {
    return (
      <View className="pipeline-detail-page">
        <View className="loading">加载中...</View>
      </View>
    )
  }

  if (!pipeline) {
    return null
  }

  return (
    <View className="pipeline-detail-page">
      <View className="header-bar">
        <Text className="pipeline-name">{pipeline.name}</Text>
        <Text className="pipeline-code">{pipeline.code}</Text>
      </View>

      <ScrollView className="content" scrollY>
        {/* 图片上传区域 */}
        <View className="upload-section">
          {selectedImage ? (
            <View className="image-preview">
              <Image src={selectedImage} mode="aspectFit" className="preview-image" />
              <View className="image-actions">
                <Button className="action-btn" onClick={handleScan} loading={scanning}>
                  开始识别
                </Button>
                <Button
                  className="action-btn cancel"
                  onClick={() => setSelectedImage(null)}
                >
                  取消
                </Button>
              </View>
            </View>
          ) : (
            <View className="upload-area" onClick={handleChooseImage}>
              <Text className="upload-icon">📷</Text>
              <Text className="upload-text">点击选择图片或拍照</Text>
              <Text className="upload-tip">支持 JPG/PNG 格式</Text>
            </View>
          )}
        </View>

        {/* 识别结果 */}
        {scanResults.length > 0 && (
          <View className="results-section">
            <Text className="section-title">识别结果</Text>
            {scanResults.map((result, index) => (
              <View key={index} className="result-card">
                <View className="result-header">
                  <Text className="result-time">{formatDate(result.scan_time)}</Text>
                </View>
                <View className="result-content">
                  <View className="result-row">
                    <Text className="result-label">物料编码：</Text>
                    <Text className="result-value">{result.material_code || '-'}</Text>
                  </View>
                  <View className="result-row">
                    <Text className="result-label">数量：</Text>
                    <Text className="result-value">{result.quantity || '-'}</Text>
                  </View>
                  <View className="result-row">
                    <Text className="result-label">批次：</Text>
                    <Text className="result-value">{result.batch || '-'}</Text>
                  </View>
                  <View className="result-row">
                    <Text className="result-label">日期：</Text>
                    <Text className="result-value">{result.date || '-'}</Text>
                  </View>
                  <View className="result-row">
                    <Text className="result-label">品牌：</Text>
                    <Text className="result-value">{result.brand || '-'}</Text>
                  </View>
                  <View className="result-row">
                    <Text className="result-label">电气特性：</Text>
                    <Text className="result-value">{result.electrical_characteristics || '-'}</Text>
                  </View>
                  <View className="result-row full-width">
                    <Text className="result-label">原始OCR：</Text>
                    <Text className="result-value ocr-text">{result.raw_ocr_text || '-'}</Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}

        {scanResults.length === 0 && (
          <View className="empty-results">
            <Text>暂无识别结果</Text>
            <Text className="empty-tip">请上传图片进行识别</Text>
          </View>
        )}
      </ScrollView>
    </View>
  )
}

