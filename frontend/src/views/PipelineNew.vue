<template>
  <div class="pipeline-new">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>新建流水线</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        style="max-width: 600px"
      >
        <el-form-item label="流水线名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入流水线名称，如：SMT-A线"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            保存并创建
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createPipeline } from '@/api/pipeline'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  name: '',
})

const rules = {
  name: [
    { required: true, message: '请输入流水线名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
  ],
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const result = await createPipeline(form.name)
        ElMessage.success('创建成功')
        router.push(`/pipelines/${result.id}`)
      } catch (error) {
        ElMessage.error('创建失败: ' + error.message)
      } finally {
        submitting.value = false
      }
    }
  })
}
</script>

<style scoped>
.pipeline-new {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}
</style>

