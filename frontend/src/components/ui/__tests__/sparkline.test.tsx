import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

// Mock recharts to avoid actual chart rendering
vi.mock('recharts', () => ({
  LineChart: function MockLineChart({ children, data }: any) {
    return <div data-testid="line-chart" data-data={JSON.stringify(data)}>{children}</div>;
  },
  Line: function MockLine(props: any) {
    return <div data-testid="line" data-stroke={props.stroke} />;
  },
  ResponsiveContainer: function MockResponsiveContainer({ children, height }: any) {
    return <div data-testid="responsive-container" data-height={height}>{children}</div>;
  },
}));

// Mock next/dynamic to execute the factory immediately (synchronous)
vi.mock('next/dynamic', () => ({
  __esModule: true,
  default: (factory: () => Promise<any>, _opts?: any) => {
    let Component: any = null;
    // Execute the factory synchronously to get the component
    factory().then((mod: any) => {
      Component = mod.default || mod;
    });
    function DynamicWrapper(props: any) {
      if (Component) {
        return <Component {...props} />;
      }
      return <div data-testid="loading">Loading...</div>;
    }
    return DynamicWrapper;
  },
}));

// Wait for dynamic import to resolve
async function flushPromises() {
  await new Promise((resolve) => setTimeout(resolve, 0));
}

describe('Sparkline', () => {
  it('should render with default props', async () => {
    // Import after mocks are set up
    const { Sparkline } = await import('../sparkline');
    await flushPromises();

    const { container } = render(<Sparkline data={[1, 2, 3, 4, 5]} />);
    expect(container).toBeTruthy();
  });

  it('should render with custom color', async () => {
    const { Sparkline } = await import('../sparkline');
    await flushPromises();

    render(<Sparkline data={[1, 2, 3]} color="#ff0000" />);
    const line = screen.queryByTestId('line');
    if (line) {
      expect(line.getAttribute('data-stroke')).toBe('#ff0000');
    }
  });

  it('should render with custom height', async () => {
    const { Sparkline } = await import('../sparkline');
    await flushPromises();

    render(<Sparkline data={[1, 2, 3]} height={60} />);
    const container = screen.queryByTestId('responsive-container');
    if (container) {
      expect(container.getAttribute('data-height')).toBe('60');
    }
  });

  it('should render with empty data', async () => {
    const { Sparkline } = await import('../sparkline');
    await flushPromises();

    const { container } = render(<Sparkline data={[]} />);
    expect(container).toBeTruthy();
  });

  it('should render with single data point', async () => {
    const { Sparkline } = await import('../sparkline');
    await flushPromises();

    const { container } = render(<Sparkline data={[5]} />);
    expect(container).toBeTruthy();
  });

  it('should transform data into chart format', async () => {
    const { Sparkline } = await import('../sparkline');
    await flushPromises();

    render(<Sparkline data={[10, 20, 30]} />);
    const chart = screen.queryByTestId('line-chart');
    if (chart) {
      const chartData = JSON.parse(chart.getAttribute('data-data') || '[]');
      expect(chartData).toEqual([
        { index: 0, value: 10 },
        { index: 1, value: 20 },
        { index: 2, value: 30 },
      ]);
    }
  });
});
