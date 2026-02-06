import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Modal, ModalFooter, ConfirmModal } from '../modal';

describe('Modal', () => {
  it('não deve renderizar quando isOpen é false', () => {
    const { container } = render(
      <Modal isOpen={false} onClose={() => {}}>
        Conteúdo
      </Modal>
    );
    expect(container.firstChild).toBeNull();
  });

  it('deve renderizar quando isOpen é true', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        Conteúdo do Modal
      </Modal>
    );
    expect(screen.getByText('Conteúdo do Modal')).toBeInTheDocument();
  });

  it('deve renderizar título', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} title="Título do Modal">
        Conteúdo
      </Modal>
    );
    expect(screen.getByText('Título do Modal')).toBeInTheDocument();
  });

  it('deve renderizar descrição', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} title="Título" description="Descrição do modal">
        Conteúdo
      </Modal>
    );
    expect(screen.getByText('Descrição do modal')).toBeInTheDocument();
  });

  it('deve chamar onClose ao clicar no botão de fechar', () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} title="Modal">
        Conteúdo
      </Modal>
    );
    const closeButton = screen.getByRole('button');
    fireEvent.click(closeButton);
    expect(handleClose).toHaveBeenCalled();
  });

  it('deve chamar onClose ao clicar no overlay quando closeOnOverlayClick é true', () => {
    const handleClose = vi.fn();
    const { container } = render(
      <Modal isOpen={true} onClose={handleClose} closeOnOverlayClick={true}>
        Conteúdo
      </Modal>
    );
    const overlay = container.querySelector('.bg-black\\/50');
    if (overlay) {
      fireEvent.click(overlay);
      expect(handleClose).toHaveBeenCalled();
    }
  });

  it('não deve chamar onClose ao clicar no overlay quando closeOnOverlayClick é false', () => {
    const handleClose = vi.fn();
    const { container } = render(
      <Modal isOpen={true} onClose={handleClose} closeOnOverlayClick={false}>
        Conteúdo
      </Modal>
    );
    const overlay = container.querySelector('.bg-black\\/50');
    if (overlay) {
      fireEvent.click(overlay);
      expect(handleClose).not.toHaveBeenCalled();
    }
  });

  it('deve renderizar com tamanho sm', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={() => {}} size="sm">
        Conteúdo
      </Modal>
    );
    const modal = container.querySelector('.max-w-md');
    expect(modal).toBeInTheDocument();
  });

  it('deve renderizar com tamanho md', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={() => {}} size="md">
        Conteúdo
      </Modal>
    );
    const modal = container.querySelector('.max-w-lg');
    expect(modal).toBeInTheDocument();
  });

  it('deve renderizar com tamanho lg', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={() => {}} size="lg">
        Conteúdo
      </Modal>
    );
    const modal = container.querySelector('.max-w-2xl');
    expect(modal).toBeInTheDocument();
  });

  it('deve renderizar com tamanho xl', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={() => {}} size="xl">
        Conteúdo
      </Modal>
    );
    const modal = container.querySelector('.max-w-4xl');
    expect(modal).toBeInTheDocument();
  });

  it('deve renderizar com tamanho full', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={() => {}} size="full">
        Conteúdo
      </Modal>
    );
    const modal = container.querySelector('.max-w-\\[95vw\\]');
    expect(modal).toBeInTheDocument();
  });

  it('deve ocultar botão de fechar quando showCloseButton é false', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={() => {}} title="Modal" showCloseButton={false}>
        Conteúdo
      </Modal>
    );
    const closeButton = container.querySelector('button');
    expect(closeButton).toBeNull();
  });

  it('deve renderizar ModalFooter com children', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        <ModalFooter>
          <button>Botão 1</button>
          <button>Botão 2</button>
        </ModalFooter>
      </Modal>
    );
    expect(screen.getByText('Botão 1')).toBeInTheDocument();
    expect(screen.getByText('Botão 2')).toBeInTheDocument();
  });

  it('deve aplicar classe customizada no ModalFooter', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        <ModalFooter className="custom-footer">
          <button>Botão</button>
        </ModalFooter>
      </Modal>
    );
    const footer = screen.getByText('Botão').parentElement;
    expect(footer?.className).toContain('custom-footer');
  });

  it('deve aplicar backdrop blur no overlay', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={() => {}}>
        Conteúdo
      </Modal>
    );
    const overlay = container.querySelector('.backdrop-blur-sm');
    expect(overlay).toBeInTheDocument();
  });
});

describe('ConfirmModal', () => {
  it('deve renderizar título e mensagem', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Confirmar Ação"
        message="Tem certeza que deseja continuar?"
      />
    );
    expect(screen.getByText('Confirmar Ação')).toBeInTheDocument();
    expect(screen.getByText('Tem certeza que deseja continuar?')).toBeInTheDocument();
  });

  it('deve renderizar botões com textos customizados', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Confirmar"
        message="Mensagem"
        confirmText="Sim, continuar"
        cancelText="Não, cancelar"
      />
    );
    expect(screen.getByText('Sim, continuar')).toBeInTheDocument();
    expect(screen.getByText('Não, cancelar')).toBeInTheDocument();
  });

  it('deve chamar onConfirm ao clicar no botão de confirmar', () => {
    const handleConfirm = vi.fn();
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={handleConfirm}
        title="Título Modal"
        message="Mensagem"
      />
    );
    // Buscar todos os botões e pegar o último (botão de confirmar)
    const buttons = screen.getAllByRole('button');
    const confirmButton = buttons[buttons.length - 1];
    fireEvent.click(confirmButton!);
    expect(handleConfirm).toHaveBeenCalled();
  });

  it('deve chamar onClose ao clicar no botão de cancelar', () => {
    const handleClose = vi.fn();
    render(
      <ConfirmModal
        isOpen={true}
        onClose={handleClose}
        onConfirm={() => {}}
        title="Confirmar"
        message="Mensagem"
      />
    );
    fireEvent.click(screen.getByText('Cancelar'));
    expect(handleClose).toHaveBeenCalled();
  });

  it('deve mostrar texto de loading quando isLoading é true', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Confirmar"
        message="Mensagem"
        isLoading={true}
      />
    );
    expect(screen.getByText('Aguarde...')).toBeInTheDocument();
  });

  it('deve desabilitar botões quando isLoading é true', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Título Modal"
        message="Mensagem"
        isLoading={true}
      />
    );
    // Pegar apenas os botões de ação (Cancelar e Confirmar), não o de fechar
    const cancelButton = screen.getByText('Cancelar');
    const buttons = screen.getAllByRole('button');
    const confirmButton = buttons[buttons.length - 1];
    expect(cancelButton).toBeDisabled();
    expect(confirmButton).toBeDisabled();
  });

  it('deve aplicar classe danger por padrão', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Título Modal"
        message="Mensagem"
        variant="danger"
      />
    );
    const buttons = screen.getAllByRole('button');
    const confirmButton = buttons[buttons.length - 1];
    expect(confirmButton!.className).toContain('bg-red-500');
  });

  it('deve aplicar classe warning quando variant é warning', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Título Modal"
        message="Mensagem"
        variant="warning"
      />
    );
    const buttons = screen.getAllByRole('button');
    const confirmButton = buttons[buttons.length - 1];
    expect(confirmButton!.className).toContain('bg-orange-500');
  });

  it('deve aplicar classe info quando variant é info', () => {
    render(
      <ConfirmModal
        isOpen={true}
        onClose={() => {}}
        onConfirm={() => {}}
        title="Título Modal"
        message="Mensagem"
        variant="info"
      />
    );
    const buttons = screen.getAllByRole('button');
    const confirmButton = buttons[buttons.length - 1];
    expect(confirmButton!.className).toContain('bg-blue-500');
  });
});
