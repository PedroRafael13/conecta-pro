import type { NextConfig } from 'next';
import withBundleAnalyzer from '@next/bundle-analyzer';

const bundleAnalyzer = withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig: NextConfig = {
  output: 'standalone',

  // TypeScript: validação de tipos ativa
  typescript: {
    ignoreBuildErrors: false,
  },

  // Configuração de ambiente
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://erp.conectamais.pro',
    NEXT_PUBLIC_APP_NAME: 'Conecta PRO',
    NEXT_PUBLIC_APP_VERSION: '2.0.0',
  },

  // Otimização de imports - FASE 4
  experimental: {
    // Otimizar imports de bibliotecas grandes
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-select',
      '@radix-ui/react-tooltip',
      '@radix-ui/react-popover',
      '@radix-ui/react-tabs',
      '@radix-ui/react-accordion',
      'date-fns',
      'recharts',
      'echarts',
      'echarts-for-react',
      'zod',
    ],

    // Otimização de server components
    serverComponentsExternalPackages: ['xlsx'],

    // Partial Prerendering (Next.js 14+)
    ppr: false, // Habilitar quando estiver estável
  },

  // Habilitar Turbopack (Next.js 16)
  turbopack: {
    // Configurações específicas do Turbopack
    resolveExtensions: ['.tsx', '.ts', '.jsx', '.js', '.json'],
  },

  // Otimização de imagens
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'erp.conectamais.pro',
      },
      {
        protocol: 'https',
        hostname: '*.amazonaws.com',
      },
    ],
  },

  // Compressão
  compress: true,

  // Headers de segurança e performance
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy', value: 'geolocation=(), microphone=(), camera=()' },
          { key: 'X-DNS-Prefetch-Control', value: 'off' },
          // Cache para assets estáticos
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        // API routes não devem ter cache longo
        source: '/api/:path*',
        headers: [
          { key: 'Cache-Control', value: 'no-store, max-age=0' },
        ],
      },
    ];
  },

  // Rewrites para API
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

  // Webpack config (fallback quando Turbopack não está disponível)
  webpack: (config, { isServer, nextRuntime }) => {
    // Otimizações de bundle
    if (!isServer) {
      // Split chunks para bibliotecas grandes
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            // Vendor separado
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
              priority: 10,
            },
            // Charts separados (carregado sob demanda)
            charts: {
              test: /[\\/](recharts|echarts|echarts-for-react)[\\/]/,
              name: 'charts',
              chunks: 'async',
              priority: 20,
            },
            // UI components
            ui: {
              test: /[\\/](@radix-ui|lucide-react)[\\/]/,
              name: 'ui',
              chunks: 'all',
              priority: 5,
            },
          },
        },
      };

      // Ignorar locales do moment se ainda estiver presente
      config.ignoreWarnings = [
        { module: /moment[\\/]locale/ },
      ];
    }

    return config;
  },

  // Logging
  logging: {
    fetches: {
      fullUrl: process.env.NODE_ENV === 'development',
    },
  },

  // DistDir customizado
  distDir: '.next',

  // Powered by header
  poweredByHeader: false,
};

export default bundleAnalyzer(nextConfig);
