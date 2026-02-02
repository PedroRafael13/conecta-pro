'use client';

import { Mail, Lock, AlertCircle, ArrowRight, Shield, FileText, Wallet, Smartphone } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
;
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

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

  const features = [
    { icon: Shield, label: 'Escalas e Postos', desc: 'Gestão completa de escalas' },
    { icon: FileText, label: 'NFS-e e eSocial', desc: 'Conformidade fiscal' },
    { icon: Wallet, label: 'Fluxo de Caixa', desc: 'Controle financeiro' },
    { icon: Smartphone, label: 'App Mobile', desc: 'Acesso em qualquer lugar' },
  ];

  return (
    <div className="min-h-screen flex">
      {/* Lado esquerdo - Branding (dividido em duas seções) */}
      <div className="hidden lg:flex lg:w-1/2 flex-col">
        {/* Seção superior - Fundo branco com logo */}
        <div className="h-2/5 bg-white flex items-center justify-center p-8 relative">
          {/* Sombra sutil na divisão */}
          <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />

          <div className="text-center">
            <Image
              src="/images/logo-original.png"
              alt="Conecta Mais"
              width={220}
              height={220}
              className="mx-auto drop-shadow-sm"
              priority
            />
          </div>
        </div>

        {/* Seção inferior - Fundo azul com texto */}
        <div className="h-3/5 bg-gradient-to-br from-navy-900 via-navy-950 to-navy-900 relative overflow-hidden">
          {/* Background pattern */}
          <div className="absolute inset-0 bg-grid opacity-20" />

          {/* Glow decorativo */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-32 bg-brand-500/10 blur-3xl" />
          <div className="absolute bottom-0 right-0 w-64 h-64 bg-brand-500/5 blur-3xl rounded-full" />

          {/* Conteúdo */}
          <div className="relative z-10 h-full flex flex-col justify-between p-10">
            {/* Texto principal */}
            <div className="space-y-4 pt-4">
              <p className="text-brand-400 text-sm font-semibold tracking-wider uppercase">
                Sistema Conecta Mais
              </p>
              <h2 className="text-3xl font-bold text-white leading-tight">
                Gestão inteligente para<br />
                <span className="text-brand-400">vigilância patrimonial</span>
              </h2>
              <p className="text-navy-300 text-base max-w-sm leading-relaxed">
                Plataforma completa com controle operacional, financeiro e fiscal
                integrados em um só lugar.
              </p>
            </div>

            {/* Features em grid */}
            <div className="grid grid-cols-2 gap-3 py-4">
              {features.map((feature) => (
                <div
                  key={feature.label}
                  className="flex items-center gap-3 p-3 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-colors"
                >
                  <div className="w-9 h-9 rounded-lg bg-brand-500/20 flex items-center justify-center">
                    <feature.icon className="w-4 h-4 text-brand-400" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">{feature.label}</p>
                    <p className="text-navy-400 text-xs">{feature.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between text-navy-500 text-xs">
              <span>© 2025 Jordan Santos de Jesus LTDA</span>
              <span>Conecta PRO v2.0</span>
            </div>
          </div>

          {/* Elementos decorativos */}
          <div className="absolute -bottom-16 -right-16 w-64 h-64 rounded-full border border-navy-800/30" />
          <div className="absolute -bottom-8 -right-8 w-40 h-40 rounded-full border border-brand-500/10" />
        </div>
      </div>

      {/* Lado direito - Form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-[hsl(var(--background))]">
        <div className="w-full max-w-md animate-fade-in">
          {/* Logo mobile */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex flex-col items-center gap-3">
              <Image
                src="/images/logo-original.png"
                alt="Conecta Mais"
                width={140}
                height={140}
              />
              <p className="text-brand-500 text-sm font-medium">Sistema de Gestão</p>
            </div>
          </div>

          {/* Header */}
          <div className="text-center lg:text-left mb-8">
            <h2 className="text-2xl font-bold text-[hsl(var(--foreground))]">
              Bem-vindo de volta
            </h2>
            <p className="text-[hsl(var(--muted-foreground))] mt-1">
              Entre com suas credenciais para acessar o sistema
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Erro */}
            {error && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-[hsl(var(--destructive))]/10 border border-[hsl(var(--destructive))]/30 text-[hsl(var(--destructive))] animate-slide-up">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span className="text-sm">{error}</span>
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
              required
            />

            {/* Lembrar e esqueci */}
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-[hsl(var(--border))] bg-[hsl(var(--input))] text-navy-600 focus:ring-navy-600 focus:ring-offset-0"
                />
                <span className="text-[hsl(var(--muted-foreground))] group-hover:text-[hsl(var(--foreground))] transition-colors">
                  Lembrar-me
                </span>
              </label>
              <a
                href="#"
                className="text-brand-500 hover:text-brand-400 transition-colors"
              >
                Esqueci a senha
              </a>
            </div>

            {/* Botão de login */}
            <Button
              type="submit"
              className="w-full btn-brand group"
              size="lg"
              isLoading={isLoading}
            >
              Entrar
              <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
            </Button>
          </form>

          {/* Divisor */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[hsl(var(--border))]" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-[hsl(var(--background))] text-[hsl(var(--muted-foreground))]">
                Conecta PRO v2.0.0
              </span>
            </div>
          </div>

          {/* Footer */}
          <p className="text-center text-xs text-[hsl(var(--muted-foreground))]">
            Ao entrar, você concorda com os{' '}
            <a href="#" className="text-brand-500 hover:underline">
              Termos de Uso
            </a>{' '}
            e{' '}
            <a href="#" className="text-brand-500 hover:underline">
              Política de Privacidade
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
