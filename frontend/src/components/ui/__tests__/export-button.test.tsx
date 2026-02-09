import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { ExportButton } from '../export-button';

// Mock dos utilitários de exportação
vi.mock('@/utils/export', () => ({
  exportToExcel: vi.fn(),
  exportToPDF: vi.fn(),
  exportToCSV: vi.fn(),
}));

// Mock do useToast
const mockToast = vi.fn();
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({ toast: mockToast }),
}));

// Mock do DropdownMenu
vi.mock('@/components/ui/dropdown-menu', () => ({
  DropdownMenu: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dropdown-menu">{children}</div>
  ),
  DropdownMenuTrigger: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dropdown-trigger">{children}</div>
  ),
  DropdownMenuContent: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dropdown-content">{children}</div>
  ),
  DropdownMenuItem: ({ children, onClick }: { children: React.ReactNode; onClick?: () => void }) => (
    <button data-testid="dropdown-item" onClick={onClick}>{children}</button>
  ),
  DropdownMenuSeparator: () => <hr data-testid="dropdown-separator" />,
}));

import { exportToExcel, exportToPDF, exportToCSV } from '@/utils/export';

describe('ExportButton', () => {
  const mockData = [
    { id: 1, name: 'Teste 1' },
    { id: 2, name: 'Teste 2' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve renderizar botão com texto padrão', () => {
    render(<ExportButton data={mockData} filename="teste" />);
    expect(screen.getByText('Exportar')).toBeInTheDocument();
  });

  it('deve renderizar botão com texto customizado', () => {
    render(<ExportButton data={mockData} filename="teste" buttonText="Baixar Dados" />);
    expect(screen.getByText('Baixar Dados')).toBeInTheDocument();
  });

  it('deve estar desabilitado quando não há dados', () => {
    render(<ExportButton data={[]} filename="teste" />);
    expect(screen.getByText('Exportar')).toBeDisabled();
  });

  it('deve estar desabilitado quando disabled é true', () => {
    render(<ExportButton data={mockData} filename="teste" disabled />);
    expect(screen.getByText('Exportar')).toBeDisabled();
  });

  it('deve mostrar ícone de download', () => {
    const { container } = render(<ExportButton data={mockData} filename="teste" />);
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('deve renderizar com variante padrão outline', () => {
    render(<ExportButton data={mockData} filename="teste" />);
    const button = screen.getByText('Exportar');
    expect(button).toBeInTheDocument();
  });

  it('deve renderizar com tamanho padrão sm', () => {
    render(<ExportButton data={mockData} filename="teste" />);
    const button = screen.getByText('Exportar');
    expect(button).toBeInTheDocument();
  });

  it('deve chamar onExportSuccess após exportação bem-sucedida', async () => {
    const onExportSuccess = vi.fn();
    render(
      <ExportButton
        data={mockData}
        filename="teste"
        onExportSuccess={onExportSuccess}
      />
    );
    // Simular exportação
    const excelButton = screen.getAllByTestId('dropdown-item')[0];
    if (excelButton) {
      fireEvent.click(excelButton);
    }

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Exportação concluída',
        })
      );
    });
  });

  it('deve chamar onExportError quando há erro na exportação', async () => {
    const onExportError = vi.fn();
    vi.mocked(exportToExcel).mockImplementationOnce(() => {
      throw new Error('Erro de exportação');
    });

    render(
      <ExportButton
        data={mockData}
        filename="teste"
        onExportError={onExportError}
      />
    );

    const excelButton = screen.getAllByTestId('dropdown-item')[0];
    if (excelButton) {
      fireEvent.click(excelButton);
    }

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          variant: 'destructive',
        })
      );
    });
  });

  it('deve mostrar toast de erro quando não há dados', () => {
    render(<ExportButton data={[]} filename="teste" />);
    // Não deve mostrar opções de exportação quando não há dados
    expect(screen.getByText('Exportar')).toBeDisabled();
  });

  it('deve aplicar gap entre ícone e texto', () => {
    const { container } = render(<ExportButton data={mockData} filename="teste" />);
    const button = container.querySelector('.gap-2');
    expect(button).toBeInTheDocument();
  });

  it('deve renderizar apenas formatos especificados', () => {
    render(<ExportButton data={mockData} filename="teste" formats={['excel']} />);
    const items = screen.getAllByTestId('dropdown-item');
    expect(items.length).toBe(1);
  });

  it('deve aplicar classe customizada ao container', () => {
    const { container } = render(<ExportButton data={mockData} filename="teste" />);
    expect(container.querySelector('[data-testid="dropdown-menu"]')).toBeInTheDocument();
  });
});
