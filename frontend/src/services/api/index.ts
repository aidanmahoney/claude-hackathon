// API Service - Central point to configure and export the API adapter
// TO SWITCH BETWEEN MOCK AND REAL API: Change the adapter instantiation below

import type { ApiAdapter } from './apiAdapter';
import { MockApiAdapter } from './mockAdapter';
import { RealApiAdapter } from './realAdapter';

// ==========================================
// CONFIGURATION - CHANGE THIS TO SWITCH BETWEEN MOCK AND REAL API
// ==========================================

const USE_MOCK_API = true; // Set to false when backend is ready

// ==========================================
// Backend API Configuration
// Update this when your backend engineer provides the API details
// ==========================================

const BACKEND_CONFIG = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    // Add any custom headers here
  }
};

// ==========================================
// Create and export the API adapter instance
// ==========================================

let apiInstance: ApiAdapter;

if (USE_MOCK_API) {
  console.log('🔧 Using MOCK API adapter for development');
  apiInstance = new MockApiAdapter();
} else {
  console.log('🚀 Using REAL API adapter');
  apiInstance = new RealApiAdapter(BACKEND_CONFIG);
}

export const api = apiInstance;

// Export types for convenience
export * from './types';
export type { ApiAdapter } from './apiAdapter';
