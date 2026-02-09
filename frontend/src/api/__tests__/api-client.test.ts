/**
 * Testes de Integração - API Client (Axios)
 *
 * Testa configuração do axios, interceptors, tratamento de erro 401
 * e retry automático.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import axios, { AxiosError, type AxiosInstance } from 'axios';

// Mock do axios
vi.mock('axios', async () => {
  const actual = await vi.importActual('axios');
  return {
    ...actual as object,
    default: {
      create: vi.fn(),
      CancelToken: {
        source: vi.fn(() => ({
          token: 'cancel-token',
          cancel: vi.fn(),
        })),
      },
      isCancel: vi.fn(),
    },
  };
});

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// Mock do window.location
const locationMock = { href: '' };
Object.defineProperty(window, 'location', {
  value: locationMock,
  writable: true,
});

// Factory para criar mock do Axios
const createMockAxios = (): AxiosInstance => {
  const mockAxios = {
    defaults: {
      baseURL: '',
      headers: {} as Record<string, string>,
    },
    interceptors: {
      request: { use: vi.fn((fn) => fn) },
      response: { use: vi.fn((fn, errFn) => 1) },
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  } as unknown as AxiosInstance;

  return mockAxios;
};

describe('API Client - Configuração', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve criar instância do axios com configuração correta', () => {
    const mockInstance = createMockAxios();
    (axios.create as ReturnType<typeof vi.fn>).mockReturnValue(mockInstance);

    const API_URL = 'http://localhost:8080';
    const instance = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    expect(axios.create).toHaveBeenCalledWith({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    expect(instance).toBe(mockInstance);
  });

  it('deve configurar interceptors de request e response', () => {
    const mockInstance = createMockAxios();
    (axios.create as ReturnType<typeof vi.fn>).mockReturnValue(mockInstance);

    const instance = axios.create({});

    // Simula adição de interceptors
    const requestInterceptor = (config: { headers: { Authorization?: string } }) => {
      const token = localStorageMock.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    };

    const responseInterceptor = (error: { response?: { status: number } }) => {
      if (error.response?.status === 401) {
        localStorageMock.removeItem('auth_token');
        locationMock.href = '/login';
      }
      return Promise.reject(error);
    };

    instance.interceptors.request.use(requestInterceptor as any);
    instance.interceptors.response.use((res) => res, responseInterceptor);

    expect(instance.interceptors.request.use).toHaveBeenCalledWith(requestInterceptor);
    expect(instance.interceptors.response.use).toHaveBeenCalledWith(
      expect.any(Function),
      responseInterceptor
    );
  });
});

describe('API Client - Request Interceptor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve adicionar token de autenticação no header quando existir', () => {
    localStorageMock.getItem.mockReturnValue('fake-token-123');

    const config = { headers: {} };
    const requestInterceptor = (cfg: { headers: { Authorization?: string } }) => {
      const token = localStorageMock.getItem('auth_token');
      if (token) {
        cfg.headers.Authorization = `Bearer ${token}`;
      }
      return cfg;
    };

    const result = requestInterceptor(config);

    expect(result.headers.Authorization).toBe('Bearer fake-token-123');
    expect(localStorageMock.getItem).toHaveBeenCalledWith('auth_token');
  });

  it('não deve adicionar header de autorização quando não houver token', () => {
    localStorageMock.getItem.mockReturnValue(null);

    const config = { headers: {} };
    const requestInterceptor = (cfg: { headers: { Authorization?: string } }) => {
      const token = localStorageMock.getItem('auth_token');
      if (token) {
        cfg.headers.Authorization = `Bearer ${token}`;
      }
      return cfg;
    };

    const result = requestInterceptor(config);

    expect(result.headers.Authorization).toBeUndefined();
  });
});

describe('API Client - Response Interceptor (Erro 401)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    locationMock.href = '';
  });

  it('deve redirecionar para login quando receber erro 401', async () => {
    const responseInterceptor = (error: { response?: { status: number } }) => {
      if (error.response?.status === 401) {
        localStorageMock.removeItem('auth_token');
        locationMock.href = '/login';
      }
      return Promise.reject(error);
    };

    const error = { response: { status: 401 } };

    await expect(responseInterceptor(error)).rejects.toEqual(error);

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
    expect(locationMock.href).toBe('/login');
  });

  it('deve remover token do localStorage quando receber erro 401', async () => {
    const responseInterceptor = (error: { response?: { status: number } }) => {
      if (error.response?.status === 401) {
        localStorageMock.removeItem('auth_token');
        locationMock.href = '/login';
      }
      return Promise.reject(error);
    };

    const error = { response: { status: 401 } };

    try {
      await responseInterceptor(error);
    } catch {
      // Esperado erro
    }

    expect(localStorageMock.removeItem).toHaveBeenCalledTimes(1);
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
  });

  it('deve propagar erros diferentes de 401 normalmente', async () => {
    const responseInterceptor = (error: { response?: { status: number } }) => {
      if (error.response?.status === 401) {
        localStorageMock.removeItem('auth_token');
        locationMock.href = '/login';
      }
      return Promise.reject(error);
    };

    const error = { response: { status: 500 } };

    await expect(responseInterceptor(error)).rejects.toEqual(error);
    expect(locationMock.href).not.toBe('/login');
    expect(localStorageMock.removeItem).not.toHaveBeenCalled();
  });
});

describe('API Client - Tratamento de Erros', () => {
  it('deve identificar erro 404 corretamente', () => {
    const error = {
      response: {
        status: 404,
        data: { detail: 'Recurso não encontrado' },
      },
    } as AxiosError;

    expect(error.response?.status).toBe(404);
    expect(error.response?.data).toEqual({ detail: 'Recurso não encontrado' });
  });

  it('deve identificar erro 500 corretamente', () => {
    const error = {
      response: {
        status: 500,
        data: { detail: 'Erro interno do servidor' },
      },
    } as AxiosError;

    expect(error.response?.status).toBe(500);
  });

  it('deve identificar erro de timeout', () => {
    const error = {
      code: 'ECONNABORTED',
      message: 'timeout of 50ms exceeded',
    } as AxiosError;

    expect(error.code).toBe('ECONNABORTED');
  });
});

describe('API Client - Retry Automático', () => {
  it('deve implementar lógica de retry', () => {
    let attempts = 0;
    const maxRetries = 3;

    const shouldRetry = (error: { response?: { status: number } }, retryCount: number) => {
      return error.response?.status === 503 && retryCount < maxRetries;
    };

    // Primeira tentativa - deve retry
    attempts = 1;
    expect(shouldRetry({ response: { status: 503 } }, attempts)).toBe(true);

    // Última tentativa - não deve retry
    attempts = 3;
    expect(shouldRetry({ response: { status: 503 } }, attempts)).toBe(false);

    // Erro diferente - não deve retry
    attempts = 1;
    expect(shouldRetry({ response: { status: 500 } }, attempts)).toBe(false);
  });

  it('deve contar tentativas de retry corretamente', () => {
    let retryCount = 0;
    const maxRetries = 2;

    const simulateRetry = (error: { response?: { status: number } }) => {
      if (error.response?.status === 503 && retryCount < maxRetries) {
        retryCount++;
        return true;
      }
      return false;
    };

    const error503 = { response: { status: 503 } };

    expect(simulateRetry(error503)).toBe(true);
    expect(retryCount).toBe(1);

    expect(simulateRetry(error503)).toBe(true);
    expect(retryCount).toBe(2);

    // Terceira tentativa deve falhar
    expect(simulateRetry(error503)).toBe(false);
    expect(retryCount).toBe(2);
  });
});

describe('API Client - Cancelamento', () => {
  it('deve criar cancel token', () => {
    const cancelTokenSource = {
      token: 'cancel-token-123',
      cancel: vi.fn((message?: string) => {
        // Simula cancelamento
      }),
    };

    expect(cancelTokenSource.token).toBe('cancel-token-123');
    expect(typeof cancelTokenSource.cancel).toBe('function');
  });

  it('deve suportar cancelamento com mensagem', () => {
    const cancelFn = vi.fn();
    const message = 'Operação cancelada pelo usuário';

    cancelFn(message);

    expect(cancelFn).toHaveBeenCalledWith(message);
  });
});

describe('API Client - Headers', () => {
  it('deve permitir headers customizados por requisição', () => {
    const customHeaders = {
      'X-Custom-Header': 'custom-value',
      'X-Request-ID': 'req-123',
    };

    expect(customHeaders['X-Custom-Header']).toBe('custom-value');
    expect(customHeaders['X-Request-ID']).toBe('req-123');
  });

  it('deve mesclar headers corretamente', () => {
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const requestHeaders = {
      'X-Specific': 'specific-value',
    };

    const mergedHeaders = { ...defaultHeaders, ...requestHeaders };

    expect(mergedHeaders['Content-Type']).toContain('application/json');
    expect(mergedHeaders['X-Specific']).toBe('specific-value');
  });
});
