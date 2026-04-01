import { describe, it, expect } from 'vitest';
import { formatFileSize, getFileIcon } from '../file-helpers';

describe('formatFileSize', () => {
  it('deve formatar bytes', () => {
    expect(formatFileSize(500)).toBe('500 Bytes');
  });

  it('deve formatar zero bytes', () => {
    expect(formatFileSize(0)).toBe('0 Bytes');
  });

  it('deve formatar KB', () => {
    expect(formatFileSize(1024)).toBe('1 KB');
  });

  it('deve formatar MB', () => {
    expect(formatFileSize(1024 * 1024)).toBe('1 MB');
  });

  it('deve formatar GB', () => {
    expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB');
  });

  it('deve formatar valores decimais', () => {
    expect(formatFileSize(1536)).toBe('1.5 KB');
  });

  it('deve formatar valores grandes', () => {
    expect(formatFileSize(1024 * 1024 * 1024 * 2)).toBe('2 GB');
  });

  it('deve formatar valores fracionados corretamente', () => {
    const size = 1024 * 1.75; // 1.75 KB
    expect(formatFileSize(size)).toBe('1.75 KB');
  });
});

describe('getFileIcon', () => {
  describe('Documentos de texto', () => {
    it('deve retornar FileText para PDF', () => {
      expect(getFileIcon('documento.pdf')).toBe('FileText');
    });

    it('deve retornar FileText para DOC', () => {
      expect(getFileIcon('documento.doc')).toBe('FileText');
    });

    it('deve retornar FileText para DOCX', () => {
      expect(getFileIcon('documento.docx')).toBe('FileText');
    });

    it('deve retornar FileText para TXT', () => {
      expect(getFileIcon('documento.txt')).toBe('FileText');
    });
  });

  describe('Planilhas', () => {
    it('deve retornar FileSpreadsheet para XLS', () => {
      expect(getFileIcon('planilha.xls')).toBe('FileSpreadsheet');
    });

    it('deve retornar FileSpreadsheet para XLSX', () => {
      expect(getFileIcon('planilha.xlsx')).toBe('FileSpreadsheet');
    });

    it('deve retornar FileSpreadsheet para CSV', () => {
      expect(getFileIcon('dados.csv')).toBe('FileSpreadsheet');
    });
  });

  describe('Apresentações', () => {
    it('deve retornar Presentation para PPT', () => {
      expect(getFileIcon('apresentacao.ppt')).toBe('Presentation');
    });

    it('deve retornar Presentation para PPTX', () => {
      expect(getFileIcon('apresentacao.pptx')).toBe('Presentation');
    });
  });

  describe('Imagens', () => {
    it('deve retornar Image para JPG', () => {
      expect(getFileIcon('foto.jpg')).toBe('Image');
    });

    it('deve retornar Image para JPEG', () => {
      expect(getFileIcon('foto.jpeg')).toBe('Image');
    });

    it('deve retornar Image para PNG', () => {
      expect(getFileIcon('foto.png')).toBe('Image');
    });

    it('deve retornar Image para GIF', () => {
      expect(getFileIcon('animacao.gif')).toBe('Image');
    });

    it('deve retornar Image para SVG', () => {
      expect(getFileIcon('icone.svg')).toBe('Image');
    });
  });

  describe('Casos especiais', () => {
    it('deve retornar File para extensão desconhecida', () => {
      expect(getFileIcon('arquivo.xyz')).toBe('File');
    });

    it('deve retornar File para arquivo sem extensão', () => {
      expect(getFileIcon('arquivo')).toBe('File');
    });

    it('deve retornar File para arquivo vazio', () => {
      expect(getFileIcon('')).toBe('File');
    });

    it('deve ser case insensitive', () => {
      expect(getFileIcon('FOTO.JPG')).toBe('Image');
      expect(getFileIcon('Foto.Jpg')).toBe('Image');
      expect(getFileIcon('foto.jpg')).toBe('Image');
    });

    it('deve extrair extensão corretamente com múltiplos pontos', () => {
      expect(getFileIcon('arquivo.backup.tar.gz')).toBe('File');
      expect(getFileIcon('documento.v2.final.pdf')).toBe('FileText');
    });
  });
});
