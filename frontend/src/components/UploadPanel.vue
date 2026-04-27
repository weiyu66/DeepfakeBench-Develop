<template>
  <div class="upload-panel">
    <el-upload
      class="upload-drag"
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      :show-file-list="false"
      accept="image/jpeg,image/png,image/webp,image/bmp"
    >
      <template v-if="!previewUrl">
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽图片到此处，或 <em>点击上传</em>
        </div>
        <div class="el-upload__tip">
          支持 JPG / PNG / WebP / BMP 格式，建议上传包含清晰人脸的图片
        </div>
      </template>
      <template v-else>
        <img :src="previewUrl" class="preview-image" alt="预览" />
      </template>
    </el-upload>

    <div class="action-bar">
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!selectedFile"
        @click="handleDetect"
      >
        {{ loading ? '检测中...' : '开始检测' }}
      </el-button>
      <el-button size="large" @click="handleClear">清除</el-button>
    </div>

    <el-alert
      v-if="errorMsg"
      :title="errorMsg"
      type="error"
      show-icon
      closable
      @close="errorMsg = ''"
      style="margin-top: 16px;"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadImage } from '../api.js'

const emit = defineEmits(['result'])

const selectedFile = ref(null)
const previewUrl = ref('')
const loading = ref(false)
const errorMsg = ref('')

function handleFileChange(file) {
  errorMsg.value = ''
  const raw = file.raw
  if (!raw) return

  // 校验文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp']
  if (!allowedTypes.includes(raw.type)) {
    errorMsg.value = '不支持的文件格式，请上传 JPG / PNG / WebP / BMP 图片'
    return
  }

  // 校验文件大小 (最大 10MB)
  if (raw.size > 10 * 1024 * 1024) {
    errorMsg.value = '图片大小不能超过 10MB'
    return
  }

  selectedFile.value = raw
  previewUrl.value = URL.createObjectURL(raw)
}

async function handleDetect() {
  if (!selectedFile.value) {
    errorMsg.value = '请先上传一张图片'
    return
  }

  loading.value = true
  errorMsg.value = ''
  emit('result', null)

  try {
    const data = await uploadImage(selectedFile.value)
    if (data.success) {
      emit('result', data.data)
    } else {
      errorMsg.value = data.message || '检测失败'
    }
  } catch (err) {
    console.error(err)
    errorMsg.value = err.response?.data?.detail || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

function handleClear() {
  selectedFile.value = null
  previewUrl.value = ''
  errorMsg.value = ''
  emit('result', null)
}
</script>

<style scoped>
.upload-panel {
  width: 100%;
}

.upload-drag {
  width: 100%;
}

.upload-drag :deep(.el-upload-dragger) {
  width: 100%;
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 260px;
  object-fit: contain;
  border-radius: 8px;
}

.action-bar {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
}
</style>
