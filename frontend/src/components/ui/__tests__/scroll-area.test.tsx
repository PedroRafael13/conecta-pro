import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ScrollArea } from '../scroll-area';

describe('ScrollArea', () => {
  it('deve renderizar children', () => {
    render(
      <ScrollArea>
        <div data-testid="scroll-content">Conteúdo</div>
      </ScrollArea>
    );
    expect(screen.getByTestId('scroll-content')).toBeInTheDocument();
  });

  it('deve ter classe overflow-auto', () => {
    const { container } = render(
      <ScrollArea>
        <div>Conteúdo</div>
      </ScrollArea>
    );
    const scrollArea = container.firstChild as HTMLElement;
    expect(scrollArea.className).toContain('overflow-auto');
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(
      <ScrollArea className="custom-scroll">
        <div>Conteúdo</div>
      </ScrollArea>
    );
    const scrollArea = container.firstChild as HTMLElement;
    expect(scrollArea.className).toContain('custom-scroll');
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(
      <ScrollArea ref={ref}>
        <div>Conteúdo</div>
      </ScrollArea>
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve renderizar como div', () => {
    const { container } = render(
      <ScrollArea>
        <div>Conteúdo</div>
      </ScrollArea>
    );
    const scrollArea = container.firstChild as HTMLElement;
    expect(scrollArea.tagName).toBe('DIV');
  });

  it('deve propagar props HTML padrão', () => {
    const { container } = render(
      <ScrollArea id="scroll-id" data-testid="scroll-area">
        <div>Conteúdo</div>
      </ScrollArea>
    );
    const scrollArea = container.firstChild as HTMLElement;
    expect(scrollArea.id).toBe('scroll-id');
    expect(scrollArea.getAttribute('data-testid')).toBe('scroll-area');
  });

  it('deve renderizar conteúdo complexo', () => {
    render(
      <ScrollArea>
        <div>
          <h1>Título</h1>
          <p>Parágrafo 1</p>
          <p>Parágrafo 2</p>
          <button>Botão</button>
        </div>
      </ScrollArea>
    );
    expect(screen.getByText('Título')).toBeInTheDocument();
    expect(screen.getByText('Parágrafo 1')).toBeInTheDocument();
    expect(screen.getByText('Parágrafo 2')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('deve renderizar múltiplos filhos', () => {
    render(
      <ScrollArea>
        <div data-testid="item-1">Item 1</div>
        <div data-testid="item-2">Item 2</div>
        <div data-testid="item-3">Item 3</div>
      </ScrollArea>
    );
    expect(screen.getByTestId('item-1')).toBeInTheDocument();
    expect(screen.getByTestId('item-2')).toBeInTheDocument();
    expect(screen.getByTestId('item-3')).toBeInTheDocument();
  });

  it('deve ter displayName correto', () => {
    expect(ScrollArea.displayName).toBe('ScrollArea');
  });

  it('deve preservar estrutura de classes', () => {
    const { container } = render(
      <ScrollArea className="h-64 w-full">
        <div>Conteúdo</div>
      </ScrollArea>
    );
    const scrollArea = container.firstChild as HTMLElement;
    expect(scrollArea.className).toContain('h-64');
    expect(scrollArea.className).toContain('w-full');
    expect(scrollArea.className).toContain('overflow-auto');
  });

  it('deve aceitar style inline', () => {
    const { container } = render(
      <ScrollArea style={{ maxHeight: '300px' }}>
        <div>Conteúdo</div>
      </ScrollArea>
    );
    const scrollArea = container.firstChild as HTMLElement;
    expect(scrollArea.style.maxHeight).toBe('300px');
  });

  it('deve renderizar lista longa de itens', () => {
    const items = Array.from({ length: 100 }, (_, i) => `Item ${i + 1}`);
    render(
      <ScrollArea>
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </ScrollArea>
    );
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 50')).toBeInTheDocument();
    expect(screen.getByText('Item 100')).toBeInTheDocument();
  });

  it('deve funcionar com tabela dentro', () => {
    render(
      <ScrollArea>
        <table>
          <thead>
            <tr>
              <th>Coluna 1</th>
              <th>Coluna 2</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Dado 1</td>
              <td>Dado 2</td>
            </tr>
          </tbody>
        </table>
      </ScrollArea>
    );
    expect(screen.getByText('Coluna 1')).toBeInTheDocument();
    expect(screen.getByText('Dado 1')).toBeInTheDocument();
  });
});
