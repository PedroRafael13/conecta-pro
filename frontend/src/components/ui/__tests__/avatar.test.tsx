import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Avatar, AvatarFallback } from '../avatar';

describe('Avatar', () => {
  it('deve renderizar Avatar', () => {
    render(<Avatar data-testid="avatar" />);
    expect(screen.getByTestId('avatar')).toBeInTheDocument();
  });

  it('deve ter classe de rounded-full', () => {
    const { container } = render(<Avatar />);
    const avatar = container.querySelector('div');
    expect(avatar?.className).toContain('rounded-full');
  });

  it('deve ter dimensões padrão h-10 w-10', () => {
    const { container } = render(<Avatar />);
    const avatar = container.querySelector('div');
    expect(avatar?.className).toContain('h-10');
    expect(avatar?.className).toContain('w-10');
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(<Avatar className="custom-class" />);
    const avatar = container.querySelector('div');
    expect(avatar?.className).toContain('custom-class');
  });

  it('deve renderizar children', () => {
    render(
      <Avatar>
        <span data-testid="child">Conteúdo</span>
      </Avatar>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(<Avatar ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve ter displayName correto', () => {
    expect(Avatar.displayName).toBe('Avatar');
  });

  describe('AvatarFallback', () => {
    it('deve renderizar AvatarFallback', () => {
      render(<AvatarFallback data-testid="fallback">AB</AvatarFallback>);
      expect(screen.getByTestId('fallback')).toBeInTheDocument();
    });

    it('deve renderizar texto dentro do fallback', () => {
      render(<AvatarFallback>AB</AvatarFallback>);
      expect(screen.getByText('AB')).toBeInTheDocument();
    });

    it('deve ter classe bg-muted', () => {
      const { container } = render(<AvatarFallback>AB</AvatarFallback>);
      const fallback = container.querySelector('div');
      expect(fallback?.className).toContain('bg-muted');
    });

    it('deve ter classe rounded-full', () => {
      const { container } = render(<AvatarFallback>AB</AvatarFallback>);
      const fallback = container.querySelector('div');
      expect(fallback?.className).toContain('rounded-full');
    });

    it('deve ter flex center', () => {
      const { container } = render(<AvatarFallback>AB</AvatarFallback>);
      const fallback = container.querySelector('div');
      expect(fallback?.className).toContain('flex');
      expect(fallback?.className).toContain('items-center');
      expect(fallback?.className).toContain('justify-center');
    });

    it('deve aplicar classe customizada', () => {
      const { container } = render(
        <AvatarFallback className="custom-fallback">AB</AvatarFallback>
      );
      const fallback = container.querySelector('div');
      expect(fallback?.className).toContain('custom-fallback');
    });

    it('deve preencher todo o espaço do avatar', () => {
      const { container } = render(<AvatarFallback>AB</AvatarFallback>);
      const fallback = container.querySelector('div');
      expect(fallback?.className).toContain('h-full');
      expect(fallback?.className).toContain('w-full');
    });

    it('deve encaminhar ref corretamente', () => {
      const ref = { current: null as HTMLDivElement | null };
      render(<AvatarFallback ref={ref}>AB</AvatarFallback>);
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });

    it('deve ter displayName correto', () => {
      expect(AvatarFallback.displayName).toBe('AvatarFallback');
    });

    it('deve renderizar Avatar com AvatarFallback', () => {
      render(
        <Avatar>
          <AvatarFallback>JD</AvatarFallback>
        </Avatar>
      );
      expect(screen.getByText('JD')).toBeInTheDocument();
    });
  });
});
