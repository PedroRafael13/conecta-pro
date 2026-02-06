/**
 * LoadingState - Componente de loading reutilizável
 *
 * Exibe um spinner animado com mensagem opcional.
 * Usado em páginas, modais e componentes que carregam dados.
 */

import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingStateProps {
  /** Mensagem a ser exibida abaixo do spinner */
  message?: string;
  /** Tamanho do spinner e texto */
  size?: 'sm' | 'md' | 'lg';
  /** Classes CSS adicionais */
  className?: string;
}

const sizeClasses = {
  sm: {
    spinner: 'h-4 w-4',
    text: 'text-xs',
    container: 'gap-2',
  },
  md: {
    spinner: 'h-8 w-8',
    text: 'text-sm',
    container: 'gap-3',
  },
  lg: {
    spinner: 'h-12 w-12',
    text: 'text-base',
    container: 'gap-4',
  },
};

export function LoadingState({
  message = 'Carregando...',
  size = 'md',
  className
}: LoadingStateProps) {
  const classes = sizeClasses[size];

  return (
    <div className={cn(
      'flex flex-col items-center justify-center p-8',
      classes.container,
      className
    )}>
      <Loader2 className={cn(
        'animate-spin text-primary',
        classes.spinner
      )} />
      {message && (
        <p className={cn(
          'text-muted-foreground',
          classes.text
        )}>
          {message}
        </p>
      )}
    </div>
  );
}

/**
 * LoadingOverlay - Loading em overlay sobre conteúdo
 *
 * Útil para mostrar loading sem substituir o conteúdo existente.
 */
export function LoadingOverlay({
  message,
  size = 'lg'
}: Omit<LoadingStateProps, 'className'>) {
  return (
    <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <LoadingState message={message} size={size} />
    </div>
  );
}

/**
 * LoadingSpinner - Apenas o spinner sem container
 *
 * Para uso inline em botões, badges, etc.
 */
export function LoadingSpinner({
  size = 'md',
  className
}: Pick<LoadingStateProps, 'size' | 'className'>) {
  const classes = sizeClasses[size];

  return (
    <Loader2 className={cn(
      'animate-spin',
      classes.spinner,
      className
    )} />
  );
}
