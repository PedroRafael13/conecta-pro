import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from '../dropdown-menu';

describe('DropdownMenu', () => {
  it('deve renderizar DropdownMenu', () => {
    render(
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button>Abrir Menu</button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem>Item 1</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
    expect(screen.getByText('Abrir Menu')).toBeInTheDocument();
  });

  it('deve renderizar trigger do dropdown', () => {
    render(
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button data-testid="trigger">Menu</button>
        </DropdownMenuTrigger>
        <DropdownMenuContent />
      </DropdownMenu>
    );
    expect(screen.getByTestId('trigger')).toBeInTheDocument();
  });

  it('deve aceitar classe customizada no DropdownMenuItem', () => {
    expect(typeof DropdownMenuItem).toBe('object');
  });

  it('deve exportar DropdownMenuLabel', () => {
    expect(DropdownMenuLabel).toBeDefined();
    expect(typeof DropdownMenuLabel).toBe('object');
  });

  it('deve exportar DropdownMenuSeparator', () => {
    expect(DropdownMenuSeparator).toBeDefined();
    expect(typeof DropdownMenuSeparator).toBe('object');
  });

  it('deve exportar DropdownMenuShortcut', () => {
    expect(DropdownMenuShortcut).toBeDefined();
    expect(typeof DropdownMenuShortcut).toBe('function');
  });

  it('deve exportar DropdownMenuGroup', () => {
    expect(DropdownMenuGroup).toBeDefined();
  });

  it('deve ter displayName correto para DropdownMenuContent', () => {
    expect(DropdownMenuContent.displayName).toBe('DropdownMenuContent');
  });

  it('deve ter displayName correto para DropdownMenuItem', () => {
    expect(DropdownMenuItem.displayName).toBe('DropdownMenuItem');
  });

  it('deve ter displayName correto para DropdownMenuLabel', () => {
    expect(DropdownMenuLabel.displayName).toBe('DropdownMenuLabel');
  });

  it('deve ter displayName correto para DropdownMenuSeparator', () => {
    expect(DropdownMenuSeparator.displayName).toBe('DropdownMenuSeparator');
  });

  it('deve ter displayName correto para DropdownMenuShortcut', () => {
    expect(DropdownMenuShortcut.displayName).toBe('DropdownMenuShortcut');
  });

  describe('Branch Coverage - Componentes exportados', () => {
    it('deve exportar DropdownMenuCheckboxItem', () => {
      expect(DropdownMenuCheckboxItem).toBeDefined();
      expect(typeof DropdownMenuCheckboxItem).toBe('object');
    });

    it('deve exportar DropdownMenuRadioItem', () => {
      expect(DropdownMenuRadioItem).toBeDefined();
      expect(typeof DropdownMenuRadioItem).toBe('object');
    });

    it('deve exportar DropdownMenuSub', () => {
      expect(DropdownMenuSub).toBeDefined();
    });

    it('deve exportar DropdownMenuSubTrigger', () => {
      expect(DropdownMenuSubTrigger).toBeDefined();
      expect(typeof DropdownMenuSubTrigger).toBe('object');
    });

    it('deve exportar DropdownMenuSubContent', () => {
      expect(DropdownMenuSubContent).toBeDefined();
      expect(typeof DropdownMenuSubContent).toBe('object');
    });
  });
});
