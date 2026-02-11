import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Toaster } from '../toaster';

const mockToasts: any[] = [];

vi.mock('../use-toast', () => ({
  useToast: () => ({ toasts: mockToasts }),
}));

vi.mock('../toast', () => ({
  Toast: ({ children, ...props }: any) => <div data-testid="toast" {...props}>{children}</div>,
  ToastClose: () => <button data-testid="toast-close">Close</button>,
  ToastDescription: ({ children }: any) => <div data-testid="toast-description">{children}</div>,
  ToastProvider: ({ children }: any) => <div data-testid="toast-provider">{children}</div>,
  ToastTitle: ({ children }: any) => <div data-testid="toast-title">{children}</div>,
  ToastViewport: () => <div data-testid="toast-viewport" />,
}));

describe('Toaster', () => {
  beforeEach(() => {
    mockToasts.length = 0;
  });

  it('should render without toasts', () => {
    render(<Toaster />);
    expect(screen.getByTestId('toast-provider')).toBeInTheDocument();
    expect(screen.getByTestId('toast-viewport')).toBeInTheDocument();
  });

  it('should render toast with title and description', () => {
    mockToasts.push({
      id: '1',
      title: 'Test Title',
      description: 'Test Description',
      open: true,
    });

    render(<Toaster />);
    expect(screen.getByTestId('toast-title')).toHaveTextContent('Test Title');
    expect(screen.getByTestId('toast-description')).toHaveTextContent('Test Description');
  });

  it('should render toast with only title', () => {
    mockToasts.push({
      id: '1',
      title: 'Test Title',
      open: true,
    });

    render(<Toaster />);
    expect(screen.getByTestId('toast-title')).toHaveTextContent('Test Title');
  });

  it('should render toast with only description', () => {
    mockToasts.push({
      id: '1',
      description: 'Test Description',
      open: true,
    });

    render(<Toaster />);
    expect(screen.getByTestId('toast-description')).toHaveTextContent('Test Description');
  });

  it('should render multiple toasts', () => {
    mockToasts.push(
      { id: '1', title: 'Toast 1', open: true },
      { id: '2', title: 'Toast 2', open: true }
    );

    render(<Toaster />);
    const toasts = screen.getAllByTestId('toast');
    expect(toasts).toHaveLength(2);
  });

  it('should render toast with action', () => {
    mockToasts.push({
      id: '1',
      title: 'Test',
      action: <button data-testid="toast-action">Action</button>,
      open: true,
    });

    render(<Toaster />);
    expect(screen.getByTestId('toast-action')).toBeInTheDocument();
  });
});
