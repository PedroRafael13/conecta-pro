import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogOverlay,
  AlertDialogPortal,
} from '../alert-dialog';

describe('AlertDialog', () => {
  it('deve renderizar AlertDialog quando aberto', () => {
    render(
      <AlertDialog open>
        <AlertDialogContent>
          <AlertDialogTitle>Título do Alerta</AlertDialogTitle>
        </AlertDialogContent>
      </AlertDialog>
    );
    expect(screen.getByText('Título do Alerta')).toBeInTheDocument();
  });

  it('deve renderizar AlertDialog completo com todas as partes', () => {
    render(
      <AlertDialog open>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar Ação</AlertDialogTitle>
            <AlertDialogDescription>
              Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction>Confirmar</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    );

    expect(screen.getByText('Confirmar Ação')).toBeInTheDocument();
    expect(screen.getByText('Esta ação não pode ser desfeita.')).toBeInTheDocument();
    expect(screen.getByText('Cancelar')).toBeInTheDocument();
    expect(screen.getByText('Confirmar')).toBeInTheDocument();
  });

  it('deve chamar onOpenChange ao clicar em Cancelar', () => {
    const handleOpenChange = vi.fn();
    render(
      <AlertDialog open onOpenChange={handleOpenChange}>
        <AlertDialogContent>
          <AlertDialogTitle>Título</AlertDialogTitle>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    );

    const cancelButton = screen.getByText('Cancelar');
    fireEvent.click(cancelButton);
    expect(handleOpenChange).toHaveBeenCalledWith(false);
  });

  it('deve chamar onClick ao clicar em Action', () => {
    const handleAction = vi.fn();
    render(
      <AlertDialog open>
        <AlertDialogContent>
          <AlertDialogTitle>Título</AlertDialogTitle>
          <AlertDialogFooter>
            <AlertDialogAction onClick={handleAction}>
              Confirmar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    );

    const actionButton = screen.getByText('Confirmar');
    fireEvent.click(actionButton);
    expect(handleAction).toHaveBeenCalled();
  });

  it('deve renderizar AlertDialogTrigger', () => {
    render(
      <AlertDialog>
        <AlertDialogTrigger asChild>
          <button>Abrir Alerta</button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogTitle>Título</AlertDialogTitle>
        </AlertDialogContent>
      </AlertDialog>
    );

    expect(screen.getByText('Abrir Alerta')).toBeInTheDocument();
  });

  it('deve abrir AlertDialog ao clicar no trigger', () => {
    render(
      <AlertDialog>
        <AlertDialogTrigger asChild>
          <button>Abrir Alerta</button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogTitle>Título do Alerta</AlertDialogTitle>
        </AlertDialogContent>
      </AlertDialog>
    );

    const trigger = screen.getByText('Abrir Alerta');
    fireEvent.click(trigger);
    expect(screen.getByText('Título do Alerta')).toBeInTheDocument();
  });

  it('deve aplicar classe customizada no AlertDialogTitle', () => {
    render(
      <AlertDialog open>
        <AlertDialogContent>
          <AlertDialogTitle className="custom-title" data-testid="title">Título</AlertDialogTitle>
        </AlertDialogContent>
      </AlertDialog>
    );
    const title = screen.getByTestId('title');
    expect(title?.className).toContain('custom-title');
  });

  it('deve aplicar classe customizada no AlertDialogDescription', () => {
    render(
      <AlertDialog open>
        <AlertDialogContent>
          <AlertDialogDescription className="custom-desc" data-testid="desc">
            Descrição
          </AlertDialogDescription>
        </AlertDialogContent>
      </AlertDialog>
    );
    const desc = screen.getByTestId('desc');
    expect(desc?.className).toContain('custom-desc');
  });

  it('deve ter displayName correto para AlertDialogOverlay', () => {
    expect(AlertDialogOverlay.displayName).toBe('AlertDialogOverlay');
  });

  it('deve ter displayName correto para AlertDialogContent', () => {
    expect(AlertDialogContent.displayName).toBe('AlertDialogContent');
  });

  it('deve ter displayName correto para AlertDialogTitle', () => {
    expect(AlertDialogTitle.displayName).toBe('AlertDialogTitle');
  });

  it('deve ter displayName correto para AlertDialogDescription', () => {
    expect(AlertDialogDescription.displayName).toBe('AlertDialogDescription');
  });

  it('deve ter displayName correto para AlertDialogAction', () => {
    expect(AlertDialogAction.displayName).toBe('AlertDialogAction');
  });

  it('deve ter displayName correto para AlertDialogCancel', () => {
    expect(AlertDialogCancel.displayName).toBe('AlertDialogCancel');
  });

  it('deve exportar AlertDialogPortal', () => {
    expect(AlertDialogPortal).toBeDefined();
  });

  it('deve ter displayName correto para AlertDialogHeader', () => {
    expect(AlertDialogHeader.displayName).toBe('AlertDialogHeader');
  });

  it('deve ter displayName correto para AlertDialogFooter', () => {
    expect(AlertDialogFooter.displayName).toBe('AlertDialogFooter');
  });
});
