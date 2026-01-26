'use client';

import { useState } from 'react';
import { useTour } from '../hooks/useTour';
import { UserRole } from '../tours/operacionalTour';

interface TourTriggerProps {
  role?: UserRole;
  variant?: 'button' | 'menu-item' | 'badge';
  className?: string;
  children?: React.ReactNode;
}

export function TourTrigger({
  role = 'USUARIO',
  variant = 'button',
  className = '',
  children
}: TourTriggerProps) {
  const { isCompleted, isActive, resetTour, startTour } = useTour(role);
  const [isResetting, setIsResetting] = useState(false);

  const handleStartTour = () => {
    setIsResetting(true);
    resetTour();

    // Pequeno delay para garantir que reset foi aplicado
    setTimeout(() => {
      startTour();
      setIsResetting(false);
    }, 100);
  };

  if (variant === 'button') {
    return (
      <button
        onClick={handleStartTour}
        disabled={isActive || isResetting}
        className={`
          px-4 py-2 rounded-lg font-medium transition-all
          ${isActive || isResetting
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
          }
          ${className}
        `}
        title={isCompleted ? 'Refazer tour guiado' : 'Iniciar tour guiado'}
      >
        {isResetting ? (
          <>
            <span className="inline-block animate-spin mr-2">⏳</span>
            Preparando...
          </>
        ) : isActive ? (
          <>
            <span className="inline-block mr-2">▶️</span>
            Tour em andamento...
          </>
        ) : (
          <>
            <span className="inline-block mr-2">🧭</span>
            {isCompleted ? 'Refazer Tour' : 'Iniciar Tour'}
          </>
        )}
      </button>
    );
  }

  if (variant === 'menu-item') {
    return (
      <button
        onClick={handleStartTour}
        disabled={isActive || isResetting}
        className={`
          w-full px-4 py-2 text-left flex items-center gap-3
          transition-colors rounded-md
          ${isActive || isResetting
            ? 'text-gray-400 cursor-not-allowed'
            : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
          }
          ${className}
        `}
      >
        <span className="text-xl">🧭</span>
        <div className="flex-1">
          <div className="font-medium">
            {isCompleted ? 'Refazer Tour Guiado' : 'Tour Guiado'}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {isResetting
              ? 'Preparando tour...'
              : isActive
              ? 'Em andamento...'
              : 'Conheça as funcionalidades'
            }
          </div>
        </div>
        {isCompleted && (
          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded dark:bg-green-900 dark:text-green-300">
            ✓ Completo
          </span>
        )}
      </button>
    );
  }

  if (variant === 'badge') {
    if (isCompleted) return null; // Não mostra badge se já completou

    return (
      <button
        onClick={handleStartTour}
        disabled={isActive || isResetting}
        className={`
          relative inline-flex items-center gap-2 px-3 py-1.5
          bg-blue-50 text-blue-700 rounded-full text-sm font-medium
          hover:bg-blue-100 transition-all
          dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800
          ${isActive || isResetting ? 'opacity-50 cursor-not-allowed' : ''}
          ${className}
        `}
      >
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
        </span>
        {isResetting ? 'Preparando...' : isActive ? 'Tour ativo' : 'Novo! Faça o tour'}
      </button>
    );
  }

  // Custom children
  return (
    <button
      onClick={handleStartTour}
      disabled={isActive || isResetting}
      className={className}
    >
      {children}
    </button>
  );
}

// Componente para trigger flutuante (floating action button)
export function FloatingTourTrigger({ role = 'USUARIO' }: { role?: UserRole }) {
  const { isCompleted, isActive } = useTour(role);
  const [isHovered, setIsHovered] = useState(false);

  // Não mostra se tour já foi completado
  if (isCompleted || isActive) return null;

  return (
    <div
      className="fixed bottom-6 right-6 z-50"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <TourTrigger
        role={role}
        variant="button"
        className={`
          !rounded-full !px-5 !py-3 shadow-lg
          flex items-center gap-2 transition-all
          ${isHovered ? '!px-6' : ''}
        `}
      >
        <span className="text-lg">🧭</span>
        {isHovered && (
          <span className="text-sm font-medium whitespace-nowrap">
            Fazer Tour
          </span>
        )}
      </TourTrigger>
    </div>
  );
}

// Componente para mostrar progresso do tour
export function TourProgress() {
  const { isActive, currentStep, totalSteps } = useTour();

  if (!isActive || currentStep === null) return null;

  const progress = ((currentStep + 1) / totalSteps) * 100;

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      <div className="bg-white dark:bg-gray-800 shadow-md">
        <div className="container mx-auto px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Tour Guiado
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Passo {currentStep + 1} de {totalSteps}
            </span>
          </div>
          <div className="w-48 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente para exibir notificação de tour disponível
export function TourNotification({ role = 'USUARIO' }: { role?: UserRole }) {
  const { isCompleted } = useTour(role);
  const [isDismissed, setIsDismissed] = useState(false);

  // Verifica se já foi dispensado nesta sessão
  if (isCompleted || isDismissed) return null;

  return (
    <div className="fixed bottom-6 left-6 z-50 max-w-md">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-4 border-l-4 border-blue-600">
        <div className="flex items-start gap-3">
          <span className="text-2xl">🧭</span>
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
              Primeira vez aqui?
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Faça um tour rápido para conhecer as principais funcionalidades do sistema.
            </p>
            <div className="flex gap-2">
              <TourTrigger
                role={role}
                variant="button"
                className="!text-sm !px-3 !py-1.5"
              />
              <button
                onClick={() => setIsDismissed(true)}
                className="text-sm px-3 py-1.5 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Agora não
              </button>
            </div>
          </div>
          <button
            onClick={() => setIsDismissed(true)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}
