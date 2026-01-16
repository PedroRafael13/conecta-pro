'use client';

import { type ReactNode } from 'react';
import { motion } from 'framer-motion';

interface AuthLayoutProps {
  children: ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-bg-primary flex">
      {/* Left Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md"
        >
          {children}
        </motion.div>
      </div>

      {/* Right Panel - Branding */}
      <div className="hidden lg:flex lg:flex-1 relative overflow-hidden">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/20 via-bg-secondary to-accent-secondary/20" />

        {/* Mesh Gradient */}
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `
              radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.3) 0px, transparent 50%),
              radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.2) 0px, transparent 50%),
              radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.2) 0px, transparent 50%),
              radial-gradient(at 0% 100%, rgba(139, 92, 246, 0.3) 0px, transparent 50%)
            `,
          }}
        />

        {/* Noise Overlay */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }} />

        {/* Content */}
        <div className="relative z-10 flex flex-col items-center justify-center p-12 text-center">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-8"
          >
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center shadow-glow-lg">
              <span className="text-white font-bold text-4xl font-display">C</span>
            </div>
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-4xl font-display font-bold text-text-primary mb-4"
          >
            Conecta PRO
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="text-lg text-text-secondary max-w-sm mb-8"
          >
            ERP Empresarial completo para gestão de segurança, facilities e serviços
          </motion.p>

          {/* Features */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="space-y-3"
          >
            {[
              'CRM & Gestão de Contratos',
              'Financeiro Completo',
              'RH & Operações',
              'Inteligência Artificial',
            ].map((feature, index) => (
              <motion.div
                key={feature}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
                className="flex items-center gap-3 text-text-secondary"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-accent-primary" />
                <span>{feature}</span>
              </motion.div>
            ))}
          </motion.div>

          {/* Decorative Elements */}
          <div className="absolute top-20 left-20 w-32 h-32 bg-accent-primary/10 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-20 w-40 h-40 bg-accent-secondary/10 rounded-full blur-3xl" />
        </div>
      </div>
    </div>
  );
}
