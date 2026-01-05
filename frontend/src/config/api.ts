/**
 * API configuration that works in both development and production
 * 
 * In production (CloudFront): Uses relative paths since CloudFront proxies to backend
 * In development: Uses localhost:8000 or VITE_API_BASE_URL if set
 */

export function getApiBaseUrl(): string {
  // Check if we have an explicit override via environment variable
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl) {
    return envUrl;
  }

  // In production, use relative path (CloudFront proxies /api/* to backend)
  if (import.meta.env.PROD) {
    return '/api/v1';
  }

  // In development, connect to local backend
  return 'http://localhost:8000/api/v1';
}

export function getWebSocketUrl(): string {
  // Check if we have an explicit override via environment variable
  const envUrl = import.meta.env.VITE_WS_URL;
  if (envUrl) {
    return envUrl;
  }

  // In production, use current host with wss:// (CloudFront proxies /ws/* to backend)
  if (import.meta.env.PROD) {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    return `${protocol}://${window.location.host}/ws/market`;
  }

  // In development, connect to local backend
  return 'ws://localhost:8000/ws/market';
}

