import http from 'k6/http';
import { check, sleep } from 'k6';

// Use BASE_URL if provided; default to local dev
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  vus: 100,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'], // less than 1% errors
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/health`);
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
