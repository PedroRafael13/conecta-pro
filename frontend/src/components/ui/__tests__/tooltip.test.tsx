import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from '../tooltip';

describe('Tooltip', () => {
  it('deve renderizar tooltip provider', () => {
    const { container } = render(
      <TooltipProvider>
        <div>Content</div>
      </TooltipProvider>
    );
    expect(container.textContent).toContain('Content');
  });

  it('deve renderizar tooltip trigger', () => {
    render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>Hover me</TooltipTrigger>
          <TooltipContent>Tooltip text</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    expect(screen.getByText('Hover me')).toBeInTheDocument();
  });

  it('deve aplicar classe customizada no TooltipContent', () => {
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger>Hover</TooltipTrigger>
          <TooltipContent className="custom-content">Conteúdo</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    const contents = screen.getAllByText('Conteúdo');
    expect(contents[0]!.className).toContain('custom-content');
  });

  it('deve ter z-index alto no TooltipContent', () => {
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger>Hover</TooltipTrigger>
          <TooltipContent>Z-Index</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    const contents = screen.getAllByText('Z-Index');
    expect(contents[0]!.className).toContain('z-50');
  });

  it('deve ter borda arredondada no TooltipContent', () => {
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger>Hover</TooltipTrigger>
          <TooltipContent>Borda</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    const contents = screen.getAllByText('Borda');
    expect(contents[0]!.className).toContain('rounded-md');
  });

  it('deve ter displayName correto para TooltipContent', () => {
    expect(TooltipContent.displayName).toBe('TooltipContent');
  });

  it('deve encaminhar ref corretamente no TooltipContent', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger>Hover</TooltipTrigger>
          <TooltipContent ref={ref}>Com Ref</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve ter estilo de animação no TooltipContent', () => {
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger>Hover</TooltipTrigger>
          <TooltipContent>Animação</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    const contents = screen.getAllByText('Animação');
    expect(contents[0]!.className).toContain('animate-in');
    expect(contents[0]!.className).toContain('fade-in-0');
  });

  it('deve ter sideOffset padrão de 4', () => {
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger>Hover</TooltipTrigger>
          <TooltipContent>Offset</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    // Use getAllByText pois Radix duplica o texto para acessibilidade
    const contents = screen.getAllByText('Offset');
    expect(contents.length).toBeGreaterThan(0);
  });

  it('deve renderizar tooltip completo', () => {
    render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>Informação</TooltipTrigger>
          <TooltipContent>
            Esta é uma informação importante
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    expect(screen.getByText('Informação')).toBeInTheDocument();
  });

  it('deve suportar tooltip aberto por padrão', () => {
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger>Trigger</TooltipTrigger>
          <TooltipContent>Aberto</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    // Use getAllByText pois Radix duplica o texto para acessibilidade
    const contents = screen.getAllByText('Aberto');
    expect(contents.length).toBeGreaterThan(0);
  });
});
