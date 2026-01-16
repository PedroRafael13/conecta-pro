import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@core': path.resolve(__dirname, './src/core'),
      '@modules': path.resolve(__dirname, './src/modules'),
      '@components': path.resolve(__dirname, './src/core/components'),
      '@hooks': path.resolve(__dirname, './src/core/hooks'),
      '@utils': path.resolve(__dirname, './src/core/utils'),
      '@api': path.resolve(__dirname, './src/core/api'),
      '@stores': path.resolve(__dirname, './src/core/stores'),
      '@types': path.resolve(__dirname, './src/core/types'),
      '@pages': path.resolve(__dirname, './src/pages'),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['framer-motion', '@headlessui/react', 'lucide-react'],
          data: ['@tanstack/react-query', 'zustand', 'axios'],
        },
      },
    },
  },
})
