import { useState, useEffect, useCallback } from 'react';
import Shepherd from 'shepherd.js';
import { createOperacionalTour, isTourCompleted, resetTour as resetTourStorage, UserRole } from '../tours/operacionalTour';

interface UseTourReturn {
  isCompleted: boolean;
  isActive: boolean;
  currentStep: number | null;
  totalSteps: number;
  startTour: () => void;
  resetTour: () => void;
  cancelTour: () => void;
}

// Lazy initialization function for localStorage
const getInitialCompletedState = (): boolean => {
  if (typeof window === 'undefined') return true;
  return isTourCompleted();
};

export const useTour = (role: UserRole = 'USUARIO', autoStart = false): UseTourReturn => {
  // Use lazy initialization to avoid setState in effect
  const [isCompleted, setIsCompleted] = useState<boolean>(getInitialCompletedState);
  const [isActive, setIsActive] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number | null>(null);
  const [totalSteps, setTotalSteps] = useState<number>(0);
  const [tourInstance, setTourInstance] = useState<any>(null);

  // Função para iniciar o tour
  const startTour = useCallback(() => {
    // Cancela tour existente se houver
    if (tourInstance) {
      tourInstance.cancel();
    }

    // Cria novo tour
    const tour = createOperacionalTour(role);
    setTourInstance(tour);
    setTotalSteps(tour.steps.length);

    // Event listeners
    tour.on('show', () => {
      setIsActive(true);
      const currentStepObj = tour.getCurrentStep();
      if (currentStepObj) {
        const stepIndex = tour.steps.indexOf(currentStepObj);
        setCurrentStep(stepIndex);
      }
    });

    tour.on('complete', () => {
      setIsActive(false);
      setIsCompleted(true);
      setCurrentStep(null);
    });

    tour.on('cancel', () => {
      setIsActive(false);
      setCurrentStep(null);
    });

    // Inicia o tour
    tour.start();
  }, [role, tourInstance]);

  // Função para resetar o tour
  const resetTour = useCallback(() => {
    resetTourStorage();
    setIsCompleted(false);
  }, []);

  // Função para cancelar tour em andamento
  const cancelTour = useCallback(() => {
    if (tourInstance && isActive) {
      tourInstance.cancel();
    }
  }, [tourInstance, isActive]);

  // Auto-start se configurado e não completado
  useEffect(() => {
    if (autoStart && !isCompleted && typeof window !== 'undefined') {
      // Delay de 1s para garantir que página carregou
      const timer = setTimeout(() => {
        startTour();
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [autoStart, isCompleted, startTour]);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (tourInstance) {
        tourInstance.cancel();
      }
    };
  }, [tourInstance]);

  return {
    isCompleted,
    isActive,
    currentStep,
    totalSteps,
    startTour,
    resetTour,
    cancelTour,
  };
};

// Lazy initialization for useShouldShowTour
const getInitialShouldShowState = (): boolean => {
  if (typeof window === 'undefined') return false;
  return !isTourCompleted();
};

// Hook simplificado para apenas verificar se deve mostrar tour
export const useShouldShowTour = (): boolean => {
  const [shouldShow, setShouldShow] = useState<boolean>(getInitialShouldShowState);

  // Update on mount only if needed
  useEffect(() => {
    const currentValue = !isTourCompleted();
    if (currentValue !== shouldShow) {

      setShouldShow(currentValue);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return shouldShow;
};

// Lazy initialization for tour progress
const getInitialProgressState = () => ({
  started: false,
  completed: false,
  startedAt: null as string | null,
  completedAt: null as string | null,
  cancelCount: 0,
});

const loadProgressFromStorage = () => {
  if (typeof window === 'undefined') {
    return getInitialProgressState();
  }

  const completed = localStorage.getItem('tour_operacional_completed') === 'true';
  const completedAt = localStorage.getItem('tour_operacional_completed_at');
  const startedAt = localStorage.getItem('tour_operacional_started_at');
  const cancelCount = parseInt(localStorage.getItem('tour_operacional_cancel_count') || '0', 10);

  return {
    started: !!startedAt,
    completed,
    startedAt,
    completedAt,
    cancelCount,
  };
};

// Hook para tracking de progresso do tour
export const useTourProgress = () => {
  // Use lazy initialization to read from localStorage
  const [progress, setProgress] = useState(loadProgressFromStorage);

  // Sync with localStorage on mount (in case it changed)
  useEffect(() => {
    const storedProgress = loadProgressFromStorage();
    // Only update if different to avoid unnecessary renders
    if (
      storedProgress.started !== progress.started ||
      storedProgress.completed !== progress.completed ||
      storedProgress.cancelCount !== progress.cancelCount
    ) {

      setProgress(storedProgress);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const markStarted = useCallback(() => {
    if (typeof window === 'undefined') return;
    const now = new Date().toISOString();
    localStorage.setItem('tour_operacional_started_at', now);
    setProgress((prev) => ({ ...prev, started: true, startedAt: now }));
  }, []);

  const markCompleted = useCallback(() => {
    if (typeof window === 'undefined') return;
    const now = new Date().toISOString();
    localStorage.setItem('tour_operacional_completed', 'true');
    localStorage.setItem('tour_operacional_completed_at', now);
    setProgress((prev) => ({ ...prev, completed: true, completedAt: now }));
  }, []);

  const incrementCancelCount = useCallback(() => {
    if (typeof window === 'undefined') return;
    const newCount = progress.cancelCount + 1;
    localStorage.setItem('tour_operacional_cancel_count', newCount.toString());
    setProgress((prev) => ({ ...prev, cancelCount: newCount }));
  }, [progress.cancelCount]);

  return {
    progress,
    markStarted,
    markCompleted,
    incrementCancelCount,
  };
};
