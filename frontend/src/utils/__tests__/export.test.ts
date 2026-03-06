import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as XLSX from 'xlsx';
import {
  exportToExcel,
  exportToCSV,
  formatDataForExport,
} from '../export';

// Mock do XLSX
vi.mock('xlsx', () => ({
  utils: {
    json_to_sheet: vi.fn(() => ({
      '!cols': undefined,
    })),
    book_new: vi.fn(() => ({})),
    book_append_sheet: vi.fn(),
    sheet_to_csv: vi.fn(() => 'csv,data'),
  },
  writeFile: vi.fn(),
}));

describe('exportToExcel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('deve lançar erro quando data é vazio', () => {
    expect(() => exportToExcel([], 'test')).toThrow('Nenhum dado disponível para exportação');
  });

  it('deve lançar erro quando data é null', () => {
    expect(() => exportToExcel(null as any, 'test')).toThrow('Nenhum dado disponível para exportação');
  });

  it('deve exportar com sucesso', () => {
    const data = [{ name: 'John', age: 30 }];
    exportToExcel(data, 'test');
    expect(XLSX.writeFile).toHaveBeenCalled();
  });

  it('deve calcular largura das colunas corretamente', () => {
    const data = [
      { name: 'John Doe With Long Name', age: 30 },
      { name: 'Jane', age: 25 },
    ];
    exportToExcel(data, 'test');
    expect(XLSX.utils.json_to_sheet).toHaveBeenCalled();
  });

  it('deve lidar com valores null/undefined ao calcular largura das colunas', () => {
    const data = [
      { name: null, description: undefined, status: 'active' },
      { name: 'Jane', description: 'test', status: null },
    ];
    exportToExcel(data, 'test');
    expect(XLSX.utils.json_to_sheet).toHaveBeenCalled();
    expect(XLSX.writeFile).toHaveBeenCalled();
  });

  it('deve re-lançar erro quando XLSX.writeFile falha', () => {
    vi.mocked(XLSX.writeFile).mockImplementationOnce(() => { throw new Error('Write failed'); });

    const data = [{ name: 'John' }];
    expect(() => exportToExcel(data, 'test')).toThrow('Write failed');
    expect(console.error).toHaveBeenCalled();
  });
});

describe('exportToCSV', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, 'error').mockImplementation(() => {});

    // Mock do DOM
    global.URL.createObjectURL = vi.fn(() => 'blob:url');
    global.URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('deve lançar erro quando data é vazio', () => {
    expect(() => exportToCSV([], 'test')).toThrow('Nenhum dado disponível para exportação');
  });

  it('deve lançar erro quando data é null', () => {
    expect(() => exportToCSV(null as any, 'test')).toThrow('Nenhum dado disponível para exportação');
  });

  it('deve exportar CSV com sucesso', () => {
    const data = [{ name: 'John', age: 30 }];

    // Mock document.createElement
    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);

    exportToCSV(data, 'test');

    expect(XLSX.utils.sheet_to_csv).toHaveBeenCalled();
    expect(mockLink.click).toHaveBeenCalled();
    // Verificar que o download file tem timestamp
    expect(mockLink.download).toMatch(/^test_\d{8}\.csv$/);
  });

  it('deve chamar revokeObjectURL após timeout', () => {
    vi.useFakeTimers();
    const data = [{ name: 'John', age: 30 }];

    const mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);

    exportToCSV(data, 'test');

    vi.advanceTimersByTime(200);
    expect(global.URL.revokeObjectURL).toHaveBeenCalled();
    vi.useRealTimers();
  });

  it('deve re-lançar erro quando exportação CSV falha internamente', () => {
    vi.mocked(XLSX.utils.json_to_sheet).mockImplementationOnce(() => { throw new Error('Sheet failed'); });

    const data = [{ name: 'John' }];
    expect(() => exportToCSV(data, 'test')).toThrow('Sheet failed');
    expect(console.error).toHaveBeenCalled();
  });
});

describe('exportToPDF', () => {
  const mockSave = vi.fn();
  const mockText = vi.fn();
  const mockSetFontSize = vi.fn();
  const mockSetTextColor = vi.fn();
  const mockAutoTable = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, 'error').mockImplementation(() => {});

    // Mock jsPDF e autoTable via dynamic import
    vi.doMock('jspdf', () => ({
      default: class MockJsPDF {
        internal = {
          pageSize: { width: 297, height: 210 },
          getNumberOfPages: () => 1,
        };
        save = mockSave;
        text = mockText;
        setFontSize = mockSetFontSize;
        setTextColor = mockSetTextColor;
      },
    }));
    vi.doMock('jspdf-autotable', () => ({
      default: (doc: any, options: any) => {
        mockAutoTable(doc, options);
        // Execute didDrawPage callback to cover the footer branch
        if (options.didDrawPage) {
          options.didDrawPage({ pageNumber: 1 });
        }
      },
    }));
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.doUnmock('jspdf');
    vi.doUnmock('jspdf-autotable');
  });

  it('deve lançar erro quando data é vazio', async () => {
    const { exportToPDF } = await import('../export');
    await expect(exportToPDF([], 'test')).rejects.toThrow('Nenhum dado disponível para exportação');
  });

  it('deve lançar erro quando data é null', async () => {
    const { exportToPDF } = await import('../export');
    await expect(exportToPDF(null as any, 'test')).rejects.toThrow('Nenhum dado disponível para exportação');
  });

  it('deve exportar PDF com título padrão (filename) quando title não é fornecido', async () => {
    const { exportToPDF } = await import('../export');

    const data = [{ name: 'John', age: 30 }];
    await exportToPDF(data, 'test_report');

    expect(mockText).toHaveBeenCalledWith('test_report', 14, 15);
    expect(mockSave).toHaveBeenCalledWith(expect.stringMatching(/^test_report_\d{8}\.pdf$/));
  });

  it('deve exportar PDF com título customizado', async () => {
    const { exportToPDF } = await import('../export');

    const data = [{ name: 'John', age: 30 }];
    await exportToPDF(data, 'test', 'Custom Title');

    expect(mockText).toHaveBeenCalledWith('Custom Title', 14, 15);
  });

  it('deve formatar valores null/undefined como "-" em PDF', async () => {
    const { exportToPDF } = await import('../export');

    const data = [
      { name: null, description: undefined, count: 5 },
    ];
    await exportToPDF(data, 'test');

    expect(mockAutoTable).toHaveBeenCalled();
    const callArgs = mockAutoTable.mock.calls[0][1];
    // O primeiro row deve ter '-' para null e undefined
    expect(callArgs.body[0]).toContain('-');
  });

  it('deve truncar strings muito longas em PDF', async () => {
    const { exportToPDF } = await import('../export');

    const longString = 'A'.repeat(100);
    const data = [{ description: longString }];
    await exportToPDF(data, 'test');

    const callArgs = mockAutoTable.mock.calls[0][1];
    expect(callArgs.body[0][0]).toBe('A'.repeat(47) + '...');
  });

  it('deve converter valores numéricos para string em PDF', async () => {
    const { exportToPDF } = await import('../export');

    const data = [{ count: 42, active: true }];
    await exportToPDF(data, 'test');

    const callArgs = mockAutoTable.mock.calls[0][1];
    expect(callArgs.body[0]).toContain('42');
    expect(callArgs.body[0]).toContain('true');
  });
});

describe('formatDataForExport', () => {
  it('deve formatar dados com mapeamento de campos', () => {
    const data = [
      { id: 1, name: 'John', email: 'john@test.com' },
      { id: 2, name: 'Jane', email: 'jane@test.com' },
    ];
    const mapping = {
      id: 'ID',
      name: 'Nome',
      email: 'Email',
    };

    const result = formatDataForExport(data, mapping);

    expect(result).toEqual([
      { ID: 1, Nome: 'John', Email: 'john@test.com' },
      { ID: 2, Nome: 'Jane', Email: 'jane@test.com' },
    ]);
  });

  it('deve usar - quando valor é null ou undefined', () => {
    const data = [
      { id: 1, name: null, email: undefined },
      { id: 2, name: 'Jane', email: 'jane@test.com' },
    ];
    const mapping = {
      id: 'ID',
      name: 'Nome',
      email: 'Email',
    };

    const result = formatDataForExport(data, mapping);

    expect(result[0].Nome).toBe('-');
    expect(result[0].Email).toBe('-');
    expect(result[1].Nome).toBe('Jane');
  });

  it('deve retornar array vazio quando data é vazio', () => {
    const result = formatDataForExport([], { id: 'ID' });
    expect(result).toEqual([]);
  });
});
