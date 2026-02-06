import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  exportToExcel,
  exportToCSV,
  formatDataForExport,
} from '../export';

// Mock do XLSX
const mockJsonToSheet = vi.fn(() => ({}));
const mockBookNew = vi.fn(() => ({}));
const mockBookAppendSheet = vi.fn();
const mockWriteFile = vi.fn();
const mockSheetToCsv = vi.fn(() => 'csv,content');

vi.mock('xlsx', () => ({
  utils: {
    json_to_sheet: (...args: any[]) => (mockJsonToSheet as any)(...args),
    book_new: () => mockBookNew(),
    book_append_sheet: (...args: any[]) => mockBookAppendSheet(...args),
    sheet_to_csv: (...args: any[]) => (mockSheetToCsv as any)(...args),
  },
  writeFile: (...args: any[]) => mockWriteFile(...args),
}));

describe('exportToExcel', () => {
  const mockData = [
    { nome: 'João', idade: 30 },
    { nome: 'Maria', idade: 25 },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('deve lançar erro quando dados estão vazios', () => {
    expect(() => exportToExcel([], 'teste')).toThrow('Nenhum dado disponível para exportação');
  });

  it('deve lançar erro quando dados são null', () => {
    expect(() => exportToExcel(null as any, 'teste')).toThrow('Nenhum dado disponível para exportação');
  });

  it('deve exportar dados com sucesso', () => {
    exportToExcel(mockData, 'relatorio');

    expect(mockJsonToSheet).toHaveBeenCalledWith(mockData);
    expect(mockBookNew).toHaveBeenCalled();
    expect(mockBookAppendSheet).toHaveBeenCalled();
    expect(mockWriteFile).toHaveBeenCalled();
  });

  it('deve incluir timestamp no nome do arquivo', () => {
    exportToExcel(mockData, 'relatorio');

    const callArg = mockWriteFile.mock.calls[0]![1];
    expect(callArg).toMatch(/relatorio_\d{8}\.xlsx/);
  });
});

describe('exportToCSV', () => {
  const mockData = [
    { nome: 'João', idade: 30 },
    { nome: 'Maria', idade: 25 },
  ];

  let mockLink: { href: string; download: string; click: ReturnType<typeof vi.fn> };
  let blobContent: string[] = [];

  beforeEach(() => {
    vi.clearAllMocks();
    blobContent = [];

    // Mock do createElement e click
    mockLink = {
      href: '',
      download: '',
      click: vi.fn(),
    };
    document.createElement = vi.fn(() => mockLink as any);
    document.body.appendChild = vi.fn();
    document.body.removeChild = vi.fn();

    // Mock URL
    global.URL.createObjectURL = vi.fn(() => 'blob:url');
    global.URL.revokeObjectURL = vi.fn();

    // Mock Blob - usando function declaration em vez de arrow function
    global.Blob = function(content: BlobPart[], options?: BlobPropertyBag) {
      if (content && content.length > 0) {
        blobContent.push(String(content[0]));
      }
      return { size: content[0]?.toString().length || 0, type: options?.type || '' } as Blob;
    } as any;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('deve lançar erro quando dados estão vazios', () => {
    expect(() => exportToCSV([], 'teste')).toThrow('Nenhum dado disponível para exportação');
  });

  it('deve exportar dados para CSV com sucesso', () => {
    exportToCSV(mockData, 'relatorio');

    expect(mockJsonToSheet).toHaveBeenCalledWith(mockData);
    expect(mockSheetToCsv).toHaveBeenCalled();
  });

  it('deve criar link de download corretamente', () => {
    exportToCSV(mockData, 'relatorio');

    expect(document.createElement).toHaveBeenCalledWith('a');
    expect(mockLink.click).toHaveBeenCalled();
  });

  it('deve incluir timestamp no nome do arquivo', () => {
    exportToCSV(mockData, 'relatorio');

    expect(mockLink.download).toMatch(/relatorio_\d{8}\.csv/);
  });

  it('deve adicionar BOM UTF-8 ao conteúdo', () => {
    exportToCSV(mockData, 'relatorio');

    expect(blobContent.length).toBeGreaterThan(0);
    expect(blobContent[0]).toContain('\ufeff');
  });
});

describe('formatDataForExport', () => {
  const mockData = [
    { firstName: 'João', lastName: 'Silva', age: 30 },
    { firstName: 'Maria', lastName: 'Souza', age: 25 },
  ];

  it('deve mapear campos corretamente', () => {
    const fieldMapping = {
      firstName: 'Nome',
      lastName: 'Sobrenome',
      age: 'Idade',
    };

    const result = formatDataForExport(mockData, fieldMapping);

    expect(result).toEqual([
      { Nome: 'João', Sobrenome: 'Silva', Idade: 30 },
      { Nome: 'Maria', Sobrenome: 'Souza', Idade: 25 },
    ]);
  });

  it('deve usar traço para valores nulos ou undefined', () => {
    const dataWithNulls = [
      { name: 'João', email: null },
      { name: 'Maria', email: undefined },
    ];

    const fieldMapping = {
      name: 'Nome',
      email: 'Email',
    };

    const result = formatDataForExport(dataWithNulls, fieldMapping);

    expect(result).toEqual([
      { Nome: 'João', Email: '-' },
      { Nome: 'Maria', Email: '-' },
    ]);
  });

  it('deve lidar com array vazio', () => {
    const result = formatDataForExport([], { name: 'Nome' });
    expect(result).toEqual([]);
  });

  it('deve incluir apenas campos mapeados', () => {
    const fieldMapping = {
      firstName: 'Nome',
    };

    const result = formatDataForExport(mockData, fieldMapping);

    expect(result).toEqual([
      { Nome: 'João' },
      { Nome: 'Maria' },
    ]);
    expect(result[0]).not.toHaveProperty('lastName');
    expect(result[0]).not.toHaveProperty('age');
  });

  it('deve preservar valores zero e false', () => {
    const data = [
      { name: 'Item', quantity: 0, active: false },
    ];

    const fieldMapping = {
      name: 'Nome',
      quantity: 'Quantidade',
      active: 'Ativo',
    };

    const result = formatDataForExport(data, fieldMapping);

    expect(result).toEqual([
      { Nome: 'Item', Quantidade: 0, Ativo: false },
    ]);
  });
});
