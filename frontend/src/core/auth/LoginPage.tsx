import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Eye, EyeOff, Loader2, Mail, Lock } from 'lucide-react';
import { useAuth } from './useAuth';

const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email e obrigatorio')
    .email('Email invalido'),
  password: z
    .string()
    .min(1, 'Senha e obrigatoria')
    .min(6, 'Senha deve ter no minimo 6 caracteres'),
  remember_me: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading, error, clearError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const from = (location.state as { from?: { pathname: string } })?.from
    ?.pathname || '/dashboard';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      remember_me: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearError();
      await login(data);
      navigate(from, { replace: true });
    } catch {
      // Error is handled by the store
    }
  };

  return (
    <div className="min-h-screen bg-conecta-gradient flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center shadow-lg">
              <svg className="w-8 h-8" viewBox="0 0 32 32">
                <path
                  d="M6 16L12 22L26 8"
                  stroke="#FF6B35"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              </svg>
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold text-white">
                CONECTA <span className="text-conecta-laranja">PRO</span>
              </h1>
              <p className="text-xs text-gray-300">By Conecta Mais</p>
            </div>
          </div>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-xl shadow-2xl p-8">
          <div className="text-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Bem-vindo de volta
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Entre com suas credenciais para acessar
            </p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg"
            >
              <p className="text-sm text-red-600">{error}</p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Email */}
            <div>
              <label htmlFor="email" className="label">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('email')}
                  id="email"
                  type="email"
                  autoComplete="email"
                  className={`input pl-10 ${
                    errors.email ? 'input-error' : ''
                  }`}
                  placeholder="seu@email.com"
                />
              </div>
              {errors.email && (
                <p className="error-text">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="label">
                Senha
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('password')}
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  className={`input pl-10 pr-10 ${
                    errors.password ? 'input-error' : ''
                  }`}
                  placeholder="********"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="error-text">{errors.password.message}</p>
              )}
            </div>

            {/* Remember me & Forgot password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  {...register('remember_me')}
                  type="checkbox"
                  className="w-4 h-4 text-conecta-laranja border-gray-300 rounded focus:ring-conecta-laranja"
                />
                <span className="text-sm text-gray-600">Lembrar-me</span>
              </label>
              <a
                href="/forgot-password"
                className="text-sm text-conecta-escuro hover:text-conecta-medio font-medium"
              >
                Esqueceu a senha?
              </a>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-3 text-base"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-gray-300 mt-6">
          2024 Conecta PRO. Todos os direitos reservados.
        </p>
      </motion.div>
    </div>
  );
}

export default LoginPage;
