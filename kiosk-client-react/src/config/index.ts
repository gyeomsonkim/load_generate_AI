/**
 * Application Configuration
 */

import type { AppConfig } from '../types';

export const config: AppConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  apiPrefix: '/api/v1',
  defaultMapId: null,

  mapConfig: {
    minZoom: 0,
    maxZoom: 3,
  },

  markers: {
    start: {
      color: '#22c55e',
      label: '출발',
    },
    end: {
      color: '#ef4444',
      label: '도착',
    },
  },

  routeStyle: {
    color: '#3b82f6',
    weight: 4,
    opacity: 0.8,
    smoothFactor: 1,
  },

  debug: import.meta.env.DEV,
};

// API Endpoint helpers
export const API = {
  maps: {
    list: () => `${config.apiBaseUrl}${config.apiPrefix}/maps/`,
    get: (mapId: string) => `${config.apiBaseUrl}${config.apiPrefix}/maps/${mapId}`,
  },
  pathfinding: {
    route: () => `${config.apiBaseUrl}${config.apiPrefix}/pathfinding/route`,
  },
  files: (path: string) => `${config.apiBaseUrl}${path}`,
};
