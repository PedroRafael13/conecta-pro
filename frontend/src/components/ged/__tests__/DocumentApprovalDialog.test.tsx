import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DocumentApprovalDialog } from '../DocumentApprovalDialog';

vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

vi.mock('@/types/generated/ged/conectaPROMóduloGED.schemas', () => ({
  formatFileSize: vi.fn((bytes: number) => `${bytes} B`),
}));

const { mockApprove, mockReject } = vi.hoisted(() => ({
  mockApprove: vi.fn(),
  mockReject: vi.fn(),
}));

vi.mock('@/types/generated/ged/ged-documentos/ged-documentos', () => ({
  approveDocumentApiV1GedDocumentsDocumentIdApprovePost: mockApprove,
  rejectDocumentApiV1GedDocumentsDocumentIdRejectPost: mockReject,
}));

const mockDocument = {
  id: 'doc-123',
  title: 'Contrato de Prestação de Serviços',
  description: 'Contrato referente a serviços de segurança',
  document_type: 'contrato',
  category: 'juridico',
  file_size_bytes: 204800,
  created_by: 'autor@test.com',
  created_at: '2024-01-15T10:00:00Z',
  is_public: false,
  confidentiality: 'interno',
  is_perpetual: false,
  requires_approval: true,
  requires_signature: false,
  valid_from: '',
  valid_until: '',
  signature_deadline: '',
  external_reference: '',
};

const mockDocumentNoDescription = {
  ...mockDocument,
  description: '',
};

describe('DocumentApprovalDialog', () => {
  const onClose = vi.fn();
  const onApproved = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockApprove.mockResolvedValue(undefined);
    mockReject.mockResolvedValue(undefined);
  });

  it('retorna null quando document é null', () => {
    const { container } = render(
      <DocumentApprovalDialog
        document={null}
        open={true}
        onClose={onClose}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('não renderiza dialog quando open=false e document existe', () => {
    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={false}
        onClose={onClose}
      />
    );
    expect(screen.queryByText('Aprovação de Documento')).not.toBeInTheDocument();
  });

  it('renderiza o dialog com informações do documento', async () => {
    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Aprovação de Documento')).toBeInTheDocument();
      expect(screen.getByText('Contrato de Prestação de Serviços')).toBeInTheDocument();
    });
  });

  it('exibe descrição quando presente', async () => {
    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Contrato referente a serviços de segurança')).toBeInTheDocument();
    });
  });

  it('não exibe seção de descrição quando vazia', async () => {
    render(
      <DocumentApprovalDialog
        document={mockDocumentNoDescription as any}
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.queryByText('Contrato referente a serviços de segurança')).not.toBeInTheDocument();
    });
  });

  it('exibe tipo, categoria e tamanho do documento', async () => {
    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('contrato')).toBeInTheDocument();
      expect(screen.getByText('juridico')).toBeInTheDocument();
    });
  });

  it('exibe criado por e data', async () => {
    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('autor@test.com')).toBeInTheDocument();
    });
  });

  it('aprova documento ao clicar em Aprovar', async () => {
    const { toast } = await import('sonner');

    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
        onApproved={onApproved}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Aprovar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Aprovar'));

    await waitFor(() => {
      expect(mockApprove).toHaveBeenCalledWith('doc-123');
      expect(toast.success).toHaveBeenCalledWith('Documento aprovado');
      expect(onApproved).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });

  it('exibe erro ao falhar aprovação', async () => {
    const { toast } = await import('sonner');
    mockApprove.mockRejectedValueOnce({
      response: { data: { detail: 'Sem permissão' } },
    });

    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Aprovar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Aprovar'));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Erro ao aprovar documento', expect.anything());
    });
  });

  it('rejeita documento com motivo preenchido', async () => {
    const { toast } = await import('sonner');

    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
        onApproved={onApproved}
      />
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Descreva o motivo/)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText(/Descreva o motivo/), {
      target: { value: 'Documentação incompleta' },
    });

    fireEvent.click(screen.getByText('Rejeitar'));

    await waitFor(() => {
      expect(mockReject).toHaveBeenCalledWith('doc-123', { reason: 'Documentação incompleta' });
      expect(toast.success).toHaveBeenCalledWith('Documento rejeitado');
      expect(onApproved).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });

  it('valida motivo obrigatório ao rejeitar', async () => {
    const { toast } = await import('sonner');

    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Rejeitar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Rejeitar'));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Motivo da rejeição é obrigatório');
      expect(mockReject).not.toHaveBeenCalled();
    });
  });

  it('exibe erro ao falhar rejeição', async () => {
    const { toast } = await import('sonner');
    mockReject.mockRejectedValueOnce({
      response: { data: { detail: 'Erro interno' } },
    });

    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Descreva o motivo/)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText(/Descreva o motivo/), {
      target: { value: 'Motivo qualquer' },
    });

    fireEvent.click(screen.getByText('Rejeitar'));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Erro ao rejeitar documento', expect.anything());
    });
  });

  it('chama onClose ao clicar em Cancelar', async () => {
    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Cancelar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Cancelar'));
    expect(onClose).toHaveBeenCalled();
  });

  it('desabilita botões durante loading', async () => {
    let resolveApprove: (value: any) => void;
    mockApprove.mockReturnValueOnce(
      new Promise((resolve) => { resolveApprove = resolve; })
    );

    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Aprovar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Aprovar'));

    // During loading, Rejeitar and Aprovar should be disabled
    await waitFor(() => {
      expect(screen.getByText('Rejeitar').closest('button')).toBeDisabled();
    });

    resolveApprove!(undefined);
  });

  it('exibe aviso de atenção', async () => {
    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Atenção')).toBeInTheDocument();
    });
  });

  it('não chama onApproved quando não passado', async () => {
    render(
      <DocumentApprovalDialog
        document={mockDocument as any}
        open={true}
        onClose={onClose}
        // onApproved not provided
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Aprovar')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Aprovar'));

    await waitFor(() => {
      expect(mockApprove).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });
});
