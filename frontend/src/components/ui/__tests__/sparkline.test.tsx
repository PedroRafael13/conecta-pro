import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { Sparkline } from '../sparkline';

// Mock next/dynamic
vi.mock('next/dynamic', () => ({
  __esModule: true,
  default: () => {
    function DynamicSparkline(props: Record<string, unknown>) {
      return <div data-testid="sparkline-chart" data-props={JSON.stringify(props)}>Chart</div>;
    }
    return DynamicSparkline;
  },
}));

describe('Sparkline', () => {
  it('should render with default props', () => {
    const { container } = render(<Sparkline data={[1, 2, 3, 4, 5]} />);
    expect(container).toBeTruthy();
  });

  it('should render with custom color', () => {
    const { container } = render(<Sparkline data={[1, 2, 3]} color="#ff0000" />);
    expect(container).toBeTruthy();
  });

  it('should render with custom height', () => {
    const { container } = render(<Sparkline data={[1, 2, 3]} height={60} />);
    expect(container).toBeTruthy();
  });

  it('should render with empty data', () => {
    const { container } = render(<Sparkline data={[]} />);
    expect(container).toBeTruthy();
  });

  it('should render with single data point', () => {
    const { container } = render(<Sparkline data={[5]} />);
    expect(container).toBeTruthy();
  });
});
