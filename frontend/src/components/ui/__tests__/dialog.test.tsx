import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from '../dialog';

describe('Dialog', () => {
  it('deve renderizar trigger', () => {
    render(
      <Dialog>
        <DialogTrigger>Abrir Dialog</DialogTrigger>
      </Dialog>
    );
    expect(screen.getByText('Abrir Dialog')).toBeInTheDocument();
  });

  it('deve abrir dialog ao clicar no trigger', () => {
    render(
      <Dialog>
        <DialogTrigger>Abrir</DialogTrigger>
        <DialogContent>
          <DialogTitle>Título</DialogTitle>
          <DialogDescription>Descrição</DialogDescription>
        </DialogContent>
      </Dialog>
    );
    fireEvent.click(screen.getByText('Abrir'));
    expect(screen.getByText('Título')).toBeInTheDocument();
    expect(screen.getByText('Descrição')).toBeInTheDocument();
  });

  it('deve renderizar DialogTitle', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Título do Dialog</DialogTitle>
        </DialogContent>
      </Dialog>
    );
    const title = screen.getByText('Título do Dialog');
    expect(title.className).toContain('text-lg');
    expect(title.className).toContain('font-semibold');
  });

  it('deve renderizar DialogDescription', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogDescription>Descrição do dialog</DialogDescription>
        </DialogContent>
      </Dialog>
    );
    const desc = screen.getByText('Descrição do dialog');
    expect(desc.className).toContain('text-sm');
    expect(desc.className).toContain('text-muted-foreground');
  });

  it('deve renderizar DialogHeader', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogHeader>Cabeçalho</DialogHeader>
        </DialogContent>
      </Dialog>
    );
    expect(screen.getByText('Cabeçalho')).toBeInTheDocument();
  });

  it('deve renderizar DialogFooter', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogFooter>
            <button>Botão 1</button>
            <button>Botão 2</button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
    expect(screen.getByText('Botão 1')).toBeInTheDocument();
    expect(screen.getByText('Botão 2')).toBeInTheDocument();
  });

  it('deve aplicar classe customizada no DialogHeader', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogHeader className="custom-header">Header</DialogHeader>
        </DialogContent>
      </Dialog>
    );
    const header = screen.getByText('Header');
    expect(header.className).toContain('custom-header');
  });

  it('deve aplicar classe customizada no DialogFooter', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogFooter className="custom-footer">
            <button>Botão</button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
    const footer = screen.getByText('Botão').parentElement;
    expect(footer?.className).toContain('custom-footer');
  });

  it('deve aplicar classe customizada no DialogTitle', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle className="custom-title">Título</DialogTitle>
        </DialogContent>
      </Dialog>
    );
    const title = screen.getByText('Título');
    expect(title.className).toContain('custom-title');
  });

  it('deve aplicar classe customizada no DialogDescription', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogDescription className="custom-desc">Descrição</DialogDescription>
        </DialogContent>
      </Dialog>
    );
    const desc = screen.getByText('Descrição');
    expect(desc.className).toContain('custom-desc');
  });

  it('deve ter displayName correto para DialogHeader', () => {
    expect(DialogHeader.displayName).toBe('DialogHeader');
  });

  it('deve ter displayName correto para DialogFooter', () => {
    expect(DialogFooter.displayName).toBe('DialogFooter');
  });

  it('deve encaminhar ref corretamente no DialogTitle', () => {
    const ref = { current: null as HTMLHeadingElement | null };
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle ref={ref}>Título</DialogTitle>
        </DialogContent>
      </Dialog>
    );
    expect(ref.current).toBeInstanceOf(HTMLHeadingElement);
  });

  it('deve encaminhar ref corretamente no DialogDescription', () => {
    const ref = { current: null as HTMLParagraphElement | null };
    render(
      <Dialog open>
        <DialogContent>
          <DialogDescription ref={ref}>Descrição</DialogDescription>
        </DialogContent>
      </Dialog>
    );
    expect(ref.current).toBeInstanceOf(HTMLParagraphElement);
  });

  it('deve renderizar botão de fechar com ícone X', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Título</DialogTitle>
        </DialogContent>
      </Dialog>
    );
    expect(screen.getByText('Close')).toBeInTheDocument();
  });

  it('deve renderizar DialogClose personalizado', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Título</DialogTitle>
          <DialogClose asChild>
            <button>Fechar Customizado</button>
          </DialogClose>
        </DialogContent>
      </Dialog>
    );
    expect(screen.getByText('Fechar Customizado')).toBeInTheDocument();
  });

  it('deve renderizar dialog completo', () => {
    render(
      <Dialog>
        <DialogTrigger>Abrir Dialog</DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Título Completo</DialogTitle>
            <DialogDescription>Descrição Completa</DialogDescription>
          </DialogHeader>
          <div>Conteúdo do dialog</div>
          <DialogFooter>
            <button>Cancelar</button>
            <button>Salvar</button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );

    fireEvent.click(screen.getByText('Abrir Dialog'));

    expect(screen.getByText('Título Completo')).toBeInTheDocument();
    expect(screen.getByText('Descrição Completa')).toBeInTheDocument();
    expect(screen.getByText('Conteúdo do dialog')).toBeInTheDocument();
    expect(screen.getByText('Cancelar')).toBeInTheDocument();
    expect(screen.getByText('Salvar')).toBeInTheDocument();
  });

  it('deve ter estilo de posicionamento central', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Título</DialogTitle>
        </DialogContent>
      </Dialog>
    );
    const content = screen.getByText('Título').closest('[class*="fixed"]');
    expect(content).toBeInTheDocument();
  });

  it('deve ter largura máxima definida', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Título</DialogTitle>
        </DialogContent>
      </Dialog>
    );
    const content = screen.getByText('Título').closest('[class*="max-w-lg"]');
    expect(content).toBeInTheDocument();
  });
});
