/**
 * MSW Handlers para mock de APIs de Autenticação
 */

import { http, HttpResponse } from 'msw';
import {
  mockLogin,
  mockRefreshToken,
  mockUser,
  mockUsers,
} from '../../fixtures/auth';

const API_BASE_URL = 'http://localhost:8080/api/v1';

export const authHandlers = [
  // ========== LOGIN ==========

  // POST /auth/login - Login do usuário
  http.post(`${API_BASE_URL}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as { email?: string; password?: string };

    // Simula validação de credenciais
    if (!body.email || !body.password) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Email e senha são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (body.password === 'senha_errada') {
      return new HttpResponse(
        JSON.stringify({ detail: 'Credenciais inválidas' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(mockLogin, { status: 200 });
  }),

  // ========== LOGOUT ==========

  // POST /auth/logout - Logout do usuário
  http.post(`${API_BASE_URL}/auth/logout`, () => {
    return new HttpResponse(null, { status: 204 });
  }),

  // ========== REFRESH TOKEN ==========

  // POST /auth/refresh - Renovar token de acesso
  http.post(`${API_BASE_URL}/auth/refresh`, async ({ request }) => {
    const body = (await request.json()) as { refresh_token?: string };

    if (!body.refresh_token) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Refresh token é obrigatório' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (body.refresh_token === 'invalid_token') {
      return new HttpResponse(
        JSON.stringify({ detail: 'Refresh token inválido ou expirado' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(mockRefreshToken, { status: 200 });
  }),

  // ========== CURRENT USER ==========

  // GET /auth/me - Obter usuário atual
  http.get(`${API_BASE_URL}/auth/me`, ({ request }) => {
    const authHeader = request.headers.get('Authorization');

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Token de autenticação não fornecido' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const token = authHeader.replace('Bearer ', '');

    if (token === 'invalid_token' || token === 'expired_token') {
      return new HttpResponse(
        JSON.stringify({ detail: 'Token inválido ou expirado' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(mockUser, { status: 200 });
  }),

  // ========== USERS ==========

  // GET /users - Listar usuários
  http.get(`${API_BASE_URL}/users`, ({ request }) => {
    const url = new URL(request.url);
    const role = url.searchParams.get('role');
    const isActive = url.searchParams.get('is_active');

    let filtered = [...mockUsers];

    if (role) {
      filtered = filtered.filter((u) => u.role === role);
    }

    if (isActive !== null) {
      const active = isActive === 'true';
      filtered = filtered.filter((u) => u.is_active === active);
    }

    return HttpResponse.json(filtered, { status: 200 });
  }),

  // GET /users/:id - Obter usuário específico
  http.get(`${API_BASE_URL}/users/:id`, ({ params }) => {
    const { id } = params;
    const user = mockUsers.find((u) => u.id === id);

    if (!user) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Usuário não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(user, { status: 200 });
  }),

  // POST /users - Criar usuário
  http.post(`${API_BASE_URL}/users`, async ({ request }) => {
    const body = await request.json();
    const newUser = {
      ...mockUser,
      ...(body as Record<string, unknown>),
      id: `user-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(newUser, { status: 201 });
  }),

  // PUT /users/:id - Atualizar usuário
  http.put(`${API_BASE_URL}/users/:id`, async ({ params, request }) => {
    const { id } = params;
    const user = mockUsers.find((u) => u.id === id);

    if (!user) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Usuário não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const body = await request.json();
    const updated = {
      ...user,
      ...(body as Record<string, unknown>),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /users/:id - Deletar usuário
  http.delete(`${API_BASE_URL}/users/:id`, ({ params }) => {
    const { id } = params;
    const user = mockUsers.find((u) => u.id === id);

    if (!user) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Usuário não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return new HttpResponse(null, { status: 204 });
  }),

  // POST /auth/forgot-password - Esqueci minha senha
  http.post(`${API_BASE_URL}/auth/forgot-password`, async ({ request }) => {
    const body = (await request.json()) as { email?: string };

    if (!body.email) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Email é obrigatório' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(
      { message: 'Email de recuperação enviado com sucesso' },
      { status: 200 }
    );
  }),

  // POST /auth/reset-password - Redefinir senha
  http.post(`${API_BASE_URL}/auth/reset-password`, async ({ request }) => {
    const body = (await request.json()) as { token?: string; password?: string };

    if (!body.token || !body.password) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Token e nova senha são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (body.token === 'invalid_token') {
      return new HttpResponse(
        JSON.stringify({ detail: 'Token inválido ou expirado' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(
      { message: 'Senha redefinida com sucesso' },
      { status: 200 }
    );
  }),
];
