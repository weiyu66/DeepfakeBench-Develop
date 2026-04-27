import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 60000, // 推理可能较慢
})

export async function uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/predict', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
    return response.data
}

export async function checkHealth() {
    const response = await api.get('/health')
    return response.data
}
