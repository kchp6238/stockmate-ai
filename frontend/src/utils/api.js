import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 90000,
})

api.interceptors.response.use(
  r => r,
  err => {
    if (!err.response)                   err.message = '서버에 연결할 수 없습니다.'
    else if (err.response.status === 429) err.message = '요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.'
    else if (err.response.status === 404) err.message = err.response.data?.detail || '종목을 찾을 수 없습니다.'
    else                                  err.message = err.response.data?.detail || '오류가 발생했습니다.'
    return Promise.reject(err)
  }
)
export default api
