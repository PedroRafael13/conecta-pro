import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { DocumentVersionHistory } from '../DocumentVersionHistory';

vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

const mockVersionService = vi.hoisted(() => ({
  listByDocument: vi.fn(),
  setCurrent: vi.fn(),
  archive: vi.fn(),
  delete: vi.fn(),
  compare: vi.fn(),
}));

vi.mock('@/services/ged/documentVersionService', () => ({
  documentVersionService: mockVersionService,
}));

vi.mock('@/utils/file-helpers', () => ({
  formatFileSize: vi.fn((bytes: number) => `${bytes} Bytes`),
}));

const mockVersionCurrent = {
  id: 'v1',
  version_number: 2,
  version_label: 'Final',
  version_type: 'major',
  is_current: true,
  status: 'ativa',
  file_name: 'contrato.pdf',
  file_size_bytes: 1024,
  created_by: 'user@test.com',
  created_at: '2024-06-01T10:00:00Z',
  change_summary: 'Versão final aprovada',
  view_count: 5,
  download_count: 2,
};

const mockVersionOld = {
  id: 'v2',
  version_number: 1,
  version_label: '',
  version_type: 'minor',
  is_current: false,
  status: 'ativa',
  file_name: 'contrato_v1.pdf',
  file_size_bytes: 900,
  created_by: 'editor@test.com',
  created_at: '2024-05-01T08:00:00Z',
  change_summary: '',
  view_count: 3,
  download_count: 1,
};

const mockVersionArchived = {
  id: 'v3',
  version_number: 0,
  version_label: '',
  version_type: 'patch',
  is_current: false,
  status: 'arquivada',
  file_name: 'contrato_draft.pdf',
  file_size_bytes: 800,
  created_by: 'user@test.com',
  created_at: '2024-04-01T07:00:00Z',
  change_summary: '',
  view_count: 1,
  download_count: 0,
};

describe('DocumentVersionHistory', () => {
  const onClose = vi.fn();

  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    vi.clearAllMocks();
    mockVersionService.listByDocument.mockResolvedValue([mockVersionCurrent, mockVersionOld]);
    mockVersionService.setCurrent.mockResolvedValue(undefined);
    mockVersionService.archive.mockResolvedValue(undefined);
    mockVersionService.delete.mockResolvedValue(undefined);
    mockVersionService.compare.mockResolvedValue({
      size_diff: 124,
      same_content: false,
    });
    vi.spyOn(window, 'confirm').mockReturnValue(true);
  });

  it('não abre quando open=false', () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={false}
        onClose={onClose}
      />
    );
    expect(screen.queryByText('Histórico de Versões')).not.toBeInTheDocument();
  });

  it('renderiza dialog quando open=true', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Histórico de Versões')).toBeInTheDocument();
    });
  });

  it('chama listByDocument ao abrir', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(mockVersionService.listByDocument).toHaveBeenCalledWith('doc-1');
    });
  });

  it('exibe resumo com total de versões', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // total de versões
    });
  });

  it('exibe versão atual no resumo', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      // version_number 2 is current
      const cells = screen.getAllByText('2');
      expect(cells.length).toBeGreaterThan(0);
    });
  });

  it('exibe badge "Atual" para versão corrente', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Atual')).toBeInTheDocument();
    });
  });

  it('mostra version_label quando presente', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText(/Final/)).toBeInTheDocument();
    });
  });

  it('mostra change_summary quando presente', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Versão final aprovada')).toBeInTheDocument();
    });
  });

  it('mostra botão "Definir como Atual" para versão não atual e ativa', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Definir como Atual')).toBeInTheDocument();
    });
  });

  it('chama setCurrent ao clicar em "Definir como Atual"', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Definir como Atual')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Definir como Atual'));

    await waitFor(() => {
      expect(mockVersionService.setCurrent).toHaveBeenCalledWith('v2');
    });
  });

  it('mostra botão "Comparar" para versão não última', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Comparar')).toBeInTheDocument();
    });
  });

  it('exibe resultado de comparação ao clicar em Comparar', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Comparar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Comparar'));

    await waitFor(() => {
      expect(screen.getByText(/Comparação:/)).toBeInTheDocument();
      expect(screen.getByText('Diferente')).toBeInTheDocument();
    });
  });

  it('exibe "Idêntico" quando same_content é true', async () => {
    mockVersionService.compare.mockResolvedValue({
      size_diff: 0,
      same_content: true,
    });

    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Comparar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Comparar'));

    await waitFor(() => {
      expect(screen.getByText('Idêntico')).toBeInTheDocument();
    });
  });

  it('exibe "menor" quando size_diff negativo', async () => {
    mockVersionService.compare.mockResolvedValue({
      size_diff: -100,
      same_content: false,
    });

    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Comparar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Comparar'));

    await waitFor(() => {
      expect(screen.getByText(/menor/)).toBeInTheDocument();
    });
  });

  it('fecha comparação ao clicar em "Fechar Comparação"', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Comparar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Comparar'));

    await waitFor(() => {
      expect(screen.getByText('Fechar Comparação')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Fechar Comparação'));

    await waitFor(() => {
      expect(screen.queryByText('Fechar Comparação')).not.toBeInTheDocument();
    });
  });

  it('mostra botão Arquivar para versão ativa não corrente', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Arquivar')).toBeInTheDocument();
    });
  });

  it('chama archive ao clicar em Arquivar', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Arquivar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Arquivar'));

    await waitFor(() => {
      expect(mockVersionService.archive).toHaveBeenCalledWith('v2');
    });
  });

  it('mostra botão Excluir para versão não corrente', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Excluir')).toBeInTheDocument();
    });
  });

  it('chama delete após confirmação', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Excluir')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Excluir'));

    await waitFor(() => {
      expect(mockVersionService.delete).toHaveBeenCalledWith('v2');
    });
  });

  it('não exclui se confirmação negada', async () => {
    vi.spyOn(window, 'confirm').mockReturnValueOnce(false);

    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Excluir')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Excluir'));

    await waitFor(() => {
      expect(mockVersionService.delete).not.toHaveBeenCalled();
    });
  });

  it('mostra loading spinner durante carregamento', async () => {
    let resolvePromise: (value: any) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockVersionService.listByDocument.mockReturnValueOnce(pendingPromise);

    const { container } = render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );

    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
    resolvePromise!([]);
  });

  it('exibe dash quando não há versão atual', async () => {
    mockVersionService.listByDocument.mockResolvedValue([mockVersionOld]);

    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('-')).toBeInTheDocument();
    });
  });

  it('exibe status arquivada para versão arquivada', async () => {
    mockVersionService.listByDocument.mockResolvedValue([mockVersionCurrent, mockVersionArchived]);

    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('arquivada')).toBeInTheDocument();
    });
  });

  it('chama onClose ao clicar em Fechar', async () => {
    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Fechar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Fechar'));
    expect(onClose).toHaveBeenCalled();
  });

  it('exibe erro ao falhar no carregamento de versões', async () => {
    const { toast } = await import('sonner');
    mockVersionService.listByDocument.mockRejectedValueOnce({
      response: { data: { detail: 'Acesso negado' } },
    });

    render(
      <DocumentVersionHistory
        documentId="doc-1"
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Erro ao carregar versões', expect.anything());
    });
  });
});
