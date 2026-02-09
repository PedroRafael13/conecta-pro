/**
 * Fixtures de dados de teste para autenticação
 */

export interface UserResponse {
  id: string;
  email: string;
  nome: string;
  avatar_url?: string;
  role: string;
  permissions: string[];
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Mock de Usuário
export const mockUser: UserResponse = {
  id: 'user-001',
  email: 'admin@conecta.com',
  nome: 'Administrador',
  avatar_url: 'https://example.com/avatar.jpg',
  role: 'admin',
  permissions: ['read:all', 'write:all', 'delete:all'],
  is_active: true,
  last_login: '2026-02-05T10:00:00Z',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-02-05T10:00:00Z',
};

export const mockUsers: UserResponse[] = [
  mockUser,
  {
    ...mockUser,
    id: 'user-002',
    email: 'gerente@conecta.com',
    nome: 'Gerente',
    role: 'manager',
    permissions: ['read:all', 'write:all'],
  },
  {
    ...mockUser,
    id: 'user-003',
    email: 'operador@conecta.com',
    nome: 'Operador',
    role: 'operator',
    permissions: ['read:all'],
  },
];

// Mock de Login
export const mockLogin: LoginResponse = {
  access_token: 'mock-access-token-12345',
  refresh_token: 'mock-refresh-token-67890',
  token_type: 'bearer',
  expires_in: 3600,
  user: mockUser,
};

// Mock de Refresh Token
export const mockRefreshToken: RefreshTokenResponse = {
  access_token: 'new-access-token-12345',
  refresh_token: 'new-refresh-token-67890',
  token_type: 'bearer',
  expires_in: 3600,
};

// Helpers para criar dados customizados
export const createMockUser = (overrides?: Partial<UserResponse>): UserResponse => ({
  ...mockUser,
  ...overrides,
});

export const createMockLogin = (overrides?: Partial<LoginResponse>): LoginResponse => ({
  ...mockLogin,
  ...overrides,
});
