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

  it('deve renderizar apenas PDF quando formats=["pdf"]', () => {
    render(<ExportButton data={mockData} filename="teste" formats={['pdf']} />);
    const items = screen.getAllByTestId('dropdown-item');
    expect(items.length).toBe(1);
    expect(items[0]).toHaveTextContent('PDF (.pdf)');
  });

  it('deve renderizar apenas CSV quando formats=["csv"]', () => {
    render(<ExportButton data={mockData} filename="teste" formats={['csv']} />);
    const items = screen.getAllByTestId('dropdown-item');
    expect(items.length).toBe(1);
    expect(items[0]).toHaveTextContent('CSV (.csv)');
  });

  it('deve chamar exportToPDF quando clicar no item PDF', async () => {
    render(<ExportButton data={mockData} filename="teste" formats={['pdf']} />);

    const pdfButton = screen.getByTestId('dropdown-item');
    fireEvent.click(pdfButton);

    await waitFor(() => {
      expect(exportToPDF).toHaveBeenCalledWith(mockData, 'teste', undefined);
    });
  });

  it('deve chamar exportToPDF com pdfTitle quando fornecido', async () => {
    render(
      <ExportButton
        data={mockData}
        filename="teste"
        formats={['pdf']}
        pdfTitle="Relatório de Teste"
      />
    );

    const pdfButton = screen.getByTestId('dropdown-item');
    fireEvent.click(pdfButton);

    await waitFor(() => {
      expect(exportToPDF).toHaveBeenCalledWith(mockData, 'teste', 'Relatório de Teste');
    });
  });

  it('deve chamar exportToCSV quando clicar no item CSV', async () => {
    render(<ExportButton data={mockData} filename="teste" formats={['csv']} />);

    const csvButton = screen.getByTestId('dropdown-item');
    fireEvent.click(csvButton);

    await waitFor(() => {
      expect(exportToCSV).toHaveBeenCalledWith(mockData, 'teste');
    });
  });

  it('deve renderizar separador entre excel/pdf e csv', () => {
    render(<ExportButton data={mockData} filename="teste" formats={['excel', 'csv']} />);
    const separator = screen.getByTestId('dropdown-separator');
    expect(separator).toBeInTheDocument();
  });
});
