import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

interface Step {
  id: string;
  label: string;
  description?: string;
}

interface StepperProps {
  steps: Step[];
  currentStep: number;
  onStepClick?: (stepId: string) => void;
  className?: string;
}

const Stepper: React.FC<StepperProps> = ({
  steps,
  currentStep,
  onStepClick,
  className
}) => {
  return (
    <div className={className} data-testid="stepper">
      <div className="flex items-center">
        {steps.map((step, index) => {
          const isCompleted = index < currentStep;
          const isCurrent = index === currentStep;
          const isClickable = onStepClick && isCompleted;

          return (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center">
                <button
                  type="button"
                  onClick={() => isClickable && onStepClick(step.id)}
                  disabled={!isCompleted && !isCurrent}
                  className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                    ${isCompleted ? 'bg-green-500 text-white' : ''}
                    ${isCurrent ? 'bg-primary text-primary-foreground ring-2 ring-primary/20' : ''}
                    ${!isCompleted && !isCurrent ? 'bg-muted text-muted-foreground' : ''}
                    ${isClickable ? 'cursor-pointer' : 'cursor-default'}
                  `}
                  data-testid={`step-${step.id}`}
                >
                  {isCompleted ? '✓' : index + 1}
                </button>
                <span className="text-xs mt-1" data-testid={`step-label-${step.id}`}>
                  {step.label}
                </span>
                {step.description && (
                  <span className="text-xs text-muted-foreground" data-testid={`step-desc-${step.id}`}>
                    {step.description}
                  </span>
                )}
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-[2px] mx-2 ${index < currentStep ? 'bg-green-500' : 'bg-muted'}`}
                  data-testid={`connector-${index}`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

Stepper.displayName = 'Stepper';

describe('Stepper', () => {
  const mockSteps: Step[] = [
    { id: 'step1', label: 'Dados Pessoais', description: 'Informações básicas' },
    { id: 'step2', label: 'Endereço', description: 'Localização' },
    { id: 'step3', label: 'Confirmação' }
  ];

  const defaultProps = {
    steps: mockSteps,
    currentStep: 1,
    onChange: vi.fn()
  };

  it('renderiza stepper com steps', () => {
    render(<Stepper steps={mockSteps} currentStep={0} />);
    expect(screen.getByTestId('stepper')).toBeInTheDocument();
  });

  it('renderiza todos os steps', () => {
    render(<Stepper steps={mockSteps} currentStep={0} />);
    expect(screen.getByTestId('step-step1')).toBeInTheDocument();
    expect(screen.getByTestId('step-step2')).toBeInTheDocument();
    expect(screen.getByTestId('step-step3')).toBeInTheDocument();
  });

  it('renderiza labels dos steps', () => {
    render(<Stepper steps={mockSteps} currentStep={0} />);
    expect(screen.getByText('Dados Pessoais')).toBeInTheDocument();
    expect(screen.getByText('Endereço')).toBeInTheDocument();
    expect(screen.getByText('Confirmação')).toBeInTheDocument();
  });

  it('renderiza descrições quando fornecidas', () => {
    render(<Stepper steps={mockSteps} currentStep={0} />);
    expect(screen.getByText('Informações básicas')).toBeInTheDocument();
    expect(screen.getByText('Localização')).toBeInTheDocument();
  });

  it('step atual tem estilo primário', () => {
    render(<Stepper steps={mockSteps} currentStep={1} />);
    const step = screen.getByTestId('step-step2');
    expect(step.className).toContain('bg-primary');
    expect(step.className).toContain('ring-2');
  });

  it('steps completados têm estilo verde', () => {
    render(<Stepper steps={mockSteps} currentStep={2} />);
    const step1 = screen.getByTestId('step-step1');
    const step2 = screen.getByTestId('step-step2');
    expect(step1.className).toContain('bg-green-500');
    expect(step2.className).toContain('bg-green-500');
  });

  it('steps futuros têm estilo muted', () => {
    render(<Stepper steps={mockSteps} currentStep={0} />);
    const step2 = screen.getByTestId('step-step2');
    const step3 = screen.getByTestId('step-step3');
    expect(step2.className).toContain('bg-muted');
    expect(step3.className).toContain('bg-muted');
  });

  it('steps completados mostram checkmark', () => {
    render(<Stepper steps={mockSteps} currentStep={2} />);
    const step1 = screen.getByTestId('step-step1');
    expect(step1.textContent).toBe('✓');
  });

  it('steps não completados mostram número', () => {
    render(<Stepper steps={mockSteps} currentStep={0} />);
    const step1 = screen.getByTestId('step-step1');
    expect(step1.textContent).toBe('1');
  });

  it('renderiza conectores entre steps', () => {
    render(<Stepper steps={mockSteps} currentStep={1} />);
    expect(screen.getByTestId('connector-0')).toBeInTheDocument();
    expect(screen.getByTestId('connector-1')).toBeInTheDocument();
  });

  it('conector tem cor verde quando step anterior está completo', () => {
    render(<Stepper steps={mockSteps} currentStep={2} />);
    const connector = screen.getByTestId('connector-0');
    expect(connector.className).toContain('bg-green-500');
  });

  it('conector tem cor muted quando step anterior não está completo', () => {
    render(<Stepper steps={mockSteps} currentStep={0} />);
    const connector = screen.getByTestId('connector-0');
    expect(connector.className).toContain('bg-muted');
  });

  it('chama onStepClick ao clicar em step completado', () => {
    const handleClick = vi.fn();
    render(
      <Stepper
        steps={mockSteps}
        currentStep={2}
        onStepClick={handleClick}
      />
    );

    fireEvent.click(screen.getByTestId('step-step1'));
    expect(handleClick).toHaveBeenCalledWith('step1');
  });

  it('não chama onStepClick ao clicar em step futuro', () => {
    const handleClick = vi.fn();
    render(
      <Stepper
        steps={mockSteps}
        currentStep={0}
        onStepClick={handleClick}
      />
    );

    fireEvent.click(screen.getByTestId('step-step2'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('steps futuros estão desabilitados', () => {
    render(<Stepper steps={mockSteps} currentStep={0} />);
    const step2 = screen.getByTestId('step-step2');
    expect(step2).toBeDisabled();
  });

  it('aplica classe customizada', () => {
    render(<Stepper steps={mockSteps} currentStep={0} className="custom-stepper" />);
    const stepper = screen.getByTestId('stepper');
    expect(stepper.className).toContain('custom-stepper');
  });

  it('tem displayName correto', () => {
    expect(Stepper.displayName).toBe('Stepper');
  });
});
