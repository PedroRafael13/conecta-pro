'use client';

import { useEffect } from 'react';
import { Capacitor } from '@capacitor/core';
import { useCapacitor } from '@core/hooks';

export function CapacitorInit() {
  const { isNative, platform } = useCapacitor();

  useEffect(() => {
    if (!isNative) return;

    // Adiciona classe no body para estilos específicos de plataforma
    document.body.classList.add('capacitor');
    document.body.classList.add(`platform-${platform}`);

    // Previne zoom indesejado em inputs no iOS
    if (platform === 'ios') {
      const meta = document.querySelector('meta[name="viewport"]');
      if (meta) {
        meta.setAttribute(
          'content',
          'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover'
        );
      }
    }

    // Ajusta safe areas para notch/home indicator
    document.documentElement.style.setProperty(
      '--safe-area-inset-top',
      'env(safe-area-inset-top)'
    );
    document.documentElement.style.setProperty(
      '--safe-area-inset-bottom',
      'env(safe-area-inset-bottom)'
    );
    document.documentElement.style.setProperty(
      '--safe-area-inset-left',
      'env(safe-area-inset-left)'
    );
    document.documentElement.style.setProperty(
      '--safe-area-inset-right',
      'env(safe-area-inset-right)'
    );

    return () => {
      document.body.classList.remove('capacitor');
      document.body.classList.remove(`platform-${platform}`);
    };
  }, [isNative, platform]);

  // Este componente não renderiza nada visível
  return null;
}
