import axios from 'axios';

// Base API URL - Backend Flask server runs on port 5001
// Set REACT_APP_API_URL environment variable to override if needed
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Service Functions

/**
 * Upload a CSV file for processing
 * @param {File} file - The CSV file to upload
 * @returns {Promise} Response with processing status
 */
export const uploadDataset = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

/**
 * Get cleaned AE data
 * @param {number} page - Page number for pagination
 * @param {number} limit - Items per page
 * @param {string} search - Search query for filtering
 * @returns {Promise} Response with cleaned data
 */
export const getCleanedData = async (page = 1, limit = 100, search = '') => {
  return api.get('/data/cleaned', {
    params: { page, limit, search },
  });
};

/**
 * Get cluster results
 * @returns {Promise} Response with cluster data
 */
export const getClusters = async () => {
  return api.get('/clusters');
};

/**
 * Get top signals
 * @param {number} topN - Number of top signals to return
 * @returns {Promise} Response with top signals
 */
export const getTopSignals = async (topN = 5) => {
  return api.get('/signals/top', {
    params: { top_n: topN },
  });
};

/**
 * Get cluster summaries (LLM-generated)
 * @param {number} topN - Number of top clusters to summarize
 * @returns {Promise} Response with cluster summaries
 */
export const getClusterSummaries = async (topN = 5) => {
  return api.get('/signals/summaries', {
    params: { top_n: topN },
  });
};

/**
 * Search clusters by drug name or adverse event
 * @param {string} query - Search query
 * @param {string} type - 'drug' or 'adverse_event'
 * @returns {Promise} Response with filtered clusters
 */
export const searchClusters = async (query, type = 'adverse_event') => {
  return api.get('/clusters/search', {
    params: { query, type },
  });
};

/**
 * Get processing status
 * @returns {Promise} Response with current processing status
 */
export const getProcessingStatus = async () => {
  return api.get('/status');
};

/**
 * Get evaluation metrics
 * @returns {Promise} Response with metrics data
 */
export const getMetrics = async () => {
  return api.get('/metrics');
};

/**
 * Reset application data
 * @returns {Promise} Response with reset status
 */
export const resetData = async () => {
  return api.post('/reset');
};

export default api;

