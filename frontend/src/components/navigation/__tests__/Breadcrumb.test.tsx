import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

interface BreadcrumbItem {
  label: string;
  href?: string;
  active?: boolean;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  className?: string;
  onItemClick?: (item: BreadcrumbItem, index: number) => void;
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  separator = '/',
  className,
  onItemClick
}) => {
  return (
    <nav aria-label="Breadcrumb" className={className} data-testid="breadcrumb">
      <ol className="flex items-center space-x-2 text-sm">
        {items.map((item, index) => (
          <li key={index} className="flex items-center">
            {index > 0 && (
              <span className="mx-2 text-muted-foreground" data-testid="separator">
                {separator}
              </span>
            )}
            {item.active || !item.href ? (
              <span
                className="text-foreground font-medium"
                aria-current="page"
                data-testid={`breadcrumb-item-${index}`}
              >
                {item.label}
              </span>
            ) : (
              <a
                href={item.href}
                className="text-muted-foreground hover:text-foreground transition-colors"
                onClick={(e) => {
                  e.preventDefault();
                  onItemClick?.(item, index);
                }}
                data-testid={`breadcrumb-link-${index}`}
              >
                {item.label}
              </a>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

Breadcrumb.displayName = 'Breadcrumb';

describe('Breadcrumb', () => {
  const mockItems: BreadcrumbItem[] = [
    { label: 'Home', href: '/' },
    { label: 'Produtos', href: '/produtos' },
    { label: 'Eletrônicos', active: true }
  ];

  it('renderiza breadcrumb com items', () => {
    render(<Breadcrumb items={mockItems} />);
    expect(screen.getByTestId('breadcrumb')).toBeInTheDocument();
  });

  it('tem aria-label correto', () => {
    render(<Breadcrumb items={mockItems} />);
    const nav = screen.getByLabelText('Breadcrumb');
    expect(nav).toBeInTheDocument();
  });

  it('renderiza todos os itens', () => {
    render(<Breadcrumb items={mockItems} />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Produtos')).toBeInTheDocument();
    expect(screen.getByText('Eletrônicos')).toBeInTheDocument();
  });

  it('renderiza item ativo sem link', () => {
    render(<Breadcrumb items={mockItems} />);
    const activeItem = screen.getByTestId('breadcrumb-item-2');
    expect(activeItem.tagName.toLowerCase()).toBe('span');
    expect(activeItem).toHaveAttribute('aria-current', 'page');
  });

  it('renderiza itens com href como links', () => {
    render(<Breadcrumb items={mockItems} />);
    const homeLink = screen.getByTestId('breadcrumb-link-0');
    expect(homeLink.tagName.toLowerCase()).toBe('a');
    expect(homeLink).toHaveAttribute('href', '/');
  });

  it('renderiza separadores entre itens', () => {
    render(<Breadcrumb items={mockItems} />);
    const separators = screen.getAllByTestId('separator');
    expect(separators).toHaveLength(2);
  });

  it('usapor padrão separador /', () => {
    render(<Breadcrumb items={mockItems} />);
    const separators = screen.getAllByTestId('separator');
    expect(separators[0]?.textContent).toBe('/');
  });

  it('aceita separador customizado', () => {
    render(<Breadcrumb items={mockItems} separator=">" />);
    const separators = screen.getAllByTestId('separator');
    expect(separators[0]?.textContent).toBe('>');
  });

  it('aceita separador como elemento React', () => {
    render(<Breadcrumb items={mockItems} separator={<span data-testid="custom-sep">→</span>} />);
    expect(screen.getAllByTestId('custom-sep')).toHaveLength(2);
  });

  it('chama onItemClick ao clicar em link', () => {
    const handleClick = vi.fn();
    render(<Breadcrumb items={mockItems} onItemClick={handleClick} />);

    const homeLink = screen.getByTestId('breadcrumb-link-0');
    fireEvent.click(homeLink);

    expect(handleClick).toHaveBeenCalledWith(mockItems[0], 0);
  });

  it('aplica classe customizada', () => {
    render(<Breadcrumb items={mockItems} className="custom-breadcrumb" />);
    const nav = screen.getByTestId('breadcrumb');
    expect(nav.className).toContain('custom-breadcrumb');
  });

  it('tem displayName correto', () => {
    expect(Breadcrumb.displayName).toBe('Breadcrumb');
  });

  it('funciona com item único', () => {
    render(<Breadcrumb items={[{ label: 'Home', active: true }]} />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.queryByTestId('separator')).not.toBeInTheDocument();
  });

  it('aplica estilo de hover em links', () => {
    render(<Breadcrumb items={mockItems} />);
    const link = screen.getByTestId('breadcrumb-link-0');
    expect(link.className).toContain('hover:text-foreground');
  });
});
