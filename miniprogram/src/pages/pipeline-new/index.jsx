import { useState } from 'react'
import { View, Text, Input, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { createPipeline } from '@/utils/api'
import './index.scss'

export default function PipelineNew() {
  const [name, setName] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!name.trim()) {
      Taro.showToast({
        title: '请输入流水线名称',
        icon: 'none',
      })
      return
    }

    setSubmitting(true)
    try {
      const result = await createPipeline(name)
      Taro.showToast({
        title: '创建成功',
        icon: 'success',
      })
      setTimeout(() => {
        Taro.navigateTo({
          url: `/pages/pipeline-detail/index?id=${result.id}`,
        })
      }, 1500)
    } catch (error) {
      Taro.showToast({
        title: '创建失败: ' + error.message,
        icon: 'none',
      })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <View className="pipeline-new-page">
      <View className="form-card">
        <Text className="form-label">流水线名称</Text>
        <Input
          className="form-input"
          placeholder="请输入流水线名称，如：SMT-A线"
          value={name}
          onInput={(e) => setName(e.detail.value)}
        />
        <Button
          className="submit-button"
          type="primary"
          onClick={handleSubmit}
          loading={submitting}
        >
          保存并创建
        </Button>
      </View>
    </View>
  )
}

