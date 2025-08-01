import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health check
  async healthCheck() {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Upload and analyze video - returns results directly
  async analyzeVideo(videoFile, analysisConfig) {
    try {
      const formData = new FormData();
      formData.append('video', videoFile);
      formData.append('api_key', analysisConfig.apiKey);
      formData.append('prompt_type', analysisConfig.promptType);
      
      if (analysisConfig.customPrompt) {
        formData.append('custom_prompt', analysisConfig.customPrompt);
      }
      
      formData.append('analyzer', analysisConfig.analyzer || 'gemini');
      formData.append('model', analysisConfig.model || 'gemini-2.0-flash-exp');
      formData.append('temperature', analysisConfig.temperature || 0.1);
      formData.append('max_tokens', analysisConfig.maxTokens || 8192);

      const response = await this.api.post('/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handler
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || error.message;
      return new Error(`API Error: ${message}`);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network Error: Unable to connect to the server');
    } else {
      // Something else happened
      return new Error(`Error: ${error.message}`);
    }
  }
}

export default new ApiService(); 