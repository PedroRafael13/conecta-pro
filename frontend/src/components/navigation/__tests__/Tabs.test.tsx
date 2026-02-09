import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

interface Tab {
  id: string;
  label: string;
  disabled?: boolean;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className
}) => {
  return (
    <div className={className} data-testid="tabs" role="tablist">
      <div className="flex border-b border-border">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-disabled={tab.disabled}
            onClick={() => !tab.disabled && onChange(tab.id)}
            disabled={tab.disabled}
            className={`
              px-4 py-2 font-medium text-sm transition-colors
              ${activeTab === tab.id
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'}
              ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
            data-testid={`tab-${tab.id}`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
};

Tabs.displayName = 'Tabs';

describe('Tabs', () => {
  const mockTabs: Tab[] = [
    { id: 'tab1', label: 'Geral' },
    { id: 'tab2', label: 'Configurações' },
    { id: 'tab3', label: 'Avançado', disabled: true }
  ];

  const defaultProps = {
    tabs: mockTabs,
    activeTab: 'tab1',
    onChange: vi.fn()
  };

  it('renderiza tabs com items', () => {
    render(<Tabs {...defaultProps} />);
    expect(screen.getByTestId('tabs')).toBeInTheDocument();
  });

  it('tem role tablist', () => {
    render(<Tabs {...defaultProps} />);
    expect(screen.getByRole('tablist')).toBeInTheDocument();
  });

  it('renderiza todos os tabs', () => {
    render(<Tabs {...defaultProps} />);
    expect(screen.getByText('Geral')).toBeInTheDocument();
    expect(screen.getByText('Configurações')).toBeInTheDocument();
    expect(screen.getByText('Avançado')).toBeInTheDocument();
  });

  it('tab ativo tem aria-selected true', () => {
    render(<Tabs {...defaultProps} activeTab="tab1" />);
    const tab = screen.getByTestId('tab-tab1');
    expect(tab).toHaveAttribute('aria-selected', 'true');
  });

  it('tabs inativos tem aria-selected false', () => {
    render(<Tabs {...defaultProps} activeTab="tab1" />);
    const tab = screen.getByTestId('tab-tab2');
    expect(tab).toHaveAttribute('aria-selected', 'false');
  });

  it('tab ativo tem estilo de borda primária', () => {
    render(<Tabs {...defaultProps} activeTab="tab1" />);
    const tab = screen.getByTestId('tab-tab1');
    expect(tab.className).toContain('border-primary');
  });

  it('chama onChange ao clicar em tab', () => {
    const handleChange = vi.fn();
    render(<Tabs {...defaultProps} onChange={handleChange} />);

    fireEvent.click(screen.getByTestId('tab-tab2'));
    expect(handleChange).toHaveBeenCalledWith('tab2');
  });

  it('não chama onChange ao clicar em tab desabilitado', () => {
    const handleChange = vi.fn();
    render(<Tabs {...defaultProps} onChange={handleChange} />);

    fireEvent.click(screen.getByTestId('tab-tab3'));
    expect(handleChange).not.toHaveBeenCalled();
  });

  it('tab desabilitado tem aria-disabled true', () => {
    render(<Tabs {...defaultProps} />);
    const tab = screen.getByTestId('tab-tab3');
    expect(tab).toHaveAttribute('aria-disabled', 'true');
  });

  it('tab desabilitado está desabilitado', () => {
    render(<Tabs {...defaultProps} />);
    const tab = screen.getByTestId('tab-tab3');
    expect(tab).toBeDisabled();
  });

  it('tab desabilitado tem cursor not-allowed', () => {
    render(<Tabs {...defaultProps} />);
    const tab = screen.getByTestId('tab-tab3');
    expect(tab.className).toContain('cursor-not-allowed');
  });

  it('tabs inativos têm hover', () => {
    render(<Tabs {...defaultProps} activeTab="tab1" />);
    const tab = screen.getByTestId('tab-tab2');
    expect(tab.className).toContain('hover:text-foreground');
  });

  it('aplica classe customizada', () => {
    render(<Tabs {...defaultProps} className="custom-tabs" />);
    const tabs = screen.getByTestId('tabs');
    expect(tabs.className).toContain('custom-tabs');
  });

  it('tem displayName correto', () => {
    expect(Tabs.displayName).toBe('Tabs');
  });

  it('atualiza tab ativo quando prop muda', () => {
    const { rerender } = render(<Tabs {...defaultProps} activeTab="tab1" />);

    expect(screen.getByTestId('tab-tab1')).toHaveAttribute('aria-selected', 'true');

    rerender(<Tabs {...defaultProps} activeTab="tab2" />);

    expect(screen.getByTestId('tab-tab2')).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByTestId('tab-tab1')).toHaveAttribute('aria-selected', 'false');
  });
});
