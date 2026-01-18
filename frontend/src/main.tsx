import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { setupInterceptors } from '@core/api/interceptors';
import './index.css';

// Inicializa interceptors de autenticação (token refresh, error handling)
setupInterceptors();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
