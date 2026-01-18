import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

interface PWAState {
  isInstallable: boolean;
  isInstalled: boolean;
  isUpdateAvailable: boolean;
}

export function usePWA() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [state, setState] = useState<PWAState>({
    isInstallable: false,
    isInstalled: false,
    isUpdateAvailable: false,
  });

  // Detecta se o app já está instalado
  useEffect(() => {
    const checkInstalled = () => {
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
      const isInWebAppiOS = ('standalone' in window.navigator) && (window.navigator as { standalone?: boolean }).standalone;

      setState((prev) => ({
        ...prev,
        isInstalled: isStandalone || !!isInWebAppiOS,
      }));
    };

    checkInstalled();

    // Listener para mudanças no display mode
    const mediaQuery = window.matchMedia('(display-mode: standalone)');
    mediaQuery.addEventListener('change', checkInstalled);

    return () => {
      mediaQuery.removeEventListener('change', checkInstalled);
    };
  }, []);

  // Captura o evento beforeinstallprompt
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setState((prev) => ({
        ...prev,
        isInstallable: true,
      }));
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  // Detecta atualizações do service worker
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((registration) => {
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                setState((prev) => ({
                  ...prev,
                  isUpdateAvailable: true,
                }));
              }
            });
          }
        });
      });
    }
  }, []);

  // Função para instalar o app
  const install = useCallback(async () => {
    if (!deferredPrompt) {
      return { success: false, error: 'Instalação não disponível' };
    }

    try {
      await deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;

      if (outcome === 'accepted') {
        setDeferredPrompt(null);
        setState((prev) => ({
          ...prev,
          isInstallable: false,
          isInstalled: true,
        }));
        return { success: true };
      }

      return { success: false, error: 'Instalação cancelada pelo usuário' };
    } catch (error) {
      return { success: false, error: 'Erro ao instalar' };
    }
  }, [deferredPrompt]);

  // Função para atualizar o app
  const update = useCallback(async () => {
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.ready;
      await registration.update();
      window.location.reload();
    }
  }, []);

  // Função para dispensar o prompt
  const dismissInstall = useCallback(() => {
    setState((prev) => ({
      ...prev,
      isInstallable: false,
    }));
  }, []);

  return {
    ...state,
    install,
    update,
    dismissInstall,
  };
}
