import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
  
  getNeo4jHealth: async () => {
    const response = await apiClient.get('/health/neo4j');
    return response.data;
  },

  // Analytics
  getAnalyticsOverview: async () => {
    const response = await apiClient.get('/analytics/overview');
    return response.data;
  },

  getRiskDistribution: async () => {
    const response = await apiClient.get('/analytics/risk-distribution');
    return response.data;
  },

  getBankRisk: async () => {
    const response = await apiClient.get('/analytics/bank-risk');
    return response.data;
  },

  // Accounts
  getAccounts: async (params) => {
    // Convert account_id to search parameter for backend filtering
    if (params && params.account_id) {
      params.search = params.account_id;
      delete params.account_id;
    }
    const response = await apiClient.get('/accounts', { params });
    return response.data;
  },

  getAccountDetails: async (accountId) => {
    const response = await apiClient.get(`/accounts/${accountId}`);
    return response.data;
  },

  getAccountNeighbors: async (accountId) => {
    const response = await apiClient.get(`/accounts/${accountId}/neighbors`);
    return response.data;
  },

  getMLPrediction: async (accountId) => {
    const response = await apiClient.get(`/accounts/${accountId}/ml-prediction`);
    return response.data;
  },

  // Networks
  getNetworks: async () => {
    const response = await apiClient.get('/networks');
    return response.data;
  },

  getNetworkGraph: async (networkId) => {
    const response = await apiClient.get(`/networks/${networkId}/graph`);
    return response.data;
  },

  getNetworkMoneyTrail: async (networkId) => {
    const response = await apiClient.get(`/networks/${networkId}/money-trail`);
    return response.data;
  },

  // Investigations
  createInvestigation: async (params) => {
    // params can be { account_id } or { network_id }
    const payload = typeof params === 'string' ? { account_id: params } : params;
    const response = await apiClient.post('/investigations', payload);
    return response.data;
  },

  getInvestigationDetails: async (investigationId) => {
    const response = await apiClient.get(`/investigations/${investigationId}`);
    return response.data;
  },

  getAlerts: async () => {
    const response = await apiClient.get('/alerts');
    return response.data;
  },

  // ML
  getMLMetrics: async () => {
    const response = await apiClient.get('/ml/metrics');
    return response.data;
  },

  // Demo
  getDemoScenario: async () => {
    const response = await apiClient.get('/demo/scenario');
    return response.data;
  }
};
