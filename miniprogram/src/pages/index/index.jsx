import { useState } from 'react'
import { View, Button, Text, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

export default function Index() {
  const [scanning, setScanning] = useState(false)

  const handleQuickScan = () => {
    Taro.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['camera', 'album'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        Taro.navigateTo({
          url: `/pages/scan/index?image=${tempFilePath}`,
        })
      },
      fail: (err) => {
        Taro.showToast({
          title: '选择图片失败',
          icon: 'none',
        })
      },
    })
  }

  return (
    <View className="index-page">
      <View className="header">
        <Text className="title">MatriQ</Text>
        <Text className="subtitle">物料标签识别助手</Text>
      </View>

      <View className="content">
        <View className="quick-scan-card">
          <Text className="card-title">快速识别</Text>
          <Text className="card-desc">拍照或选择图片进行标签识别</Text>
          <Button
            className="scan-button"
            type="primary"
            onClick={handleQuickScan}
            loading={scanning}
          >
            开始扫描
          </Button>
        </View>

        <View className="menu-list">
          <View
            className="menu-item"
            onClick={() => Taro.navigateTo({ url: '/pages/pipeline-list/index' })}
          >
            <Text className="menu-icon">📋</Text>
            <Text className="menu-text">我的流水线</Text>
            <Text className="menu-arrow">›</Text>
          </View>
        </View>
      </View>
    </View>
  )
}

