'use client';

import { Mail, Lock, AlertCircle, ArrowRight } from 'lucide-react';
import { Suspense, useState, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';

const OAUTH_ERROR_MESSAGES: Record<string, string> = {
  google_auth_failed: 'Falha na autenticacao com Google',
  no_code: 'Codigo de autorizacao nao recebido',
  missing_state: 'Parametro de seguranca ausente',
  invalid_state: 'Sessao expirada. Tente novamente',
  oauth_not_configured: 'Login com Google nao configurado',
  token_exchange_failed: 'Falha ao processar autenticacao',
  userinfo_failed: 'Falha ao obter dados do Google',
  no_email: 'Conta Google sem email associado',
  user_inactive: 'Usuario inativo. Contate o administrador',
  internal_error: 'Erro interno. Tente novamente',
  no_tokens: 'Falha ao receber tokens de autenticacao',
};

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // Erro vindo do OAuth redirect (derivado, sem setState em efeito)
  const oauthError = useMemo(() => {
    const code = searchParams.get('error');
    if (!code) return '';
    return OAUTH_ERROR_MESSAGES[code] ?? 'Erro na autenticacao';
  }, [searchParams]);

  const displayError = error || oauthError;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = await login({ email, password });

    if (result.success) {
      router.push('/dashboard');
    } else {
      setError(result.error || 'Erro ao fazer login');
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* ===== LEFT SIDE - Branding (desktop only) ===== */}
      <div className="hidden lg:flex lg:w-[55%] relative overflow-hidden bg-gradient-to-br from-navy-950 via-navy-900 to-navy-950">
        {/* Noise texture overlay */}
        <div className="noise absolute inset-0 z-10 pointer-events-none" />

        {/* Animated gradient orbs */}
        <div
          className="absolute top-[15%] left-[20%] w-80 h-80 rounded-full opacity-30 blur-3xl"
          style={{
            background: 'radial-gradient(circle, #1a47f5 0%, transparent 70%)',
            animation: 'float 6s ease-in-out infinite',
          }}
        />
        <div
          className="absolute bottom-[20%] right-[15%] w-96 h-96 rounded-full opacity-20 blur-3xl"
          style={{
            background: 'radial-gradient(circle, #f97707 0%, transparent 70%)',
            animation: 'float 8s ease-in-out infinite 2s',
          }}
        />
        <div
          className="absolute top-[60%] left-[50%] w-64 h-64 rounded-full opacity-15 blur-3xl"
          style={{
            background: 'radial-gradient(circle, #3366ff 0%, transparent 70%)',
            animation: 'float 7s ease-in-out infinite 1s',
          }}
        />

        {/* Floating geometric shapes */}
        <div
          className="absolute top-[12%] right-[18%] w-16 h-16 rounded-2xl border border-white/10 rotate-12"
          style={{ animation: 'float 5s ease-in-out infinite 0.5s' }}
        />
        <div
          className="absolute top-[35%] left-[10%] w-10 h-10 rounded-full border border-brand-500/20"
          style={{ animation: 'float 6s ease-in-out infinite 1.5s' }}
        />
        <div
          className="absolute bottom-[30%] left-[25%] w-20 h-20 rounded-3xl border border-white/5 -rotate-6"
          style={{ animation: 'float 7s ease-in-out infinite 0.8s' }}
        />
        <div
          className="absolute bottom-[15%] right-[30%] w-8 h-8 rounded-full border border-brand-400/15"
          style={{ animation: 'float 5s ease-in-out infinite 2.2s' }}
        />
        <div
          className="absolute top-[55%] right-[10%] w-14 h-14 rounded-2xl border border-navy-400/10 rotate-45"
          style={{ animation: 'float 8s ease-in-out infinite 3s' }}
        />

        {/* Grid pattern */}
        <div className="absolute inset-0 bg-grid opacity-[0.06]" />

        {/* Main content */}
        <div className="relative z-20 flex flex-col items-center justify-center w-full px-16">
          {/* Logo with glow */}
          <div className="relative mb-12">
            <div className="absolute inset-0 scale-150 blur-3xl opacity-20 bg-brand-500 rounded-full" />
            <Image
              src="/images/logo-transparent.png"
              alt="Conecta Mais"
              width={200}
              height={200}
              className="relative z-10 drop-shadow-2xl animate-pulse-slow"
              style={{ animationDuration: '4s' }}
              priority
            />
          </div>

          {/* Tagline */}
          <div className="text-center mb-14 max-w-lg">
            <p className="text-brand-400 text-sm font-semibold tracking-widest uppercase mb-4">
              Conecta PRO
            </p>
            <h1 className="text-4xl xl:text-5xl font-bold text-white leading-tight mb-4">
              Gestao inteligente para{' '}
              <span className="text-gradient">vigilancia patrimonial</span>
            </h1>
            <p className="text-navy-300/80 text-base leading-relaxed max-w-md mx-auto">
              Plataforma completa com controle operacional, financeiro e fiscal integrados em um so lugar.
            </p>
          </div>

          {/* Stats row */}
          <div className="flex items-center gap-0 bg-white/[0.04] backdrop-blur-sm rounded-2xl border border-white/[0.08] px-2 py-5">
            <div className="flex-1 text-center px-8">
              <p className="text-3xl font-bold text-white mb-1">500+</p>
              <p className="text-navy-400 text-xs font-medium tracking-wide uppercase">Colaboradores</p>
            </div>
            <div className="w-px h-10 bg-white/10" />
            <div className="flex-1 text-center px-8">
              <p className="text-3xl font-bold text-white mb-1">50+</p>
              <p className="text-navy-400 text-xs font-medium tracking-wide uppercase">Postos</p>
            </div>
            <div className="w-px h-10 bg-white/10" />
            <div className="flex-1 text-center px-8">
              <p className="text-3xl font-bold text-brand-400 mb-1">24/7</p>
              <p className="text-navy-400 text-xs font-medium tracking-wide uppercase">Monitoramento</p>
            </div>
          </div>

          {/* Footer */}
          <div className="absolute bottom-8 left-0 right-0 text-center text-navy-600 text-xs">
            <span>&copy; 2025 Jordan Santos de Jesus LTDA</span>
          </div>
        </div>

        {/* Corner decorative circles */}
        <div className="absolute -bottom-20 -right-20 w-72 h-72 rounded-full border border-navy-800/20" />
        <div className="absolute -bottom-10 -right-10 w-48 h-48 rounded-full border border-brand-500/10" />
        <div className="absolute -top-16 -left-16 w-56 h-56 rounded-full border border-navy-700/15" />
      </div>

      {/* ===== RIGHT SIDE - Form ===== */}
      {/* Mobile: full background with gradient */}
      <div className="flex-1 flex items-center justify-center relative lg:bg-[hsl(var(--background))]">
        {/* Mobile gradient background */}
        <div className="absolute inset-0 lg:hidden bg-gradient-to-br from-navy-950 via-navy-900 to-navy-950">
          <div className="noise absolute inset-0 pointer-events-none" />
          <div
            className="absolute top-[10%] left-[15%] w-64 h-64 rounded-full opacity-20 blur-3xl"
            style={{ background: 'radial-gradient(circle, #1a47f5 0%, transparent 70%)' }}
          />
          <div
            className="absolute bottom-[20%] right-[10%] w-48 h-48 rounded-full opacity-15 blur-3xl"
            style={{ background: 'radial-gradient(circle, #f97707 0%, transparent 70%)' }}
          />
        </div>

        <div className="relative z-10 w-full max-w-md px-6 py-12 lg:px-10">
          {/* Mobile: glass card wrapper */}
          <div className="lg:bg-transparent lg:border-0 lg:shadow-none lg:backdrop-blur-none glass rounded-3xl p-8 lg:p-0 lg:rounded-none">
            {/* Logo mobile */}
            <div className="lg:hidden flex justify-center mb-8">
              <div className="relative">
                <div className="absolute inset-0 scale-150 blur-2xl opacity-20 bg-brand-500 rounded-full" />
                <Image
                  src="/images/logo-transparent.png"
                  alt="Conecta Mais"
                  width={120}
                  height={120}
                  className="relative z-10 animate-pulse-slow"
                  style={{ animationDuration: '4s' }}
                />
              </div>
            </div>

            {/* Staggered form content */}
            <div className="stagger">
              {/* Header */}
              <div className="text-center lg:text-left mb-8 animate-slide-up">
                <h2 className="text-2xl font-bold text-white lg:text-[hsl(var(--foreground))]">
                  Bem-vindo de volta
                </h2>
                <p className="text-navy-300 lg:text-[hsl(var(--muted-foreground))] mt-2 text-sm">
                  Entre com suas credenciais para acessar o sistema
                </p>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-5 animate-slide-up">
                {/* Erro */}
                {displayError && (
                  <div className="flex items-center gap-2 p-3 rounded-xl bg-[hsl(var(--destructive))]/10 border border-[hsl(var(--destructive))]/30 text-[hsl(var(--destructive))] animate-slide-up">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span className="text-sm">{displayError}</span>
                  </div>
                )}

                {/* Email */}
                <Input
                  type="email"
                  label="E-mail"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  icon={<Mail className="w-4 h-4" />}
                  className="!h-12 !rounded-xl !bg-white/[0.06] lg:!bg-[hsl(var(--input))]"
                  required
                  autoFocus
                />

                {/* Senha */}
                <Input
                  type="password"
                  label="Senha"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  icon={<Lock className="w-4 h-4" />}
                  className="!h-12 !rounded-xl !bg-white/[0.06] lg:!bg-[hsl(var(--input))]"
                  required
                />

                {/* Lembrar e esqueci */}
                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      className="w-4 h-4 rounded border-[hsl(var(--border))] bg-[hsl(var(--input))] text-navy-600 focus:ring-navy-600 focus:ring-offset-0"
                    />
                    <span className="text-navy-300 lg:text-[hsl(var(--muted-foreground))] group-hover:text-white lg:group-hover:text-[hsl(var(--foreground))] transition-colors">
                      Lembrar-me
                    </span>
                  </label>
                  <Link
                    href="/forgot-password"
                    className="text-brand-400 hover:text-brand-300 transition-colors"
                  >
                    Esqueci a senha
                  </Link>
                </div>

                {/* Botao de login */}
                <Button
                  type="submit"
                  className="w-full btn-brand !h-12 !rounded-xl !text-base !font-semibold group"
                  size="lg"
                  isLoading={isLoading}
                >
                  Entrar
                  <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </Button>
              </form>

              {/* Separador "ou" */}
              <div className="relative my-6 animate-slide-up">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/10 lg:border-[hsl(var(--border))]" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-3 bg-transparent text-navy-400 lg:bg-[hsl(var(--background))] lg:text-[hsl(var(--muted-foreground))]">
                    ou continue com
                  </span>
                </div>
              </div>

              {/* Google OAuth */}
              <a
                href="/api/v1/auth/google"
                className="animate-slide-up w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl border border-white/10 lg:border-[hsl(var(--border))] bg-white/[0.04] lg:bg-transparent hover:bg-white/[0.08] lg:hover:bg-[hsl(var(--accent))]/10 transition-all text-navy-200 lg:text-[hsl(var(--muted-foreground))] hover:text-white lg:hover:text-[hsl(var(--foreground))] font-medium text-sm"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Entrar com Google
              </a>

              {/* Version footer */}
              <p className="animate-slide-up text-center text-[10px] text-navy-600 lg:text-[hsl(var(--muted-foreground))]/40 mt-8">
                Conecta PRO v2.0.0
              </p>

              {/* Terms footer */}
              <p className="animate-slide-up text-center text-xs text-navy-400 lg:text-[hsl(var(--muted-foreground))] mt-3">
                Ao entrar, voce concorda com os{' '}
                <a href="#" className="text-brand-400 hover:underline">
                  Termos de Uso
                </a>{' '}
                e{' '}
                <a href="#" className="text-brand-400 hover:underline">
                  Politica de Privacidade
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginContent />
    </Suspense>
  );
}
