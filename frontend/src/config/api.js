// API設定
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  DIALOGUE_START: `${API_BASE_URL}/api/dialogue/start`,
  DIALOGUE_NEXT: `${API_BASE_URL}/api/dialogue/next`,
  DIALOGUE_CHARACTER: `${API_BASE_URL}/api/dialogue/character`,
  DIALOGUE_OPTIONS: `${API_BASE_URL}/api/dialogue/options`,
  CHARACTERS: `${API_BASE_URL}/api/characters`,
  CHARACTER: (id) => `${API_BASE_URL}/api/characters/${id}`,
};

export default API_BASE_URL; 