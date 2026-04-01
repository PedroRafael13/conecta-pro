'use client';

import { useEffect } from 'react';
import { AlertCircle, RotateCcw, Home } from 'lucide-react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log to external service in production
    if (process.env.NODE_ENV === 'production') {
      // Sentry or similar would capture this
      console.error('[ErrorBoundary]', error);
    }
  }, [error]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center p-6">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="mx-auto w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-red-500" />
        </div>

        <div className="space-y-2">
          <h2 className="text-xl font-semibold text-[hsl(var(--foreground))]">
            Algo deu errado
          </h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Ocorreu um erro inesperado. Tente novamente ou volte para o inicio.
          </p>
          {error.digest && (
            <p className="text-xs text-[hsl(var(--muted-foreground))] font-mono">
              Codigo: {error.digest}
            </p>
          )}
        </div>

        <div className="flex items-center justify-center gap-3">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 transition-opacity"
          >
            <RotateCcw className="w-4 h-4" />
            Tentar novamente
          </button>
          <a
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border border-[hsl(var(--border))] text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))] transition-colors"
          >
            <Home className="w-4 h-4" />
            Ir para o inicio
          </a>
        </div>
      </div>
    </div>
  );
}
