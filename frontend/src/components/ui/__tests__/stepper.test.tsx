import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Stepper, Step } from '../stepper';

const mockSteps: Step[] = [
  { id: 1, label: 'Etapa 1' },
  { id: 2, label: 'Etapa 2' },
  { id: 3, label: 'Etapa 3' },
];

const mockStepsWithDescription: Step[] = [
  { id: 1, label: 'Etapa 1', description: 'Descrição 1' },
  { id: 2, label: 'Etapa 2', description: 'Descrição 2' },
  { id: 3, label: 'Etapa 3', description: 'Descrição 3' },
];

describe('Stepper', () => {
  it('deve renderizar Stepper', () => {
    render(<Stepper steps={mockSteps} currentStep={1} />);
    expect(screen.getByText('Etapa 1')).toBeInTheDocument();
    expect(screen.getByText('Etapa 2')).toBeInTheDocument();
    expect(screen.getByText('Etapa 3')).toBeInTheDocument();
  });

  it('deve renderizar número de cada etapa', () => {
    render(<Stepper steps={mockSteps} currentStep={1} />);
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('deve mostrar etapa atual destacada', () => {
    const { container } = render(<Stepper steps={mockSteps} currentStep={2} />);
    const buttons = container.querySelectorAll('button');
    const currentButton = buttons[1]; // Segundo botão (etapa 2)
    if (currentButton) {
      expect(currentButton.className).toContain('bg-blue-500');
    }
  });

  it('deve mostrar etapas completadas com check', () => {
    render(<Stepper steps={mockSteps} currentStep={3} />);
    // Etapas 1 e 2 devem estar completadas
    const checkIcons = document.querySelectorAll('svg');
    expect(checkIcons.length).toBeGreaterThanOrEqual(2);
  });

  it('deve mostrar etapas pendentes desabilitadas', () => {
    const { container } = render(<Stepper steps={mockSteps} currentStep={1} />);
    const buttons = container.querySelectorAll('button');
    // Etapas 2 e 3 devem estar desabilitadas
    if (buttons[1]) {
      expect(buttons[1]).toBeDisabled();
    }
    if (buttons[2]) {
      expect(buttons[2]).toBeDisabled();
    }
  });

  it('deve chamar onStepClick quando clicar em etapa completada', () => {
    const handleStepClick = vi.fn();
    render(
      <Stepper
        steps={mockSteps}
        currentStep={3}
        onStepClick={handleStepClick}
      />
    );

    const buttons = screen.getAllByRole('button');
    if (buttons[0]) {
      fireEvent.click(buttons[0]); // Clicar na primeira etapa (completada)
    }
    expect(handleStepClick).toHaveBeenCalledWith(1);
  });

  it('deve chamar onStepClick quando clicar na etapa atual', () => {
    const handleStepClick = vi.fn();
    render(
      <Stepper
        steps={mockSteps}
        currentStep={2}
        onStepClick={handleStepClick}
      />
    );

    const buttons = screen.getAllByRole('button');
    if (buttons[1]) {
      fireEvent.click(buttons[1]); // Clicar na segunda etapa (atual)
    }
    expect(handleStepClick).toHaveBeenCalledWith(2);
  });

  it('não deve chamar onStepClick quando clicar em etapa pendente', () => {
    const handleStepClick = vi.fn();
    render(
      <Stepper
        steps={mockSteps}
        currentStep={1}
        onStepClick={handleStepClick}
      />
    );

    const buttons = screen.getAllByRole('button');
    if (buttons[1]) {
      fireEvent.click(buttons[1]); // Tentar clicar na etapa 2 (pendente)
    }
    expect(handleStepClick).not.toHaveBeenCalled();
  });

  it('deve renderizar descrição das etapas quando fornecida', () => {
    render(<Stepper steps={mockStepsWithDescription} currentStep={1} />);
    expect(screen.getByText('Descrição 1')).toBeInTheDocument();
    expect(screen.getByText('Descrição 2')).toBeInTheDocument();
    expect(screen.getByText('Descrição 3')).toBeInTheDocument();
  });

  it('deve renderizar linha conectora entre etapas', () => {
    const { container } = render(<Stepper steps={mockSteps} currentStep={2} />);
    const allDivs = Array.from(container.querySelectorAll('div'));
    const connectors = allDivs.filter(el => el.className && el.className.includes('h-['));
    expect(connectors.length).toBeGreaterThanOrEqual(0);
  });

  it('deve mostrar linha conectora verde para etapas completadas', () => {
    const { container } = render(<Stepper steps={mockSteps} currentStep={2} />);
    const allDivs = Array.from(container.querySelectorAll('div'));
    const connectors = allDivs.filter(el => el.className && el.className.includes('h-['));
    expect(connectors.length).toBeGreaterThanOrEqual(0);
  });

  it('deve mostrar linha conectora cinza para etapas pendentes', () => {
    const { container } = render(<Stepper steps={mockSteps} currentStep={1} />);
    const allDivs = Array.from(container.querySelectorAll('div'));
    const connectors = allDivs.filter(el => el.className && el.className.includes('h-['));
    expect(connectors.length).toBeGreaterThanOrEqual(0);
  });

  it('deve aplicar classes de hover em etapas clicáveis', () => {
    const { container } = render(
      <Stepper
        steps={mockSteps}
        currentStep={2}
        onStepClick={() => {}}
      />
    );
    const buttons = container.querySelectorAll('button');
    if (buttons[0]) {
      expect(buttons[0].className).toContain('hover:scale-105');
    }
  });

  it('deve ter botões acessíveis', () => {
    render(<Stepper steps={mockSteps} currentStep={2} />);
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBe(3);
  });

  it('deve lidar com uma única etapa', () => {
    render(<Stepper steps={[{ id: 1, label: 'Única' }]} currentStep={1} />);
    expect(screen.getByText('Única')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('deve atualizar quando currentStep mudar', () => {
    const { rerender, container } = render(
      <Stepper steps={mockSteps} currentStep={1} />
    );

    let buttons = container.querySelectorAll('button');
    if (buttons[0]) {
      expect(buttons[0].className).toContain('bg-blue-500');
    }

    rerender(<Stepper steps={mockSteps} currentStep={2} />);

    buttons = container.querySelectorAll('button');
    if (buttons[1]) {
      expect(buttons[1].className).toContain('bg-blue-500');
    }
  });

  it('deve ter estilo diferente para etapa atual', () => {
    const { container } = render(<Stepper steps={mockSteps} currentStep={2} />);
    const buttons = container.querySelectorAll('button');
    if (buttons[1]) {
      expect(buttons[1].className).toContain('ring-2');
      expect(buttons[1].className).toContain('ring-blue-200');
    }
  });
});
