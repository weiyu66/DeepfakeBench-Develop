<template>
  <div class="result-card" :class="{ fake: result.is_fake, real: !result.is_fake }">
    <div class="result-header">
      <el-icon size="48" class="result-icon">
        <CircleClose v-if="result.is_fake" color="#f56c6c" />
        <CircleCheck v-else color="#67c23a" />
      </el-icon>
      <h2 class="result-title">
        {{ result.is_fake ? '🔴 检测到伪造人脸' : '🟢 真实人脸' }}
      </h2>
    </div>

    <div class="result-body">
      <p class="result-message">{{ result.message }}</p>

      <div class="confidence-bar">
        <div class="bar-label">
          <span>真实</span>
          <span>伪造</span>
        </div>
        <el-progress
          :percentage="Math.round(result.confidence * 100)"
          :color="result.is_fake ? '#f56c6c' : '#67c23a'"
          :stroke-width="20"
          :show-text="true"
        />
      </div>

      <div class="meta-info">
        <el-tag :type="result.is_fake ? 'danger' : 'success'" size="large">
          伪造概率: {{ (result.confidence * 100).toFixed(2) }}%
        </el-tag>
        <el-tag type="info" size="large">
          人脸检测: {{ result.has_face ? '成功' : '失败' }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'

defineProps({
  result: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.result-card {
  border-radius: 16px;
  padding: 30px;
  text-align: center;
  transition: all 0.3s ease;
}

.result-card.fake {
  background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
  border: 2px solid #f56c6c;
}

.result-card.real {
  background: linear-gradient(135deg, #f0f9eb 0%, #e0f5d8 100%);
  border: 2px solid #67c23a;
}

.result-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.result-icon {
  margin-bottom: 12px;
}

.result-title {
  font-size: 1.5rem;
  margin: 0;
}

.result-message {
  font-size: 1.05rem;
  color: #555;
  margin-bottom: 24px;
  line-height: 1.6;
}

.confidence-bar {
  margin-bottom: 24px;
}

.bar-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.85rem;
  color: #888;
}

.meta-info {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
