// API設定
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  DIALOGUE_START: `${API_BASE_URL}/api/dialogue/start`,
  DIALOGUE_NEXT: `${API_BASE_URL}/api/dialogue/next`,
};

export default API_BASE_URL; 