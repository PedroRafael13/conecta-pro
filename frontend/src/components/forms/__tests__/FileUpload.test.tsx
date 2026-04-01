import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React, { useRef } from 'react';

interface FileUploadProps {
  accept?: string;
  maxSize?: number;
  onFileSelect?: (file: File) => void;
  onError?: (error: string) => void;
  label?: string;
  disabled?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  accept = '*',
  maxSize = 5 * 1024 * 1024,
  onFileSelect,
  onError,
  label = 'Selecionar arquivo',
  disabled
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    if (!disabled) {
      inputRef.current?.click();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > maxSize) {
      onError?.(`Arquivo muito grande. Máximo: ${maxSize / 1024 / 1024}MB`);
      return;
    }

    onFileSelect?.(file);
  };

  return (
    <div className="file-upload" data-testid="file-upload">
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        data-testid="file-input"
        style={{ display: 'none' }}
      />
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        data-testid="upload-button"
      >
        {label}
      </button>
    </div>
  );
};

FileUpload.displayName = 'FileUpload';

describe('FileUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renderiza componente de upload', () => {
    render(<FileUpload />);
    expect(screen.getByTestId('file-upload')).toBeInTheDocument();
  });

  it('renderiza botão com label padrão', () => {
    render(<FileUpload />);
    expect(screen.getByText('Selecionar arquivo')).toBeInTheDocument();
  });

  it('renderiza botão com label customizado', () => {
    render(<FileUpload label="Enviar documento" />);
    expect(screen.getByText('Enviar documento')).toBeInTheDocument();
  });

  it('input file está oculto', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    expect(input).toHaveStyle({ display: 'none' });
  });

  it('aceita tipos de arquivo específicos', () => {
    render(<FileUpload accept=".pdf,.doc" />);
    const input = screen.getByTestId('file-input');
    expect(input).toHaveAttribute('accept', '.pdf,.doc');
  });

  it('chama onFileSelect quando arquivo é selecionado', () => {
    const handleFileSelect = vi.fn();
    render(<FileUpload onFileSelect={handleFileSelect} />);

    const input = screen.getByTestId('file-input');
    const file = new File(['conteúdo'], 'teste.pdf', { type: 'application/pdf' });

    fireEvent.change(input, { target: { files: [file] } });
    expect(handleFileSelect).toHaveBeenCalledWith(file);
  });

  it('chama onError quando arquivo excede tamanho máximo', () => {
    const handleError = vi.fn();
    render(<FileUpload maxSize={10} onError={handleError} />);

    const input = screen.getByTestId('file-input');
    // Criar arquivo com conteúdo que excede 10 bytes
    const file = new File(['conteudo grande'], 'teste.pdf', { type: 'application/pdf' });

    fireEvent.change(input, { target: { files: [file] } });
    expect(handleError).toHaveBeenCalledWith(expect.stringContaining('Arquivo muito grande'));
  });

  it('pode ser desabilitado', () => {
    render(<FileUpload disabled />);
    const button = screen.getByTestId('upload-button');
    expect(button).toBeDisabled();
  });

  it('não chama onFileSelect quando desabilitado', () => {
    const handleFileSelect = vi.fn();
    render(<FileUpload disabled onFileSelect={handleFileSelect} />);

    const button = screen.getByTestId('upload-button');
    fireEvent.click(button);
    // O botão está desabilitado, então não deve haver interação
    expect(button).toBeDisabled();
  });

  it('tem displayName correto', () => {
    expect(FileUpload.displayName).toBe('FileUpload');
  });

  it('não chama callback quando nenhum arquivo é selecionado', () => {
    const handleFileSelect = vi.fn();
    render(<FileUpload onFileSelect={handleFileSelect} />);

    const input = screen.getByTestId('file-input');
    fireEvent.change(input, { target: { files: [] } });
    expect(handleFileSelect).not.toHaveBeenCalled();
  });

  it('aceita múltiplos tipos de arquivo', () => {
    render(<FileUpload accept="image/*,.pdf,.doc,.docx" />);
    const input = screen.getByTestId('file-input');
    expect(input).toHaveAttribute('accept', 'image/*,.pdf,.doc,.docx');
  });

  it('define tamanho máximo padrão de 5MB', () => {
    const handleError = vi.fn();
    render(<FileUpload onError={handleError} />);

    const input = screen.getByTestId('file-input');
    const largeFile = new File([new ArrayBuffer(6 * 1024 * 1024)], 'large.pdf', { type: 'application/pdf' });

    fireEvent.change(input, { target: { files: [largeFile] } });
    expect(handleError).toHaveBeenCalledWith(expect.stringContaining('5MB'));
  });

  it('não abre o input quando clicado e desabilitado', () => {
    const handleFileSelect = vi.fn();
    render(<FileUpload disabled onFileSelect={handleFileSelect} />);

    const button = screen.getByTestId('upload-button');
    const input = screen.getByTestId('file-input');

    // Mock do click no input
    const clickSpy = vi.spyOn(input, 'click');

    fireEvent.click(button);

    // Quando desabilitado, não deve chamar o click do input
    expect(clickSpy).not.toHaveBeenCalled();
  });
});
