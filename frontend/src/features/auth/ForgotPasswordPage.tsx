'use client';

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, ArrowLeft, CheckCircle2, KeyRound } from 'lucide-react';
import { Button, Input } from '@/design-system/components';

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsLoading(false);
    setIsSubmitted(true);
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-bg-primary via-bg-secondary to-bg-primary flex items-center justify-center p-4">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="max-w-md w-full bg-bg-secondary rounded-2xl p-8 text-center"
        >
          <div className="w-20 h-20 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle2 className="w-10 h-10 text-success" />
          </div>
          <h2 className="text-2xl font-bold text-text-primary mb-2">Email Enviado!</h2>
          <p className="text-text-secondary mb-6">
            Enviamos um link de recuperacao para <strong>{email}</strong>. Verifique sua caixa de entrada e spam.
          </p>
          <div className="space-y-3">
            <Button variant="primary" className="w-full" onClick={() => navigate('/login')}>
              Voltar ao Login
            </Button>
            <button
              onClick={() => setIsSubmitted(false)}
              className="text-sm text-text-muted hover:text-accent-primary transition-colors"
            >
              Nao recebeu? Tentar outro email
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-bg-primary via-bg-secondary to-bg-primary flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        <div className="bg-bg-secondary rounded-2xl p-8 shadow-xl">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-accent-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <KeyRound className="w-8 h-8 text-accent-primary" />
            </div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Recuperar Senha
            </h1>
            <p className="text-text-secondary mt-2">
              Digite seu email para receber o link de recuperacao
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-5 h-5" />}
              placeholder="seu@email.com"
              required
              autoFocus
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              disabled={isLoading || !email}
            >
              {isLoading ? 'Enviando...' : 'Enviar Link de Recuperacao'}
            </Button>
          </form>

          <div className="mt-8 pt-6 border-t border-border-default">
            <Link
              to="/login"
              className="flex items-center justify-center gap-2 text-text-secondary hover:text-accent-primary transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Voltar ao login
            </Link>
          </div>
        </div>

        <p className="text-center text-text-muted text-sm mt-6">
          Lembrou sua senha?{' '}
          <Link to="/login" className="text-accent-primary hover:underline">
            Fazer login
          </Link>
        </p>
      </motion.div>
    </div>
  );
}

export default ForgotPasswordPage;
