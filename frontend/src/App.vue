<template>
  <div class="app-container">
    <header class="header">
      <h1>🔍 Deepfake 检测系统</h1>
      <p class="subtitle">基于 DeepfakeBench 的网页端识别 Demo</p>
    </header>

    <main class="main-content">
      <UploadPanel @result="handleResult" />
      <ResultCard v-if="result" :result="result" />
    </main>

    <footer class="footer">
      <p>Powered by DeepfakeBench + FastAPI + Vue3</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import UploadPanel from './components/UploadPanel.vue'
import ResultCard from './components/ResultCard.vue'

const result = ref(null)

function handleResult(data) {
  result.value = data
}
</script>

<style scoped>
.app-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  min-height: 500px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 0.95rem;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.footer {
  text-align: center;
  margin-top: 30px;
  color: #999;
  font-size: 0.85rem;
}
</style>
