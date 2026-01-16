export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: string;
  permissions: string[];
  created_at?: string;
  updated_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface AuthResponse {
  token: string;
  refresh_token: string;
  user: User;
  expires_in: number;
}

export interface RefreshResponse {
  token: string;
  expires_in: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User) => void;
}

export type AuthStore = AuthState & AuthActions;
