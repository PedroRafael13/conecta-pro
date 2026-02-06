/**
 * Utilitários de Exportação de Dados
 * Suporta Excel (XLSX), PDF e CSV
 */

import * as XLSX from 'xlsx';

// Type para jspdf-autotable (já que @types não está disponível)
declare module 'jspdf' {
  interface jsPDF {
    autoTable: (options: any) => jsPDF;
    lastAutoTable?: {
      finalY: number;
    };
  }
}

/**
 * Exporta dados para arquivo Excel (.xlsx)
 * @param data Array de objetos a serem exportados
 * @param filename Nome do arquivo (sem extensão)
 */
export const exportToExcel = (data: any[], filename: string): void => {
  try {
    if (!data || data.length === 0) {
      throw new Error('Nenhum dado disponível para exportação');
    }

    // Criar worksheet
    const ws = XLSX.utils.json_to_sheet(data);

    // Auto-ajustar largura das colunas
    const cols = Object.keys(data[0]).map((key) => ({
      wch: Math.max(
        key.length,
        ...data.map((row) => String(row[key] || '').length)
      ).toString().length + 2,
    }));
    ws['!cols'] = cols;

    // Criar workbook e adicionar sheet
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Dados');

    // Gerar arquivo
    const timestamp = (new Date().toISOString().split('T')[0] ?? '').replace(/-/g, '');
    XLSX.writeFile(wb, `${filename}_${timestamp}.xlsx`);
  } catch (error) {
    console.error('Erro ao exportar para Excel:', error);
    throw error;
  }
};

/**
 * Exporta dados para arquivo PDF (.pdf)
 * @param data Array de objetos a serem exportados
 * @param filename Nome do arquivo (sem extensão)
 * @param title Título do documento (opcional)
 */
export const exportToPDF = async (
  data: any[],
  filename: string,
  title?: string
): Promise<void> => {
  try {
    if (!data || data.length === 0) {
      throw new Error('Nenhum dado disponível para exportação');
    }

    // Lazy load jsPDF e autoTable
    const [{ default: jsPDF }, { default: autoTable }] = await Promise.all([
      import('jspdf'),
      import('jspdf-autotable')
    ]);

    // Criar documento PDF
    const doc = new jsPDF({
      orientation: 'landscape',
      unit: 'mm',
      format: 'a4',
    });

    // Configurar título
    const documentTitle = title || filename;
    doc.setFontSize(16);
    doc.text(documentTitle, 14, 15);

    // Adicionar data de geração
    doc.setFontSize(8);
    doc.setTextColor(100);
    const dateStr = new Date().toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
    doc.text(`Gerado em: ${dateStr}`, 14, 22);

    // Preparar dados da tabela
    const headers = Object.keys(data[0]);
    const rows = data.map((item) =>
      headers.map((header) => {
        const value = item[header];
        // Formatar valores nulos/undefined
        if (value === null || value === undefined) return '-';
        // Truncar strings muito longas
        if (typeof value === 'string' && value.length > 50) {
          return value.substring(0, 47) + '...';
        }
        return String(value);
      })
    );

    // Gerar tabela
    autoTable(doc, {
      head: [headers],
      body: rows,
      startY: 28,
      theme: 'grid',
      styles: {
        fontSize: 8,
        cellPadding: 2,
        overflow: 'linebreak',
        halign: 'left',
      },
      headStyles: {
        fillColor: [59, 130, 246], // Blue-500
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        halign: 'center',
      },
      alternateRowStyles: {
        fillColor: [245, 245, 245],
      },
      margin: { top: 28, right: 14, bottom: 20, left: 14 },
      didDrawPage: (data: any) => {
        // Footer com número da página
        const pageCount = (doc as any).internal.getNumberOfPages();
        doc.setFontSize(8);
        doc.setTextColor(100);
        doc.text(
          `Página ${data.pageNumber} de ${pageCount}`,
          doc.internal.pageSize.width / 2,
          doc.internal.pageSize.height - 10,
          { align: 'center' }
        );
      },
    });

    // Salvar arquivo
    const timestamp = (new Date().toISOString().split('T')[0] ?? '').replace(/-/g, '');
    doc.save(`${filename}_${timestamp}.pdf`);
  } catch (error) {
    console.error('Erro ao exportar para PDF:', error);
    throw error;
  }
};

/**
 * Exporta dados para arquivo CSV (.csv)
 * @param data Array de objetos a serem exportados
 * @param filename Nome do arquivo (sem extensão)
 */
export const exportToCSV = (data: any[], filename: string): void => {
  try {
    if (!data || data.length === 0) {
      throw new Error('Nenhum dado disponível para exportação');
    }

    // Converter para sheet e depois para CSV
    const ws = XLSX.utils.json_to_sheet(data);
    const csv = XLSX.utils.sheet_to_csv(ws);

    // Criar blob com BOM UTF-8 para garantir acentuação correta no Excel
    const blob = new Blob(['\ufeff' + csv], {
      type: 'text/csv;charset=utf-8;',
    });

    // Criar link temporário e fazer download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    const timestamp = (new Date().toISOString().split('T')[0] ?? '').replace(/-/g, '');
    link.download = `${filename}_${timestamp}.csv`;
    link.click();

    // Cleanup
    setTimeout(() => URL.revokeObjectURL(link.href), 100);
  } catch (error) {
    console.error('Erro ao exportar para CSV:', error);
    throw error;
  }
};

/**
 * Formata dados para exportação, removendo campos desnecessários
 * e renomeando para português
 * @param data Array de dados brutos
 * @param fieldMapping Mapeamento de campos {key: label}
 * @returns Array formatado para exportação
 */
export const formatDataForExport = (
  data: any[],
  fieldMapping: Record<string, string>
): any[] => {
  return data.map((item) => {
    const formatted: any = {};
    Object.entries(fieldMapping).forEach(([key, label]) => {
      formatted[label] = item[key] ?? '-';
    });
    return formatted;
  });
};
