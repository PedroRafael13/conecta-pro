'use client';

import { useEffect } from 'react';
import { useTour } from '../hooks/useTour';
import { UserRole } from '../tours/operacionalTour';
import { TourProgress, TourNotification } from './TourTrigger';

// Import CSS customizado
import '../styles/shepherd-custom.css';

interface OperacionalTourProviderProps {
  children: React.ReactNode;
  userRole?: UserRole;
  autoStart?: boolean;
  showNotification?: boolean;
}

export function OperacionalTourProvider({
  children,
  userRole = 'USUARIO',
  autoStart = true,
  showNotification = true,
}: OperacionalTourProviderProps) {
  const { isCompleted } = useTour(userRole, autoStart);

  return (
    <>
      {children}
      <TourProgress />
      {showNotification && !isCompleted && (
        <TourNotification role={userRole} />
      )}
    </>
  );
}
