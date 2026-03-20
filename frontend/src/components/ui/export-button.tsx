'use client';

import { Download, FileSpreadsheet, FileText, Table } from 'lucide-react';
import { useState } from 'react';
;
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { exportToExcel, exportToPDF, exportToCSV } from '@/utils/export';
import { useToast } from '@/components/ui/use-toast';

export type ExportFormat = 'excel' | 'pdf' | 'csv';

export interface ExportButtonProps {
  /**
   * Dados a serem exportados
   */
  data: any[];

  /**
   * Nome base do arquivo (sem extensão)
   */
  filename: string;

  /**
   * Formatos disponíveis para exportação
   * @default ['excel', 'pdf', 'csv']
   */
  formats?: ExportFormat[];

  /**
   * Título do documento PDF (opcional)
   */
  pdfTitle?: string;

  /**
   * Tamanho do botão
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Variante do botão
   */
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';

  /**
   * Texto do botão
   */
  buttonText?: string;

  /**
   * Desabilitar botão
   */
  disabled?: boolean;

  /**
   * Callback após exportação bem-sucedida
   */
  onExportSuccess?: (format: ExportFormat) => void;

  /**
   * Callback após erro na exportação
   */
  onExportError?: (error: Error, format: ExportFormat) => void;
}

/**
 * Componente de Botão de Exportação
 *
 * Oferece opções para exportar dados em múltiplos formatos:
 * - Excel (.xlsx)
 * - PDF (.pdf)
 * - CSV (.csv)
 *
 * @example
 * ```tsx
 * <ExportButton
 *   data={colaboradores}
 *   filename="colaboradores"
 *   formats={['excel', 'pdf']}
 * />
 * ```
 */
export function ExportButton({
  data,
  filename,
  formats = ['excel', 'pdf', 'csv'],
  pdfTitle,
  size = 'sm',
  variant = 'outline',
  buttonText = 'Exportar',
  disabled = false,
  onExportSuccess,
  onExportError,
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportingFormat, setExportingFormat] = useState<ExportFormat | null>(null);
  const { toast } = useToast();

  const handleExport = async (format: ExportFormat) => {
    if (!data || data.length === 0) {
      toast({
        title: 'Nenhum dado disponível',
        description: 'Não há dados para exportar.',
        variant: 'destructive',
      });
      return;
    }

    setIsExporting(true);
    setExportingFormat(format);

    try {
      // Pequeno delay para dar feedback visual
      await new Promise((resolve) => setTimeout(resolve, 300));

      switch (format) {
        case 'excel':
          await exportToExcel(data, filename);
          break;
        case 'pdf':
          await exportToPDF(data, filename, pdfTitle);
          break;
        case 'csv':
          await exportToCSV(data, filename);
          break;
      }

      toast({
        title: 'Exportação concluída',
        description: `Arquivo ${format.toUpperCase()} baixado com sucesso.`,
      });

      onExportSuccess?.(format);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';

      toast({
        title: 'Erro na exportação',
        description: `Falha ao exportar para ${format.toUpperCase()}: ${errorMessage}`,
        variant: 'destructive',
      });

      onExportError?.(error instanceof Error ? error : new Error(errorMessage), format);
    } finally {
      setIsExporting(false);
      setExportingFormat(null);
    }
  };

  const formatConfig = {
    excel: {
      icon: FileSpreadsheet,
      label: 'Excel (.xlsx)',
      color: 'text-green-600',
    },
    pdf: {
      icon: FileText,
      label: 'PDF (.pdf)',
      color: 'text-red-600',
    },
    csv: {
      icon: Table,
      label: 'CSV (.csv)',
      color: 'text-blue-600',
    },
  };

  const isDisabled = disabled || !data || data.length === 0 || isExporting;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          disabled={isDisabled}
          className="gap-2"
        >
          {isExporting ? (
            <>
              <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
              Exportando...
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              {buttonText}
            </>
          )}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-48">
        {formats.includes('excel') && (
          <DropdownMenuItem
            onClick={() => handleExport('excel')}
            disabled={isExporting}
            className="cursor-pointer"
          >
            <FileSpreadsheet className={`w-4 h-4 mr-2 ${formatConfig.excel.color}`} />
            <span>
              {exportingFormat === 'excel' ? 'Exportando...' : formatConfig.excel.label}
            </span>
          </DropdownMenuItem>
        )}

        {formats.includes('pdf') && (
          <DropdownMenuItem
            onClick={() => handleExport('pdf')}
            disabled={isExporting}
            className="cursor-pointer"
          >
            <FileText className={`w-4 h-4 mr-2 ${formatConfig.pdf.color}`} />
            <span>
              {exportingFormat === 'pdf' ? 'Exportando...' : formatConfig.pdf.label}
            </span>
          </DropdownMenuItem>
        )}

        {formats.includes('csv') && (
          <>
            {(formats.includes('excel') || formats.includes('pdf')) && (
              <DropdownMenuSeparator />
            )}
            <DropdownMenuItem
              onClick={() => handleExport('csv')}
              disabled={isExporting}
              className="cursor-pointer"
            >
              <Table className={`w-4 h-4 mr-2 ${formatConfig.csv.color}`} />
              <span>
                {exportingFormat === 'csv' ? 'Exportando...' : formatConfig.csv.label}
              </span>
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
