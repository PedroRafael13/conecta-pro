'use client';

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Mail,
  Lock,
  User,
  Building2,
  Phone,
  Eye,
  EyeOff,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';
import { Button, Input } from '@/design-system/components';

export function RegisterPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (step < 2) {
      setStep(step + 1);
      return;
    }

    setIsLoading(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsLoading(false);
    setStep(3);
  };

  if (step === 3) {
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
          <h2 className="text-2xl font-bold text-text-primary mb-2">Cadastro Realizado!</h2>
          <p className="text-text-secondary mb-6">
            Enviamos um email de confirmacao para {formData.email}. Por favor, verifique sua caixa de entrada.
          </p>
          <Button variant="primary" className="w-full" onClick={() => navigate('/login')}>
            Ir para Login
          </Button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-bg-primary via-bg-secondary to-bg-primary flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 items-center justify-center p-12 bg-gradient-to-br from-accent-primary/10 to-accent-secondary/10">
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-lg"
        >
          <div className="mb-8">
            <h1 className="text-5xl font-display font-bold text-text-primary mb-4">
              Conecta<span className="text-accent-primary">Plus</span>
            </h1>
            <p className="text-xl text-text-secondary">
              Plataforma completa de gestao empresarial
            </p>
          </div>
          <div className="space-y-4">
            {[
              'Gestao de contratos e clientes',
              'Controle financeiro integrado',
              'RH e folha de pagamento',
              'Inteligencia artificial embarcada',
            ].map((feature, index) => (
              <motion.div
                key={feature}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
                className="flex items-center gap-3"
              >
                <div className="w-6 h-6 rounded-full bg-accent-primary/20 flex items-center justify-center">
                  <CheckCircle2 className="w-4 h-4 text-accent-primary" />
                </div>
                <span className="text-text-secondary">{feature}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full"
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl font-display font-bold text-text-primary">
              Criar Conta
            </h2>
            <p className="text-text-secondary mt-2">
              Passo {step} de 2 - {step === 1 ? 'Dados pessoais' : 'Seguranca'}
            </p>
          </div>

          {/* Progress Bar */}
          <div className="flex gap-2 mb-8">
            {[1, 2].map((s) => (
              <div
                key={s}
                className={`flex-1 h-1 rounded-full transition-colors ${
                  s <= step ? 'bg-accent-primary' : 'bg-bg-tertiary'
                }`}
              />
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {step === 1 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-4"
              >
                <Input
                  label="Nome Completo"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  leftIcon={<User className="w-5 h-5" />}
                  placeholder="Seu nome completo"
                  required
                />
                <Input
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  leftIcon={<Mail className="w-5 h-5" />}
                  placeholder="seu@email.com"
                  required
                />
                <Input
                  label="Telefone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  leftIcon={<Phone className="w-5 h-5" />}
                  placeholder="(11) 99999-9999"
                />
                <Input
                  label="Empresa"
                  type="text"
                  value={formData.company}
                  onChange={(e) => handleChange('company', e.target.value)}
                  leftIcon={<Building2 className="w-5 h-5" />}
                  placeholder="Nome da empresa"
                />
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-4"
              >
                <div className="relative">
                  <Input
                    label="Senha"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    leftIcon={<Lock className="w-5 h-5" />}
                    placeholder="Crie uma senha forte"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-9 text-text-muted hover:text-text-primary"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                <Input
                  label="Confirmar Senha"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  leftIcon={<Lock className="w-5 h-5" />}
                  placeholder="Confirme sua senha"
                  required
                />
                <p className="text-xs text-text-muted">
                  A senha deve ter pelo menos 8 caracteres, incluindo maiusculas, minusculas e numeros.
                </p>
              </motion.div>
            )}

            <div className="flex gap-3">
              {step > 1 && (
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => setStep(step - 1)}
                >
                  Voltar
                </Button>
              )}
              <Button
                type="submit"
                variant="primary"
                className="flex-1"
                disabled={isLoading}
              >
                {isLoading ? (
                  'Criando conta...'
                ) : step < 2 ? (
                  <>
                    Continuar
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                ) : (
                  'Criar Conta'
                )}
              </Button>
            </div>
          </form>

          <p className="text-center text-text-secondary mt-8">
            Ja tem uma conta?{' '}
            <Link to="/login" className="text-accent-primary hover:underline font-medium">
              Fazer login
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}

export default RegisterPage;
