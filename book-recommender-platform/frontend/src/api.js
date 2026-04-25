import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
})

export const fetchDatasetInfo = () => api.get('/dataset-info').then((r) => r.data)
export const fetchMetrics = () => api.get('/metrics').then((r) => r.data)
export const fetchModelStatus = () => api.get('/model-status').then((r) => r.data)
export const fetchPopularBooks = () => api.get('/popular-books').then((r) => r.data)
export const fetchUsers = () => api.get('/users').then((r) => r.data)
export const fetchRecommendations = (userId) => api.get(`/recommendations/${userId}`).then((r) => r.data)
export const fetchUserProfile = (userId) => api.get(`/user-profile/${userId}`).then((r) => r.data)
export const fetchPopularBooks = () => api.get('/popular-books').then((r) => r.data)
export const fetchUsers = () => api.get('/users').then((r) => r.data)
export const fetchRecommendations = (userId) => api.get(`/recommendations/${userId}`).then((r) => r.data)
export const postPredict = (payload) => api.post('/predict', payload).then((r) => r.data)
