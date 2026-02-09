import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../card';

describe('Card', () => {
  it('deve renderizar card com conteúdo', () => {
    render(<Card>Conteúdo do Card</Card>);
    expect(screen.getByText('Conteúdo do Card')).toBeInTheDocument();
  });

  it('deve renderizar com variant padrão', () => {
    const { container } = render(<Card>Default Card</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toBeInTheDocument();
    expect(card.className).toContain('rounded-xl');
    expect(card.className).toContain('p-4');
  });

  it('deve renderizar com variant interactive', () => {
    const { container } = render(<Card variant="interactive">Interactive Card</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('cursor-pointer');
    expect(card.className).toContain('transition-all');
  });

  it('deve renderizar com variant highlighted', () => {
    const { container } = render(<Card variant="highlighted">Highlighted Card</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('shadow-lg');
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(<Card className="custom-card">Custom Card</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('custom-card');
  });

  it('deve renderizar CardHeader', () => {
    render(
      <Card>
        <CardHeader>Cabeçalho</CardHeader>
      </Card>
    );
    expect(screen.getByText('Cabeçalho')).toBeInTheDocument();
  });

  it('deve aplicar espaçamento no CardHeader', () => {
    const { container } = render(
      <Card>
        <CardHeader>Cabeçalho</CardHeader>
      </Card>
    );
    const header = container.querySelector('[class*="flex flex-col"]');
    expect(header).toBeInTheDocument();
  });

  it('deve renderizar CardTitle', () => {
    render(
      <Card>
        <CardTitle>Título do Card</CardTitle>
      </Card>
    );
    const title = screen.getByText('Título do Card');
    expect(title.tagName).toBe('H3');
    expect(title.className).toContain('text-lg');
    expect(title.className).toContain('font-semibold');
  });

  it('deve renderizar CardDescription', () => {
    render(
      <Card>
        <CardDescription>Descrição do card</CardDescription>
      </Card>
    );
    const desc = screen.getByText('Descrição do card');
    expect(desc.tagName).toBe('P');
    expect(desc.className).toContain('text-sm');
  });

  it('deve renderizar CardContent', () => {
    render(
      <Card>
        <CardContent>Conteúdo principal</CardContent>
      </Card>
    );
    expect(screen.getByText('Conteúdo principal')).toBeInTheDocument();
  });

  it('deve renderizar card completo com todos os subcomponentes', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Título</CardTitle>
          <CardDescription>Descrição</CardDescription>
        </CardHeader>
        <CardContent>Conteúdo</CardContent>
      </Card>
    );
    expect(screen.getByText('Título')).toBeInTheDocument();
    expect(screen.getByText('Descrição')).toBeInTheDocument();
    expect(screen.getByText('Conteúdo')).toBeInTheDocument();
  });

  it('deve encaminhar ref corretamente no Card', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(<Card ref={ref}>Card com Ref</Card>);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve encaminhar ref corretamente no CardHeader', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(
      <Card>
        <CardHeader ref={ref}>Header</CardHeader>
      </Card>
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve encaminhar ref corretamente no CardTitle', () => {
    const ref = { current: null as HTMLHeadingElement | null };
    render(
      <Card>
        <CardTitle ref={ref}>Título</CardTitle>
      </Card>
    );
    expect(ref.current).toBeInstanceOf(HTMLHeadingElement);
  });

  it('deve encaminhar ref corretamente no CardDescription', () => {
    const ref = { current: null as HTMLParagraphElement | null };
    render(
      <Card>
        <CardDescription ref={ref}>Descrição</CardDescription>
      </Card>
    );
    expect(ref.current).toBeInstanceOf(HTMLParagraphElement);
  });

  it('deve encaminhar ref corretamente no CardContent', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(
      <Card>
        <CardContent ref={ref}>Conteúdo</CardContent>
      </Card>
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve ter displayName correto para Card', () => {
    expect(Card.displayName).toBe('Card');
  });

  it('deve ter displayName correto para CardHeader', () => {
    expect(CardHeader.displayName).toBe('CardHeader');
  });

  it('deve ter displayName correto para CardTitle', () => {
    expect(CardTitle.displayName).toBe('CardTitle');
  });

  it('deve ter displayName correto para CardDescription', () => {
    expect(CardDescription.displayName).toBe('CardDescription');
  });

  it('deve ter displayName correto para CardContent', () => {
    expect(CardContent.displayName).toBe('CardContent');
  });

  it('deve aplicar classe customizada no CardHeader', () => {
    const { container } = render(
      <Card>
        <CardHeader className="custom-header">Header</CardHeader>
      </Card>
    );
    const header = screen.getByText('Header');
    expect(header.className).toContain('custom-header');
  });

  it('deve aplicar classe customizada no CardTitle', () => {
    render(
      <Card>
        <CardTitle className="custom-title">Título</CardTitle>
      </Card>
    );
    const title = screen.getByText('Título');
    expect(title.className).toContain('custom-title');
  });

  it('deve aplicar classe customizada no CardDescription', () => {
    render(
      <Card>
        <CardDescription className="custom-desc">Descrição</CardDescription>
      </Card>
    );
    const desc = screen.getByText('Descrição');
    expect(desc.className).toContain('custom-desc');
  });

  it('deve aplicar classe customizada no CardContent', () => {
    render(
      <Card>
        <CardContent className="custom-content">Conteúdo</CardContent>
      </Card>
    );
    const content = screen.getByText('Conteúdo');
    expect(content.className).toContain('custom-content');
  });

  it('deve suportar múltiplos cards', () => {
    const { container } = render(
      <>
        <Card>Card 1</Card>
        <Card>Card 2</Card>
        <Card>Card 3</Card>
      </>
    );
    expect(screen.getByText('Card 1')).toBeInTheDocument();
    expect(screen.getByText('Card 2')).toBeInTheDocument();
    expect(screen.getByText('Card 3')).toBeInTheDocument();
  });
});
