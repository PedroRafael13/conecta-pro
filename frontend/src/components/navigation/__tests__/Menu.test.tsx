import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

interface MenuItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  href?: string;
  active?: boolean;
  disabled?: boolean;
  children?: MenuItem[];
}

interface MenuProps {
  items: MenuItem[];
  vertical?: boolean;
  className?: string;
  onItemClick?: (item: MenuItem) => void;
}

const Menu: React.FC<MenuProps> = ({
  items,
  vertical = false,
  className,
  onItemClick
}) => {
  const [expandedItems, setExpandedItems] = React.useState<Set<string>>(new Set());

  const toggleItem = (id: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedItems(newExpanded);
  };

  const renderItem = (item: MenuItem) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.id);

    return (
      <li key={item.id} data-testid={`menu-item-${item.id}`}>
        <button
          onClick={() => {
            if (hasChildren) {
              toggleItem(item.id);
            } else if (!item.disabled) {
              onItemClick?.(item);
            }
          }}
          disabled={item.disabled}
          className={`
            flex items-center gap-2 px-4 py-2 w-full text-left
            ${item.active ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}
            ${item.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
          data-testid={`menu-button-${item.id}`}
        >
          {item.icon && <span data-testid={`menu-icon-${item.id}`}>{item.icon}</span>}
          <span>{item.label}</span>
          {hasChildren && (
            <span data-testid={`menu-arrow-${item.id}`}>
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
        </button>
        {hasChildren && isExpanded && item.children && (
          <ul className="pl-4" data-testid={`submenu-${item.id}`}>
            {item.children.map(renderItem)}
          </ul>
        )}
      </li>
    );
  };

  return (
    <nav className={className} data-testid="menu">
      <ul className={vertical ? 'flex flex-col' : 'flex'}>
        {items.map(renderItem)}
      </ul>
    </nav>
  );
};

Menu.displayName = 'Menu';

describe('Menu', () => {
  const mockItems: MenuItem[] = [
    { id: '1', label: 'Home', href: '/', active: true },
    { id: '2', label: 'Produtos', href: '/produtos' },
    { id: '3', label: 'Sobre', href: '/sobre', disabled: true },
    {
      id: '4',
      label: 'Serviços',
      children: [
        { id: '4-1', label: 'Consultoria', href: '/consultoria' },
        { id: '4-2', label: 'Suporte', href: '/suporte' }
      ]
    }
  ];

  it('renderiza menu com items', () => {
    render(<Menu items={mockItems} />);
    expect(screen.getByTestId('menu')).toBeInTheDocument();
  });

  it('renderiza todos os itens do menu', () => {
    render(<Menu items={mockItems} />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Produtos')).toBeInTheDocument();
    expect(screen.getByText('Sobre')).toBeInTheDocument();
    expect(screen.getByText('Serviços')).toBeInTheDocument();
  });

  it('marca item ativo com estilo correto', () => {
    render(<Menu items={mockItems} />);
    const activeButton = screen.getByTestId('menu-button-1');
    expect(activeButton.className).toContain('bg-primary');
  });

  it('desabilita item quando disabled é true', () => {
    render(<Menu items={mockItems} />);
    const disabledButton = screen.getByTestId('menu-button-3');
    expect(disabledButton).toBeDisabled();
    expect(disabledButton.className).toContain('cursor-not-allowed');
  });

  it('chama onItemClick ao clicar em item', () => {
    const handleClick = vi.fn();
    render(<Menu items={mockItems} onItemClick={handleClick} />);

    fireEvent.click(screen.getByTestId('menu-button-2'));
    expect(handleClick).toHaveBeenCalledWith(mockItems[1]);
  });

  it('não chama onItemClick ao clicar em item desabilitado', () => {
    const handleClick = vi.fn();
    render(<Menu items={mockItems} onItemClick={handleClick} />);

    fireEvent.click(screen.getByTestId('menu-button-3'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('expande submenu ao clicar em item com children', () => {
    render(<Menu items={mockItems} />);

    expect(screen.queryByTestId('submenu-4')).not.toBeInTheDocument();

    fireEvent.click(screen.getByTestId('menu-button-4'));

    expect(screen.getByTestId('submenu-4')).toBeInTheDocument();
    expect(screen.getByText('Consultoria')).toBeInTheDocument();
    expect(screen.getByText('Suporte')).toBeInTheDocument();
  });

  it('colapsa submenu ao clicar novamente', () => {
    render(<Menu items={mockItems} />);

    fireEvent.click(screen.getByTestId('menu-button-4'));
    expect(screen.getByTestId('submenu-4')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('menu-button-4'));
    expect(screen.queryByTestId('submenu-4')).not.toBeInTheDocument();
  });

  it('renderiza ícone quando fornecido', () => {
    const itemsWithIcons: MenuItem[] = [
      { id: '1', label: 'Home', icon: <span data-testid="home-icon">🏠</span> }
    ];
    render(<Menu items={itemsWithIcons} />);
    expect(screen.getByTestId('home-icon')).toBeInTheDocument();
  });

  it('aplica layout vertical quando vertical é true', () => {
    const { container } = render(<Menu items={mockItems} vertical />);
    const ul = container.querySelector('ul');
    expect(ul?.className).toContain('flex-col');
  });

  it('aplica layout horizontal quando vertical é false', () => {
    const { container } = render(<Menu items={mockItems} vertical={false} />);
    const ul = container.querySelector('ul');
    expect(ul?.className).not.toContain('flex-col');
  });

  it('aplica classe customizada', () => {
    render(<Menu items={mockItems} className="custom-menu" />);
    const nav = screen.getByTestId('menu');
    expect(nav.className).toContain('custom-menu');
  });

  it('tem displayName correto', () => {
    expect(Menu.displayName).toBe('Menu');
  });
});
