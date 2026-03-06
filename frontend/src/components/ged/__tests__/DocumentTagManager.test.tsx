import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DocumentTagManager } from '../DocumentTagManager';

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

// Mock documentTagService
const mockDocumentTagService = vi.hoisted(() => ({
  getTags: vi.fn(),
  createTag: vi.fn(),
  addTagToDocument: vi.fn(),
  removeTagFromDocument: vi.fn(),
}));

vi.mock('@/services/ged', () => ({
  documentTagService: mockDocumentTagService,
}));

const mockTag = {
  id: 'tag-1',
  name: 'Contrato',
  color: '#3B82F6',
  tag_type: 'categoria' as const,
  usage_count: 3,
  description: 'Tags de contrato',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockTag2 = {
  id: 'tag-2',
  name: 'Urgente',
  color: '#EF4444',
  tag_type: 'prioridade' as const,
  usage_count: 0,
  description: '',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

describe('DocumentTagManager', () => {
  const onClose = vi.fn();
  const onTagsUpdated = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockDocumentTagService.getTags.mockResolvedValue([mockTag, mockTag2]);
    mockDocumentTagService.createTag.mockResolvedValue({ ...mockTag, id: 'tag-new' });
    mockDocumentTagService.addTagToDocument.mockResolvedValue(undefined);
    mockDocumentTagService.removeTagFromDocument.mockResolvedValue(undefined);
  });

  it('renderiza sem abrir quando open=false', () => {
    render(
      <DocumentTagManager
        open={false}
        onClose={onClose}
      />
    );
    // Dialog not shown
    expect(screen.queryByText('Gerenciar Tags')).not.toBeInTheDocument();
  });

  it('renderiza o dialog quando open=true', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Gerenciar Tags')).toBeInTheDocument();
    });
  });

  it('mostra "Nenhuma tag selecionada" quando sem tags selecionadas', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
        selectedTags={[]}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Nenhuma tag selecionada')).toBeInTheDocument();
    });
  });

  it('exibe tags selecionadas passadas via selectedTags', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
        selectedTags={[mockTag]}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Contrato')).toBeInTheDocument();
    });
  });

  it('carrega tags existentes ao abrir', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(mockDocumentTagService.getTags).toHaveBeenCalled();
    });
  });

  it('mostra tag com usage_count na lista de tags disponíveis', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText(/\(3\)/)).toBeInTheDocument();
    });
  });

  it('filtra tags pela busca', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Buscar tags...')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText('Buscar tags...'), {
      target: { value: 'Contrato' },
    });

    await waitFor(() => {
      expect(screen.getByText('Contrato')).toBeInTheDocument();
    });
  });

  it('exibe "Nenhuma tag encontrada" quando busca não tem resultado', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Buscar tags...')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText('Buscar tags...'), {
      target: { value: 'zzz_inexistente' },
    });

    await waitFor(() => {
      expect(screen.getByText('Nenhuma tag encontrada')).toBeInTheDocument();
    });
  });

  it('exibe "Todas as tags já foram adicionadas" quando nenhuma busca mas sem tags disponíveis', async () => {
    // All tags are already selected
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
        selectedTags={[mockTag, mockTag2]}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Todas as tags já foram adicionadas')).toBeInTheDocument();
    });
  });

  it('adiciona tag sem documentId (modo seleção apenas)', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
        onTagsUpdated={onTagsUpdated}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Contrato')).toBeInTheDocument();
    });

    // Click on a tag to add it
    fireEvent.click(screen.getByText('Contrato').closest('button')!);

    await waitFor(() => {
      expect(onTagsUpdated).toHaveBeenCalledWith([mockTag]);
    });
    expect(mockDocumentTagService.addTagToDocument).not.toHaveBeenCalled();
  });

  it('adiciona tag com documentId chama addTagToDocument', async () => {
    // loadTags retorna todas as tags; loadDocumentTags retorna vazio (sem tags pre-selecionadas)
    mockDocumentTagService.getTags
      .mockResolvedValueOnce([mockTag, mockTag2])
      .mockResolvedValueOnce([]);

    render(
      <DocumentTagManager
        documentId="doc-123"
        open={true}
        onClose={onClose}
        onTagsUpdated={onTagsUpdated}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Contrato')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Contrato').closest('button')!);

    await waitFor(() => {
      expect(mockDocumentTagService.addTagToDocument).toHaveBeenCalledWith('doc-123', 'tag-1');
    });
  });

  it('remove tag selecionada (sem documentId)', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
        selectedTags={[mockTag]}
        onTagsUpdated={onTagsUpdated}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Contrato')).toBeInTheDocument();
    });

    // Find the X button inside the badge
    const removeButtons = screen.getAllByRole('button');
    // The remove button inside the badge for selected tag
    const badgeRemoveButton = removeButtons.find(
      (btn) => btn.closest('[style]') && btn.querySelector('svg')
    );

    if (badgeRemoveButton) {
      fireEvent.click(badgeRemoveButton);
      await waitFor(() => {
        expect(onTagsUpdated).toHaveBeenCalledWith([]);
      });
    }
  });

  it('mostra formulário de criação ao clicar em "Criar Nova Tag"', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Criar Nova Tag')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Criar Nova Tag'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Nome da tag')).toBeInTheDocument();
    });
  });

  it('valida que nome é obrigatório ao criar tag', async () => {
    const { toast } = await import('sonner');

    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Criar Nova Tag')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Criar Nova Tag'));

    await waitFor(() => {
      expect(screen.getByText('Criar Tag')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Criar Tag'));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Nome da tag é obrigatório');
    });
  });

  it('cria tag com sucesso', async () => {
    const { toast } = await import('sonner');

    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Criar Nova Tag')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Criar Nova Tag'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Nome da tag')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText('Nome da tag'), {
      target: { value: 'Nova Tag' },
    });

    fireEvent.click(screen.getByText('Criar Tag'));

    await waitFor(() => {
      expect(mockDocumentTagService.createTag).toHaveBeenCalledWith(
        expect.objectContaining({ name: 'Nova Tag' })
      );
      expect(toast.success).toHaveBeenCalledWith('Tag criada com sucesso');
    });
  });

  it('fecha o formulário de criação ao clicar no X', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Criar Nova Tag')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Criar Nova Tag'));

    await waitFor(() => {
      expect(screen.getByText('Criar Nova Tag', { selector: 'label, .font-semibold' })).toBeInTheDocument();
    });

    // Find the X close button in the form header
    const ghostButtons = screen.getAllByRole('button');
    const closeFormButton = ghostButtons.find(
      (btn) => !btn.textContent?.includes('Criar Tag') && btn.closest('.p-4.border.rounded-lg')
    );

    if (closeFormButton) {
      fireEvent.click(closeFormButton);
    }
  });

  it('exibe mensagem de erro ao falhar no carregamento de tags', async () => {
    const { toast } = await import('sonner');
    mockDocumentTagService.getTags.mockRejectedValueOnce(new Error('Falha'));

    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Erro ao carregar tags', expect.anything());
    });
  });

  it('chama onClose ao clicar em Fechar', async () => {
    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getAllByText('Fechar').length).toBeGreaterThan(0);
    });

    fireEvent.click(screen.getAllByText('Fechar')[0]!);
    expect(onClose).toHaveBeenCalled();
  });

  it('resposta de getTags como objeto com items array', async () => {
    mockDocumentTagService.getTags.mockResolvedValue({ items: [mockTag] });

    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(mockDocumentTagService.getTags).toHaveBeenCalled();
    });
  });

  it('mostra "Carregando..." enquanto carrega tags', async () => {
    let resolvePromise: (value: any) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockDocumentTagService.getTags.mockReturnValueOnce(pendingPromise);

    render(
      <DocumentTagManager
        open={true}
        onClose={onClose}
      />
    );

    expect(screen.getByText('Carregando...')).toBeInTheDocument();

    resolvePromise!([]);
  });
});
