import axios from 'axios';

// Configure axios with the backend URL
const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for file uploads
});

export default apiClient;
export { API_BASE_URL };