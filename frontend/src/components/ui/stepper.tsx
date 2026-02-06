'use client';

;
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Step {
  id: number;
  label: string;
  description?: string;
}

interface StepperProps {
  steps: Step[];
  currentStep: number;
  onStepClick?: (stepId: number) => void;
}

export function Stepper({ steps, currentStep, onStepClick }: StepperProps) {
  return (
    <div className="w-full py-4">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isCompleted = step.id < currentStep;
          const isCurrent = step.id === currentStep;
          const isClickable = onStepClick && (isCompleted || isCurrent);

          return (
            <div key={step.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center relative">
                <button
                  type="button"
                  onClick={() => isClickable && onStepClick(step.id)}
                  disabled={!isClickable}
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-all',
                    'focus:outline-none focus:ring-2 focus:ring-offset-2',
                    isCompleted &&
                      'bg-emerald-500 text-white focus:ring-emerald-500',
                    isCurrent &&
                      'bg-blue-500 text-white focus:ring-blue-500 ring-2 ring-blue-200',
                    !isCompleted &&
                      !isCurrent &&
                      'bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]',
                    isClickable && 'cursor-pointer hover:scale-105'
                  )}
                >
                  {isCompleted ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <span>{step.id}</span>
                  )}
                </button>
                <div className="mt-2 text-center">
                  <div
                    className={cn(
                      'text-xs font-medium whitespace-nowrap',
                      isCurrent
                        ? 'text-[hsl(var(--foreground))]'
                        : 'text-[hsl(var(--muted-foreground))]'
                    )}
                  >
                    {step.label}
                  </div>
                  {step.description && (
                    <div className="text-[10px] text-[hsl(var(--muted-foreground))] mt-0.5 whitespace-nowrap">
                      {step.description}
                    </div>
                  )}
                </div>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    'flex-1 h-[2px] mx-2 mb-8 transition-colors',
                    isCompleted
                      ? 'bg-emerald-500'
                      : 'bg-[hsl(var(--border))]'
                  )}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
