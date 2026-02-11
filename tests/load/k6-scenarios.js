/**
 * Load Testing Scenarios - ERP Conecta Mais
 * ==========================================
 * Ferramenta: k6 v0.49.0
 * Executar: k6 run tests/load/k6-scenarios.js
 *
 * Cenários:
 * 1. health - Health check baseline (constante)
 * 2. login - Simulação de login (ramping)
 * 3. api_reads - Leituras de API/dashboard (arrival rate)
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// URL base configurável via env
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

// Métricas customizadas
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

// Opções de configuração
export const options = {
  scenarios: {
    // Cenário 1: Health check (baseline constante)
    health: {
      executor: 'constant-vus',
      vus: 10,
      duration: '2m',
      exec: 'healthCheck',
      tags: { scenario: 'health' },
    },

    // Cenário 2: Login flow (ramping de carga)
    login: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 20 },   // Ramp up
        { duration: '2m', target: 50 },    // Carga sustentada
        { duration: '30s', target: 0 },    // Ramp down
      ],
      exec: 'loginFlow',
      startTime: '2m',  // Inicia após health baseline
      tags: { scenario: 'login' },
    },

    // Cenário 3: API reads (taxa de chegada constante)
    api_reads: {
      executor: 'constant-arrival-rate',
      rate: 30,           // 30 iterações por segundo
      timeUnit: '1s',
      duration: '3m',
      preAllocatedVUs: 20,
      maxVUs: 100,
      exec: 'apiReads',
      startTime: '5m',    // Inicia após login
      tags: { scenario: 'api_reads' },
    },

    // Cenário 4: Smoke test (rápido, para validação)
    smoke: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      exec: 'smokeTest',
      tags: { scenario: 'smoke' },
    },
  },

  // Thresholds de qualidade
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95% < 500ms, 99% < 1s
    http_req_failed: ['rate<0.01'],                   // Error rate < 1%
    errors: ['rate<0.05'],                            // Métrica custom < 5%
  },

  // Tags globais
  tags: {
    project: 'erp-conecta-mais',
    environment: __ENV.ENV || 'staging',
  },
};

/**
 * Health Check - Verificação básica de saúde
 */
export function healthCheck() {
  const res = http.get(`${BASE_URL}/health`);

  const success = check(res, {
    'health status 200': (r) => r.status === 200,
    'health response time < 200ms': (r) => r.timings.duration < 200,
    'health response valid': (r) => r.json('status') === 'healthy',
  });

  errorRate.add(!success);
  responseTime.add(res.timings.duration);

  sleep(1);
}

/**
 * Login Flow - Simula tentativas de login
 */
export function loginFlow() {
  const payload = JSON.stringify({
    email: 'loadtest@conectamais.pro',
    password: __ENV.LOAD_TEST_PASSWORD || 'LoadTest2024!',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(`${BASE_URL}/api/v1/auth/login`, payload, params);

  // Aceita 200 (sucesso) ou 401 (credenciais inválidas) - ambos são respostas válidas
  const success = check(res, {
    'login status válido': (r) => [200, 401].includes(r.status),
    'login response time < 500ms': (r) => r.timings.duration < 500,
  });

  errorRate.add(!success);
  responseTime.add(res.timings.duration);

  sleep(1);
}

/**
 * API Reads - Leituras de endpoints de API
 */
export function apiReads() {
  const endpoints = [
    '/api/v1/health/detailed',
    '/api/v1/tenants',
    '/docs',
  ];

  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const res = http.get(`${BASE_URL}${endpoint}`);

  const success = check(res, {
    'api status not 500': (r) => r.status !== 500,
    'api status not 503': (r) => r.status !== 503,
    'api response time < 500ms': (r) => r.timings.duration < 500,
  });

  errorRate.add(!success);
  responseTime.add(res.timings.duration);

  sleep(0.5);
}

/**
 * Smoke Test - Teste rápido de fumaça
 */
export function smokeTest() {
  // Testa health
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'smoke: health 200': (r) => r.status === 200,
  });

  // Testa docs
  const docsRes = http.get(`${BASE_URL}/docs`);
  check(docsRes, {
    'smoke: docs acessível': (r) => r.status === 200,
  });

  sleep(0.5);
}

/**
 * Setup inicial - executado uma vez antes dos testes
 */
export function setup() {
  console.log(`Iniciando load test contra: ${BASE_URL}`);
  console.log(`Ambiente: ${__ENV.ENV || 'staging'}`);

  // Verifica se a aplicação está respondendo
  const res = http.get(`${BASE_URL}/health`);
  if (res.status !== 200) {
    console.error(`ERRO: Aplicação não está respondendo em ${BASE_URL}`);
    return { valid: false };
  }

  console.log('✓ Aplicação respondendo, iniciando testes...');
  return { valid: true };
}

/**
 * Teardown - executado uma vez após os testes
 */
export function teardown(data) {
  if (data.valid) {
    console.log('✓ Load test concluído com sucesso');
  } else {
    console.log('✗ Load test abortado - aplicação indisponível');
  }
}
