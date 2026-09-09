import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  register: (data) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

export const documentsAPI = {
  list: (skip = 0, limit = 50, organization = null) => {
    let url = `/documents/?skip=${skip}&limit=${limit}`;
    if (organization) url += `&organization=${organization}`;
    return api.get(url);
  },
  get: (id) => api.get(`/documents/${id}`),
  previewSerial: (organization, holderName = 'Titular') => api.get(`/documents/preview-serial/${organization}?holder_name=${encodeURIComponent(holderName)}`),
  previewQR: (organization, holderName = 'Titular') => api.get(`/documents/preview-qr/${organization}?holder_name=${encodeURIComponent(holderName)}`),
  create: (formData) => api.post('/documents/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id) => api.delete(`/documents/${id}`),
};

export const verifyAPI = {
  getCaptcha: (organization, serial) => api.get(`/verify/${organization}/${serial}/captcha`),
  verify: (organization, serial, captchaText) => api.post(`/verify/${organization}/${serial}`, { captcha_text: captchaText }),
  download: (organization, serial) => api.get(`/verify/${organization}/${serial}/download`),
};

export default api;
