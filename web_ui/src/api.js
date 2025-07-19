import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(
      `Making ${config.method?.toUpperCase()} request to ${config.url}`
    );
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const ragAPI = {
  // Ask a question
  askQuestion: async (question, maxTokens = 300) => {
    const response = await api.post("/api/ask", {
      question,
      max_tokens: maxTokens,
    });
    return response.data;
  },

  // Search documents
  searchDocuments: async (query, topK = 5) => {
    const response = await api.post("/api/search", {
      query,
      top_k: topK,
    });
    return response.data;
  },

  // Get system statistics
  getStats: async () => {
    const response = await api.get("/api/stats");
    return response.data;
  },

  // Upload documents
  uploadDocuments: async (files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await api.post("/api/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  // Clear all documents
  clearDocuments: async () => {
    const response = await api.delete("/api/clear");
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get("/");
    return response.data;
  },
};

export default api;
