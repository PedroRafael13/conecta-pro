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

export const useTour = (role: UserRole = 'USUARIO', autoStart = false): UseTourReturn => {
  const [isCompleted, setIsCompleted] = useState<boolean>(true);
  const [isActive, setIsActive] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number | null>(null);
  const [totalSteps, setTotalSteps] = useState<number>(0);
  const [tourInstance, setTourInstance] = useState<any>(null);

  // Verifica se tour já foi completado
  useEffect(() => {
    const completed = isTourCompleted();
    setIsCompleted(completed);
  }, []);

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
      console.log('[useTour] Tour completado');
    });

    tour.on('cancel', () => {
      setIsActive(false);
      setCurrentStep(null);
      console.log('[useTour] Tour cancelado');
    });

    // Inicia o tour
    tour.start();
  }, [role, tourInstance]);

  // Função para resetar o tour
  const resetTour = useCallback(() => {
    resetTourStorage();
    setIsCompleted(false);
    console.log('[useTour] Tour resetado');
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
        console.log('[useTour] Auto-iniciando tour após 1s');
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

// Hook simplificado para apenas verificar se deve mostrar tour
export const useShouldShowTour = (): boolean => {
  const [shouldShow, setShouldShow] = useState(false);

  useEffect(() => {
    const completed = isTourCompleted();
    setShouldShow(!completed);
  }, []);

  return shouldShow;
};

// Hook para tracking de progresso do tour
export const useTourProgress = () => {
  const [progress, setProgress] = useState({
    started: false,
    completed: false,
    startedAt: null as string | null,
    completedAt: null as string | null,
    cancelCount: 0,
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const completed = localStorage.getItem('tour_operacional_completed') === 'true';
    const completedAt = localStorage.getItem('tour_operacional_completed_at');
    const startedAt = localStorage.getItem('tour_operacional_started_at');
    const cancelCount = parseInt(localStorage.getItem('tour_operacional_cancel_count') || '0', 10);

    setProgress({
      started: !!startedAt,
      completed,
      startedAt,
      completedAt,
      cancelCount,
    });
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
