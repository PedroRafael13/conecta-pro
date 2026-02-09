import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
} from '../table';

describe('Table', () => {
  it('deve renderizar tabela básica', () => {
    const { container } = render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>Dado</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(container.querySelector('table')).toBeInTheDocument();
  });

  it('deve renderizar com wrapper de overflow', () => {
    const { container } = render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>Dado</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(container.querySelector('.overflow-auto')).toBeInTheDocument();
  });

  it('deve renderizar TableHeader', () => {
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nome</TableHead>
            <TableHead>Email</TableHead>
          </TableRow>
        </TableHeader>
      </Table>
    );
    expect(screen.getByText('Nome')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
  });

  it('deve renderizar TableBody com múltiplas linhas', () => {
    render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>Linha 1</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Linha 2</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(screen.getByText('Linha 1')).toBeInTheDocument();
    expect(screen.getByText('Linha 2')).toBeInTheDocument();
  });

  it('deve renderizar TableFooter', () => {
    render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>Dado</TableCell>
          </TableRow>
        </TableBody>
        <TableFooter>
          <TableRow>
            <TableCell>Total</TableCell>
          </TableRow>
        </TableFooter>
      </Table>
    );
    expect(screen.getByText('Total')).toBeInTheDocument();
  });

  it('deve aplicar classe de estilo no TableFooter', () => {
    const { container } = render(
      <Table>
        <TableFooter>
          <TableRow>
            <TableCell>Footer</TableCell>
          </TableRow>
        </TableFooter>
      </Table>
    );
    const footer = container.querySelector('tfoot');
    expect(footer?.className).toContain('bg-muted');
  });

  it('deve renderizar TableHead com fonte média', () => {
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Cabeçalho</TableHead>
          </TableRow>
        </TableHeader>
      </Table>
    );
    const header = screen.getByText('Cabeçalho');
    expect(header.className).toContain('font-medium');
    expect(header.className).toContain('text-muted-foreground');
  });

  it('deve renderizar TableCell com alinhamento correto', () => {
    render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>Célula</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    const cell = screen.getByText('Célula');
    expect(cell.className).toContain('align-middle');
  });

  it('deve renderizar TableCaption', () => {
    render(
      <Table>
        <TableCaption>Legenda da tabela</TableCaption>
        <TableBody>
          <TableRow>
            <TableCell>Dado</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(screen.getByText('Legenda da tabela')).toBeInTheDocument();
  });

  it('deve aplicar classe de estilo no TableCaption', () => {
    render(
      <Table>
        <TableCaption>Legenda</TableCaption>
      </Table>
    );
    const caption = screen.getByText('Legenda');
    expect(caption.className).toContain('text-muted-foreground');
  });

  it('deve aplicar classe customizada no Table', () => {
    const { container } = render(
      <Table className="custom-table">
        <TableBody>
          <TableRow>
            <TableCell>Dado</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    const table = container.querySelector('table');
    expect(table?.className).toContain('custom-table');
  });

  it('deve aplicar classe customizada no TableRow', () => {
    const { container } = render(
      <Table>
        <TableBody>
          <TableRow className="custom-row">
            <TableCell>Dado</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    const row = container.querySelector('tr');
    expect(row?.className).toContain('custom-row');
  });

  it('deve aplicar classe customizada no TableCell', () => {
    render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell className="custom-cell">Dado</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    const cell = screen.getByText('Dado');
    expect(cell.className).toContain('custom-cell');
  });

  it('deve ter displayName correto para Table', () => {
    expect(Table.displayName).toBe('Table');
  });

  it('deve ter displayName correto para TableHeader', () => {
    expect(TableHeader.displayName).toBe('TableHeader');
  });

  it('deve ter displayName correto para TableBody', () => {
    expect(TableBody.displayName).toBe('TableBody');
  });

  it('deve ter displayName correto para TableFooter', () => {
    expect(TableFooter.displayName).toBe('TableFooter');
  });

  it('deve ter displayName correto para TableRow', () => {
    expect(TableRow.displayName).toBe('TableRow');
  });

  it('deve ter displayName correto para TableHead', () => {
    expect(TableHead.displayName).toBe('TableHead');
  });

  it('deve ter displayName correto para TableCell', () => {
    expect(TableCell.displayName).toBe('TableCell');
  });

  it('deve ter displayName correto para TableCaption', () => {
    expect(TableCaption.displayName).toBe('TableCaption');
  });

  it('deve renderizar tabela completa com todos os elementos', () => {
    render(
      <Table>
        <TableCaption>Lista de usuários</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead>Email</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>1</TableCell>
            <TableCell>João</TableCell>
            <TableCell>joao@email.com</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>2</TableCell>
            <TableCell>Maria</TableCell>
            <TableCell>maria@email.com</TableCell>
          </TableRow>
        </TableBody>
        <TableFooter>
          <TableRow>
            <TableCell colSpan={3}>Total: 2 usuários</TableCell>
          </TableRow>
        </TableFooter>
      </Table>
    );
    expect(screen.getByText('Lista de usuários')).toBeInTheDocument();
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('João')).toBeInTheDocument();
    expect(screen.getByText('maria@email.com')).toBeInTheDocument();
    expect(screen.getByText('Total: 2 usuários')).toBeInTheDocument();
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLTableElement | null };
    render(
      <Table ref={ref}>
        <TableBody>
          <TableRow>
            <TableCell>Dado</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(ref.current).toBeInstanceOf(HTMLTableElement);
  });
});
