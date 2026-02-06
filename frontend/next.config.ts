import type { NextConfig } from 'next';
import withBundleAnalyzer from '@next/bundle-analyzer';

const bundleAnalyzer = withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig: NextConfig = {
  output: 'standalone',

  // TypeScript: validação de tipos ativa (0 erros - migração completa)
  typescript: {
    ignoreBuildErrors: false,
  },

  // Configuração de ambiente
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://erp.conectamais.pro',
    NEXT_PUBLIC_APP_NAME: 'Conecta PRO',
    NEXT_PUBLIC_APP_VERSION: '2.0.0',
  },

  // Otimização de imports
  experimental: {
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-select',
      '@radix-ui/react-tooltip',
      '@radix-ui/react-popover',
      'date-fns',
      'recharts',
    ],
  },

  // Habilitar Turbopack explicitamente (Next.js 16)
  // Configuração vazia para silenciar warning
  turbopack: {},

  // Otimização de imagens
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Headers de segurança
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ];
  },

  // Rewrites para API (desenvolvimento local)
  async rewrites() {
    return process.env.NODE_ENV === 'development'
      ? [
          {
            source: '/api/v1/:path*',
            destination: 'http://localhost:8080/api/v1/:path*',
          },
        ]
      : [];
  },

  // Code splitting estratégico (desabilitado temporariamente para Turbopack)
  // NOTA: Turbopack tem seu próprio code splitting otimizado
  // As configurações de webpack serão ignoradas quando Turbopack estiver ativo
  // webpack: (config, { isServer }) => {
  //   if (!isServer) {
  //     config.optimization = {
  //       ...config.optimization,
  //       splitChunks: {
  //         chunks: 'all',
  //         cacheGroups: {
  //           // Bibliotecas de gráficos (pesadas)
  //           recharts: {
  //             test: /[\\/]node_modules[\\/]recharts[\\/]/,
  //             name: 'recharts',
  //             priority: 10,
  //             reuseExistingChunk: true,
  //           },
  //           // Componentes Radix UI
  //           radixUI: {
  //             test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
  //             name: 'radix-ui',
  //             priority: 9,
  //             reuseExistingChunk: true,
  //           },
  //           // Data utilities
  //           dateUtils: {
  //             test: /[\\/]node_modules[\\/](date-fns|dayjs)[\\/]/,
  //             name: 'date-utils',
  //             priority: 8,
  //             reuseExistingChunk: true,
  //           },
  //           // Features por módulo
  //           financeiro: {
  //             test: /[\\/]src[\\/]app[\\/]modulos[\\/]financeiro[\\/]/,
  //             name: 'feature-financeiro',
  //             priority: 7,
  //             minChunks: 2,
  //             reuseExistingChunk: true,
  //           },
  //           equipamentos: {
  //             test: /[\\/]src[\\/]app[\\/]modulos[\\/]equipamentos[\\/]/,
  //             name: 'feature-equipamentos',
  //             priority: 7,
  //             minChunks: 2,
  //             reuseExistingChunk: true,
  //           },
  //           operacional: {
  //             test: /[\\/]src[\\/]app[\\/]modulos[\\/]operacional[\\/]/,
  //             name: 'feature-operacional',
  //             priority: 7,
  //             minChunks: 2,
  //             reuseExistingChunk: true,
  //           },
  //           integracoes: {
  //             test: /[\\/]src[\\/]app[\\/]modulos[\\/]integracoes[\\/]/,
  //             name: 'feature-integracoes',
  //             priority: 7,
  //             minChunks: 2,
  //             reuseExistingChunk: true,
  //           },
  //           // Componentes compartilhados
  //           components: {
  //             test: /[\\/]src[\\/]components[\\/]/,
  //             name: 'components',
  //             priority: 6,
  //             minChunks: 3,
  //             reuseExistingChunk: true,
  //           },
  //           // Vendors comuns
  //           vendor: {
  //             test: /[\\/]node_modules[\\/]/,
  //             name: 'vendor',
  //             priority: 5,
  //             reuseExistingChunk: true,
  //           },
  //         },
  //       },
  //     };
  //   }
  //   return config;
  // },
};

export default bundleAnalyzer(nextConfig);
