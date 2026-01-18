import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'br.com.conectapro.app',
  appName: 'Conecta PRO',
  webDir: 'dist',

  // Configuração do servidor
  server: {
    // Em desenvolvimento, usar URL do servidor local
    // url: 'http://192.168.1.100:3000',
    // cleartext: true,

    // Em produção, usa os arquivos buildados
    androidScheme: 'https',
    iosScheme: 'https',
  },

  // Plugins
  plugins: {
    // Splash Screen
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: '#0A2540',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
      splashFullScreen: true,
      splashImmersive: true,
    },

    // Status Bar
    StatusBar: {
      backgroundColor: '#0A2540',
      style: 'LIGHT',
      overlaysWebView: false,
    },

    // Keyboard
    Keyboard: {
      resize: 'body',
      resizeOnFullScreen: true,
    },

    // Push Notifications
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },

    // App
    App: {
      // Deep links
      // url: 'conectapro://',
    },
  },

  // Configurações Android
  android: {
    allowMixedContent: false,
    captureInput: true,
    webContentsDebuggingEnabled: false, // Desabilitar em produção
    backgroundColor: '#0A2540',
    buildOptions: {
      keystorePath: 'release-key.keystore',
      keystoreAlias: 'conectapro',
    },
  },

  // Configurações iOS
  ios: {
    contentInset: 'automatic',
    backgroundColor: '#0A2540',
    preferredContentMode: 'mobile',
    scheme: 'ConectaPRO',
  },
};

export default config;
