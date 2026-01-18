import { useEffect, useState, useCallback } from 'react';
import { Capacitor } from '@capacitor/core';
import { App } from '@capacitor/app';
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';
import { Keyboard } from '@capacitor/keyboard';
import { Network } from '@capacitor/network';
import { PushNotifications } from '@capacitor/push-notifications';

interface CapacitorState {
  isNative: boolean;
  platform: 'ios' | 'android' | 'web';
  isOnline: boolean;
  pushToken: string | null;
}

export function useCapacitor() {
  const [state, setState] = useState<CapacitorState>({
    isNative: Capacitor.isNativePlatform(),
    platform: Capacitor.getPlatform() as 'ios' | 'android' | 'web',
    isOnline: true,
    pushToken: null,
  });

  // Inicialização dos plugins nativos
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    const initializeNative = async () => {
      try {
        // Configurar Status Bar
        await StatusBar.setStyle({ style: Style.Dark });
        await StatusBar.setBackgroundColor({ color: '#0A2540' });

        // Esconder splash screen após carregamento
        await SplashScreen.hide();

        // Verificar status da rede
        const networkStatus = await Network.getStatus();
        setState((prev) => ({ ...prev, isOnline: networkStatus.connected }));

        // Listener para mudanças de rede
        Network.addListener('networkStatusChange', (status) => {
          setState((prev) => ({ ...prev, isOnline: status.connected }));
        });

        // Listener para quando o app volta do background
        App.addListener('appStateChange', ({ isActive }) => {
          if (isActive) {
            // App voltou ao foreground
            console.log('App ativo');
          }
        });

        // Configurar keyboard listeners (apenas mobile)
        if (Capacitor.getPlatform() !== 'web') {
          Keyboard.addListener('keyboardWillShow', () => {
            document.body.classList.add('keyboard-open');
          });

          Keyboard.addListener('keyboardWillHide', () => {
            document.body.classList.remove('keyboard-open');
          });
        }
      } catch (error) {
        console.error('Erro ao inicializar plugins nativos:', error);
      }
    };

    initializeNative();

    return () => {
      Network.removeAllListeners();
      App.removeAllListeners();
      if (Capacitor.getPlatform() !== 'web') {
        Keyboard.removeAllListeners();
      }
    };
  }, []);

  // Solicitar permissão para push notifications
  const requestPushPermission = useCallback(async () => {
    if (!Capacitor.isNativePlatform()) return null;

    try {
      const permStatus = await PushNotifications.checkPermissions();

      if (permStatus.receive === 'prompt') {
        const result = await PushNotifications.requestPermissions();
        if (result.receive !== 'granted') {
          return null;
        }
      }

      if (permStatus.receive !== 'granted') {
        return null;
      }

      // Registrar para receber push
      await PushNotifications.register();

      // Listener para receber o token
      return new Promise<string>((resolve) => {
        PushNotifications.addListener('registration', (token) => {
          setState((prev) => ({ ...prev, pushToken: token.value }));
          resolve(token.value);
        });

        PushNotifications.addListener('registrationError', (err) => {
          console.error('Erro no registro push:', err);
          resolve('');
        });
      });
    } catch (error) {
      console.error('Erro ao solicitar permissão push:', error);
      return null;
    }
  }, []);

  // Função para vibrar (feedback háptico)
  const vibrate = useCallback(async () => {
    if (!Capacitor.isNativePlatform()) return;

    try {
      const { Haptics, ImpactStyle } = await import('@capacitor/haptics');
      await Haptics.impact({ style: ImpactStyle.Medium });
    } catch (error) {
      // Haptics não disponível
    }
  }, []);

  // Função para abrir URL no browser nativo
  const openBrowser = useCallback(async (url: string) => {
    try {
      const { Browser } = await import('@capacitor/browser');
      await Browser.open({ url });
    } catch (error) {
      window.open(url, '_blank');
    }
  }, []);

  return {
    ...state,
    requestPushPermission,
    vibrate,
    openBrowser,
  };
}

export default useCapacitor;
