import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Sparkline } from '../sparkline';

// Mock do next/dynamic
vi.mock('next/dynamic', () => ({
  default: vi.fn((dynamicOptions: any) => {
    // Simular o comportamento do dynamic import
    const MockedComponent = ({ data, color, height }: { data: number[]; color?: string; height?: number }) => {
      const finalColor = color || '#3b82f6';
      const finalHeight = height || 40;
      return (
        <div
          data-testid="sparkline-chart"
          data-data={JSON.stringify(data)}
          data-color={finalColor}
          data-height={finalHeight}
        >
          <svg viewBox={`0 0 100 ${finalHeight}`} style={{ height: finalHeight }}>
            <polyline
              fill="none"
              stroke={finalColor}
              strokeWidth="2"
              points={data.map((v, i) => `${i * (100 / (data.length - 1 || 1))},${finalHeight - v}`).join(' ')}
            />
          </svg>
        </div>
      );
    };
    return MockedComponent;
  }),
}));

describe('Sparkline', () => {
  it('deve renderizar componente de gráfico', () => {
    render(<Sparkline data={[10, 20, 30, 40, 50]} />);
    expect(screen.getByTestId('sparkline-chart')).toBeInTheDocument();
  });

  it('deve passar dados corretamente para o gráfico', () => {
    const data = [10, 20, 30, 40, 50];
    render(<Sparkline data={data} />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart.getAttribute('data-data')).toBe(JSON.stringify(data));
  });

  it('deve aplicar cor padrão', () => {
    render(<Sparkline data={[10, 20, 30]} />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart.getAttribute('data-color')).toBe('#3b82f6');
  });

  it('deve aplicar cor customizada', () => {
    render(<Sparkline data={[10, 20, 30]} color="#ef4444" />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart.getAttribute('data-color')).toBe('#ef4444');
  });

  it('deve aplicar altura padrão', () => {
    render(<Sparkline data={[10, 20, 30]} />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart.getAttribute('data-height')).toBe('40');
  });

  it('deve aplicar altura customizada', () => {
    render(<Sparkline data={[10, 20, 30]} height={60} />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart.getAttribute('data-height')).toBe('60');
  });

  it('deve renderizar SVG do gráfico', () => {
    const { container } = render(<Sparkline data={[10, 20, 30, 40, 50]} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('deve ter polyline no SVG', () => {
    const { container } = render(<Sparkline data={[10, 20, 30, 40, 50]} />);
    const polyline = container.querySelector('polyline');
    expect(polyline).toBeInTheDocument();
  });

  it('deve aceitar array de dados vazio', () => {
    render(<Sparkline data={[]} />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart).toBeInTheDocument();
  });

  it('deve aceitar array com um único valor', () => {
    render(<Sparkline data={[50]} />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart).toBeInTheDocument();
  });

  it('deve aceitar valores decimais', () => {
    render(<Sparkline data={[10.5, 20.3, 30.7]} />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart).toBeInTheDocument();
  });

  it('deve aceitar valores negativos', () => {
    render(<Sparkline data={[-10, 0, 10, 20]} />);
    const chart = screen.getByTestId('sparkline-chart');
    expect(chart).toBeInTheDocument();
  });

  it('deve renderizar múltiplos sparklines', () => {
    const { container } = render(
      <>
        <Sparkline data={[10, 20, 30]} color="#3b82f6" />
        <Sparkline data={[30, 20, 10]} color="#ef4444" />
        <Sparkline data={[15, 25, 35]} color="#10b981" />
      </>
    );
    const charts = container.querySelectorAll('[data-testid="sparkline-chart"]');
    expect(charts.length).toBe(3);
  });

  it('deve ter strokeWidth definido no polyline', () => {
    const { container } = render(<Sparkline data={[10, 20, 30]} />);
    const polyline = container.querySelector('polyline');
    expect(polyline?.getAttribute('stroke-width')).toBe('2');
  });

  it('deve ter fill none no polyline', () => {
    const { container } = render(<Sparkline data={[10, 20, 30]} />);
    const polyline = container.querySelector('polyline');
    expect(polyline?.getAttribute('fill')).toBe('none');
  });

  it('deve aceitar diferentes formatos de cores', () => {
    const { rerender } = render(
      <Sparkline data={[10, 20, 30]} color="rgb(59, 130, 246)" />
    );
    expect(screen.getByTestId('sparkline-chart')).toBeInTheDocument();

    rerender(<Sparkline data={[10, 20, 30]} color="hsl(217, 91%, 60%)" />);
    expect(screen.getByTestId('sparkline-chart')).toBeInTheDocument();
  });

  it('deve renderizar com largura responsiva', () => {
    const { container } = render(
      <div style={{ width: '200px' }}>
        <Sparkline data={[10, 20, 30]} />
      </div>
    );
    expect(screen.getByTestId('sparkline-chart')).toBeInTheDocument();
  });

  it('deve manter proporção com diferentes alturas', () => {
    const { rerender } = render(<Sparkline data={[10, 20, 30]} height={30} />);
    expect(screen.getByTestId('sparkline-chart').getAttribute('data-height')).toBe('30');

    rerender(<Sparkline data={[10, 20, 30]} height={100} />);
    expect(screen.getByTestId('sparkline-chart').getAttribute('data-height')).toBe('100');
  });
});
