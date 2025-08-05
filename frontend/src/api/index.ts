import axios from 'axios';
import { ElMessage } from 'element-plus';

const http = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 30000,
});

http.interceptors.response.use(
  response => response,
  error => {
    const msg = error.response?.data?.detail || error.message || '网络错误';
    ElMessage.error(msg);
    return Promise.reject(error);
  }
);

export default http;