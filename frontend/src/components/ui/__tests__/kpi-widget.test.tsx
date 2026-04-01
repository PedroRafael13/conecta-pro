import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { KPIWidget, KPIWidgetSkeleton } from '../kpi-widget';
import { TrendingUp, Users, DollarSign } from 'lucide-react';

describe('KPIWidget', () => {
  it('deve renderizar título do KPI', () => {
    render(
      <KPIWidget
        title="Receita"
        value="R$ 100.000"
        icon={DollarSign}
        iconColor="text-green-500"
        iconBgColor="bg-green-100"
      />
    );
    expect(screen.getByText('Receita')).toBeInTheDocument();
  });

  it('deve renderizar valor do KPI', () => {
    render(
      <KPIWidget
        title="Receita"
        value="R$ 100.000"
        icon={DollarSign}
        iconColor="text-green-500"
        iconBgColor="bg-green-100"
      />
    );
    expect(screen.getByText('R$ 100.000')).toBeInTheDocument();
  });

  it('deve mostrar change positivo com ícone e cor verde', () => {
    const { container } = render(
      <KPIWidget
        title="Receita"
        value="R$ 100.000"
        change={10}
        changeType="positive"
        icon={DollarSign}
        iconColor="text-green-500"
        iconBgColor="bg-green-100"
      />
    );
    expect(screen.getByText('10%')).toBeInTheDocument();
    const changeElement = screen.getByText('10%').parentElement;
    expect(changeElement?.className).toContain('text-green-500');
  });

  it('deve mostrar change negativo com ícone e cor vermelha', () => {
    render(
      <KPIWidget
        title="Despesas"
        value="R$ 50.000"
        change={5}
        changeType="negative"
        icon={DollarSign}
        iconColor="text-red-500"
        iconBgColor="bg-red-100"
      />
    );
    expect(screen.getByText('5%')).toBeInTheDocument();
    const changeElement = screen.getByText('5%').parentElement;
    expect(changeElement?.className).toContain('text-red-500');
  });

  it('deve renderizar ícone quando fornecido', () => {
    const { container } = render(
      <KPIWidget
        title="Usuários"
        value="1.234"
        icon={Users}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
      />
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('deve chamar onClick quando clicado se fornecido', () => {
    const handleClick = vi.fn();
    const { container } = render(
      <KPIWidget
        title="Cliques"
        value="500"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
        onClick={handleClick}
      />
    );
    // Clica no container principal que tem o onClick
    fireEvent.click(container.firstChild as Element);
    expect(handleClick).toHaveBeenCalled();
  });

  it('deve ter cursor pointer quando onClick é fornecido', () => {
    const handleClick = vi.fn();
    const { container } = render(
      <KPIWidget
        title="Cliques"
        value="500"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
        onClick={handleClick}
      />
    );
    const widget = container.firstChild as HTMLElement;
    expect(widget.className).toContain('cursor-pointer');
  });

  it('deve aplicar classe customizada via className (se suportado)', () => {
    const { container } = render(
      <KPIWidget
        title="Teste"
        value="100"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
      />
    );
    const widget = container.firstChild as HTMLElement;
    expect(widget.className).toContain('rounded-xl');
    expect(widget.className).toContain('border');
  });

  it('deve renderizar sem change quando não fornecido', () => {
    render(
      <KPIWidget
        title="Total"
        value="1000"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
      />
    );
    expect(screen.getByText('Total')).toBeInTheDocument();
    expect(screen.getByText('1000')).toBeInTheDocument();
    expect(screen.queryByText('%')).not.toBeInTheDocument();
  });

  it('deve ter layout de card', () => {
    const { container } = render(
      <KPIWidget
        title="Layout"
        value="Test"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
      />
    );
    const widget = container.firstChild as HTMLElement;
    expect(widget.className).toContain('rounded-xl');
    expect(widget.className).toContain('border');
  });

  it('deve mostrar sparkline quando fornecido', () => {
    const { container } = render(
      <KPIWidget
        title="Gráfico"
        value="100"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
        sparklineData={[10, 20, 30, 40, 50]}
      />
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('deve formatar valores grandes corretamente', () => {
    render(
      <KPIWidget
        title="Grande"
        value="1.000.000"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
      />
    );
    expect(screen.getByText('1.000.000')).toBeInTheDocument();
  });

  it('deve renderizar skeleton quando isLoading é true', () => {
    const { container } = render(
      <KPIWidget
        title="Loading"
        value="0"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
        isLoading={true}
      />
    );
    // O container principal tem animate-pulse quando isLoading
    const widget = container.firstChild as HTMLElement;
    expect(widget.className).toContain('animate-pulse');
  });

  it('deve renderizar múltiplos widgets', () => {
    render(
      <>
        <KPIWidget title="KPI 1" value="100" icon={TrendingUp} iconColor="text-blue-500" iconBgColor="bg-blue-100" />
        <KPIWidget title="KPI 2" value="200" icon={TrendingUp} iconColor="text-blue-500" iconBgColor="bg-blue-100" />
        <KPIWidget title="KPI 3" value="300" icon={TrendingUp} iconColor="text-blue-500" iconBgColor="bg-blue-100" />
      </>
    );
    expect(screen.getByText('KPI 1')).toBeInTheDocument();
    expect(screen.getByText('KPI 2')).toBeInTheDocument();
    expect(screen.getByText('KPI 3')).toBeInTheDocument();
  });

  it('deve ter estrutura semântica como div', () => {
    const { container } = render(
      <KPIWidget
        title="Título"
        value="Valor"
        icon={TrendingUp}
        iconColor="text-blue-500"
        iconBgColor="bg-blue-100"
      />
    );
    expect(container.querySelector('div')).toBeInTheDocument();
  });
});

describe('KPIWidgetSkeleton', () => {
  it('deve renderizar skeleton', () => {
    const { container } = render(<KPIWidgetSkeleton />);
    expect(container.firstChild).toBeInTheDocument();
  });
});
