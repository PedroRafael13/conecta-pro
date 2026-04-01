/**
 * Testes de Integração - Auth API
 *
 * Testa endpoints de autenticação:
 * - Login
 * - Logout
 * - Refresh Token
 * - Get Current User
 */

import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import axios from 'axios';
import { authHandlers } from '@/test/mocks/handlers/auth';
import { server } from '@/test/mocks/server';
import {
  mockLogin,
  mockRefreshToken,
  mockUser,
  mockUsers,
} from '@/test/fixtures/auth';

// Configura axios para testes
const API_URL = 'http://localhost:8080/api/v1';
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

describe('Auth API - Login', () => {
  beforeAll(() => {
    server.use(...authHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve fazer login com credenciais válidas', async () => {
    const credentials = {
      email: 'admin@conecta.com',
      password: 'senha123',
    };

    const response = await apiClient.post('/auth/login', credentials);

    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('access_token');
    expect(response.data).toHaveProperty('refresh_token');
    expect(response.data).toHaveProperty('user');
    expect(response.data.user.email).toBe(mockLogin.user.email);
    expect(response.data.token_type).toBe('bearer');
    expect(response.data.expires_in).toBeGreaterThan(0);
  });

  it('deve retornar erro 401 com credenciais inválidas', async () => {
    const credentials = {
      email: 'admin@conecta.com',
      password: 'senha_errada',
    };

    try {
      await apiClient.post('/auth/login', credentials);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(401);
        expect(error.response?.data.detail).toBe('Credenciais inválidas');
      }
    }
  });

  it('deve retornar erro 400 quando email não for fornecido', async () => {
    const credentials = {
      password: 'senha123',
    };

    try {
      await apiClient.post('/auth/login', credentials);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(400);
        expect(error.response?.data.detail).toContain('Email e senha são obrigatórios');
      }
    }
  });

  it('deve retornar erro 400 quando senha não for fornecida', async () => {
    const credentials = {
      email: 'admin@conecta.com',
    };

    try {
      await apiClient.post('/auth/login', credentials);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(400);
        expect(error.response?.data.detail).toContain('Email e senha são obrigatórios');
      }
    }
  });
});

describe('Auth API - Logout', () => {
  beforeAll(() => {
    server.use(...authHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve fazer logout com sucesso', async () => {
    const response = await apiClient.post('/auth/logout');

    expect(response.status).toBe(204);
  });

  it('deve aceitar token no header durante logout', async () => {
    const response = await apiClient.post(
      '/auth/logout',
      {},
      {
        headers: {
          Authorization: 'Bearer fake-token',
        },
      }
    );

    expect(response.status).toBe(204);
  });
});

describe('Auth API - Refresh Token', () => {
  beforeAll(() => {
    server.use(...authHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve renovar token de acesso com refresh token válido', async () => {
    const refreshData = {
      refresh_token: 'valid-refresh-token',
    };

    const response = await apiClient.post('/auth/refresh', refreshData);

    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('access_token');
    expect(response.data).toHaveProperty('refresh_token');
    expect(response.data.access_token).not.toBe(refreshData.refresh_token);
    expect(response.data.token_type).toBe('bearer');
  });

  it('deve retornar erro 400 quando refresh token não for fornecido', async () => {
    try {
      await apiClient.post('/auth/refresh', {});
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(400);
        expect(error.response?.data.detail).toContain('Refresh token é obrigatório');
      }
    }
  });

  it('deve retornar erro 401 com refresh token inválido', async () => {
    const refreshData = {
      refresh_token: 'invalid_token',
    };

    try {
      await apiClient.post('/auth/refresh', refreshData);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(401);
        expect(error.response?.data.detail).toContain('inválido ou expirado');
      }
    }
  });
});

describe('Auth API - Get Current User', () => {
  beforeAll(() => {
    server.use(...authHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve retornar usuário atual com token válido', async () => {
    const response = await apiClient.get('/auth/me', {
      headers: {
        Authorization: 'Bearer valid-token',
      },
    });

    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('id');
    expect(response.data).toHaveProperty('email');
    expect(response.data).toHaveProperty('nome');
    expect(response.data).toHaveProperty('role');
    expect(response.data).toHaveProperty('permissions');
    expect(response.data.email).toBe(mockUser.email);
  });

  it('deve retornar erro 401 quando não houver token', async () => {
    try {
      await apiClient.get('/auth/me');
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(401);
        expect(error.response?.data.detail).toContain('Token de autenticação não fornecido');
      }
    }
  });

  it('deve retornar erro 401 com token inválido', async () => {
    try {
      await apiClient.get('/auth/me', {
        headers: {
          Authorization: 'Bearer invalid_token',
        },
      });
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(401);
        expect(error.response?.data.detail).toContain('Token inválido ou expirado');
      }
    }
  });

  it('deve retornar erro 401 com token expirado', async () => {
    try {
      await apiClient.get('/auth/me', {
        headers: {
          Authorization: 'Bearer expired_token',
        },
      });
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(401);
        expect(error.response?.data.detail).toContain('Token inválido ou expirado');
      }
    }
  });

  it('deve retornar erro 401 com formato de token inválido', async () => {
    try {
      await apiClient.get('/auth/me', {
        headers: {
          Authorization: 'InvalidFormat token',
        },
      });
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(401);
      }
    }
  });
});

describe('Auth API - Gerenciamento de Usuários', () => {
  beforeAll(() => {
    server.use(...authHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  describe('Listar Usuários', () => {
    it('deve listar todos os usuários', async () => {
      const response = await apiClient.get('/users');

      expect(response.status).toBe(200);
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBe(mockUsers.length);
    });

    it('deve filtrar usuários por role', async () => {
      const response = await apiClient.get('/users?role=admin');

      expect(response.status).toBe(200);
      expect(response.data.every((u: typeof mockUser) => u.role === 'admin')).toBe(true);
    });

    it('deve filtrar usuários por status ativo', async () => {
      const response = await apiClient.get('/users?is_active=true');

      expect(response.status).toBe(200);
      expect(response.data.every((u: typeof mockUser) => u.is_active === true)).toBe(true);
    });
  });

  describe('Obter Usuário', () => {
    it('deve obter usuário por ID', async () => {
      const response = await apiClient.get('/users/user-001');

      expect(response.status).toBe(200);
      expect(response.data.id).toBe('user-001');
      expect(response.data.email).toBe(mockUser.email);
    });

    it('deve retornar erro 404 para usuário inexistente', async () => {
      try {
        await apiClient.get('/users/user-inexistente');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
          expect(error.response?.data.detail).toContain('Usuário não encontrado');
        }
      }
    });
  });

  describe('Criar Usuário', () => {
    it('deve criar novo usuário', async () => {
      const newUser = {
        email: 'novo@conecta.com',
        nome: 'Novo Usuário',
        role: 'operator',
        permissions: ['read:all'],
        is_active: true,
      };

      const response = await apiClient.post('/users', newUser);

      expect(response.status).toBe(201);
      expect(response.data.email).toBe(newUser.email);
      expect(response.data.nome).toBe(newUser.nome);
      expect(response.data).toHaveProperty('id');
      expect(response.data).toHaveProperty('created_at');
    });
  });

  describe('Atualizar Usuário', () => {
    it('deve atualizar usuário existente', async () => {
      const updateData = {
        nome: 'Nome Atualizado',
      };

      const response = await apiClient.put('/users/user-001', updateData);

      expect(response.status).toBe(200);
      expect(response.data.nome).toBe(updateData.nome);
      expect(response.data).toHaveProperty('updated_at');
    });

    it('deve retornar erro 404 ao atualizar usuário inexistente', async () => {
      try {
        await apiClient.put('/users/user-inexistente', { nome: 'Test' });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });

  describe('Deletar Usuário', () => {
    it('deve deletar usuário existente', async () => {
      const response = await apiClient.delete('/users/user-001');

      expect(response.status).toBe(204);
    });

    it('deve retornar erro 404 ao deletar usuário inexistente', async () => {
      try {
        await apiClient.delete('/users/user-inexistente');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });
});

describe('Auth API - Recuperação de Senha', () => {
  beforeAll(() => {
    server.use(...authHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  describe('Esqueci Minha Senha', () => {
    it('deve enviar email de recuperação', async () => {
      const response = await apiClient.post('/auth/forgot-password', {
        email: 'usuario@conecta.com',
      });

      expect(response.status).toBe(200);
      expect(response.data.message).toContain('Email de recuperação enviado');
    });

    it('deve retornar erro 400 quando email não for fornecido', async () => {
      try {
        await apiClient.post('/auth/forgot-password', {});
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
          expect(error.response?.data.detail).toContain('Email é obrigatório');
        }
      }
    });
  });

  describe('Redefinir Senha', () => {
    it('deve redefinir senha com token válido', async () => {
      const response = await apiClient.post('/auth/reset-password', {
        token: 'valid-token',
        password: 'novaSenha123',
      });

      expect(response.status).toBe(200);
      expect(response.data.message).toContain('Senha redefinida com sucesso');
    });

    it('deve retornar erro 400 quando token não for fornecido', async () => {
      try {
        await apiClient.post('/auth/reset-password', { password: 'novaSenha' });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
        }
      }
    });

    it('deve retornar erro 400 quando senha não for fornecida', async () => {
      try {
        await apiClient.post('/auth/reset-password', { token: 'valid-token' });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
        }
      }
    });

    it('deve retornar erro 400 com token inválido', async () => {
      try {
        await apiClient.post('/auth/reset-password', {
          token: 'invalid_token',
          password: 'novaSenha',
        });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
          expect(error.response?.data.detail).toContain('Token inválido ou expirado');
        }
      }
    });
  });
});
