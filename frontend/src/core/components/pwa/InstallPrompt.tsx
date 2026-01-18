'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, X, Smartphone } from 'lucide-react';
import { usePWA } from '@core/hooks';

const DISMISSED_KEY = 'pwa-install-dismissed';
const DISMISS_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 dias

export function InstallPrompt() {
  const { isInstallable, isInstalled, install, dismissInstall } = usePWA();
  const [isVisible, setIsVisible] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);

  useEffect(() => {
    if (isInstallable && !isInstalled) {
      const dismissed = localStorage.getItem(DISMISSED_KEY);
      if (dismissed) {
        const dismissedAt = parseInt(dismissed, 10);
        if (Date.now() - dismissedAt < DISMISS_DURATION) {
          return;
        }
      }
      // Mostra o prompt após 30 segundos de uso
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 30000);
      return () => clearTimeout(timer);
    }
  }, [isInstallable, isInstalled]);

  const handleInstall = async () => {
    setIsInstalling(true);
    const result = await install();
    setIsInstalling(false);

    if (result.success) {
      setIsVisible(false);
    }
  };

  const handleDismiss = () => {
    localStorage.setItem(DISMISSED_KEY, Date.now().toString());
    setIsVisible(false);
    dismissInstall();
  };

  if (isInstalled) return null;

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-[100]"
        >
          <div className="bg-bg-secondary border border-border-default rounded-xl p-4 shadow-2xl">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-accent-primary/10 rounded-xl flex items-center justify-center">
                <Smartphone className="w-6 h-6 text-accent-primary" />
              </div>

              <div className="flex-1 min-w-0">
                <h3 className="text-base font-semibold text-text-primary">
                  Instalar Conecta PRO
                </h3>
                <p className="text-sm text-text-secondary mt-1">
                  Instale o app para acesso rapido e funcionalidades offline.
                </p>

                <div className="flex items-center gap-2 mt-4">
                  <button
                    onClick={handleInstall}
                    disabled={isInstalling}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-accent-primary hover:bg-accent-primary/90 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
                  >
                    {isInstalling ? (
                      <>
                        <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                        Instalando...
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4" />
                        Instalar
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleDismiss}
                    className="px-4 py-2 text-text-secondary hover:text-text-primary text-sm font-medium rounded-lg hover:bg-bg-tertiary transition-colors"
                  >
                    Agora nao
                  </button>
                </div>
              </div>

              <button
                onClick={handleDismiss}
                className="flex-shrink-0 p-1 text-text-muted hover:text-text-secondary rounded-full hover:bg-bg-tertiary transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
