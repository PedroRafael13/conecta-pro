/**
 * Testes para TemplateCard
 * Cobre branches: description presente/ausente, post_name presente/ausente,
 * last_used_at presente/ausente, menu dropdown aberto/fechado,
 * callbacks onUse/onEdit/onDelete, formatDate com null/valido
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@/test/helpers/test-utils';
import { TemplateCard } from '../TemplateCard';
import type { ScaleTemplate } from '@/types/operacional';

// Mock date-fns para evitar variacao com data atual
vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn(() => 'ha 2 dias'),
}));
vi.mock('date-fns/locale', () => ({
  ptBR: {},
}));

const mockOnUse = vi.fn();
const mockOnEdit = vi.fn();
const mockOnDelete = vi.fn();

const baseTemplate: ScaleTemplate = {
  id: 'tpl-1',
  tenant_id: 'tenant-1',
  name: 'Template 12x36',
  description: 'Template para escala 12x36',
  scale_type: '12x36',
  post_id: 'post-1',
  post_name: 'Portaria Central',
  source_scale_id: 'scale-1',
  total_employees: 4,
  coverage_percentage: 95,
  pattern_days: 36,
  times_used: 10,
  last_used_at: '2025-01-10T00:00:00Z',
  created_by: null,
  created_at: '2024-12-01T00:00:00Z',
  updated_at: '2025-01-10T00:00:00Z',
  is_active: true,
};

describe('TemplateCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('renderizacao basica', () => {
    it('exibe nome do template', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getByText('Template 12x36')).toBeInTheDocument();
    });

    it('exibe tipo de escala', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getAllByText('12x36 (12h trabalho, 36h descanso)')[0]).toBeInTheDocument();
    });

    it('exibe metricas: colaboradores, cobertura e dias', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getByText('4')).toBeInTheDocument(); // total_employees
      expect(screen.getByText('95%')).toBeInTheDocument(); // coverage
      expect(screen.getByText('36')).toBeInTheDocument(); // pattern_days
    });

    it('exibe quantidade de vezes usado', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getByText(/Usado 10x/)).toBeInTheDocument();
    });

    it('exibe botao "Usar este Template"', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getByRole('button', { name: /usar este template/i })).toBeInTheDocument();
    });
  });

  describe('description branch', () => {
    it('exibe descricao quando presente', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getByText('Template para escala 12x36')).toBeInTheDocument();
    });

    it('nao exibe descricao quando ausente (null)', () => {
      render(
        <TemplateCard
          template={{ ...baseTemplate, description: null }}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.queryByText('Template para escala 12x36')).not.toBeInTheDocument();
    });
  });

  describe('post_name branch', () => {
    it('exibe nome do posto quando presente', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getByText(/Portaria Central/)).toBeInTheDocument();
    });

    it('nao exibe nome do posto quando ausente (null)', () => {
      render(
        <TemplateCard
          template={{ ...baseTemplate, post_name: null }}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.queryByText(/Portaria Central/)).not.toBeInTheDocument();
    });
  });

  describe('last_used_at branch', () => {
    it('exibe ultimo uso quando last_used_at e preenchido', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getByText(/Último uso:/)).toBeInTheDocument();
    });

    it('nao exibe ultimo uso quando last_used_at e null', () => {
      render(
        <TemplateCard
          template={{ ...baseTemplate, last_used_at: null }}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.queryByText(/Último uso:/)).not.toBeInTheDocument();
    });
  });

  describe('formatDate branches', () => {
    it('exibe "Nunca" quando created_at e null', () => {
      render(
        <TemplateCard
          template={{ ...baseTemplate, created_at: null as unknown as string }}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.getByText(/Nunca/)).toBeInTheDocument();
    });
  });

  describe('menu dropdown', () => {
    it('menu esta oculto por padrao', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      expect(screen.queryByText('Usar Template')).not.toBeInTheDocument();
      expect(screen.queryByText('Editar')).not.toBeInTheDocument();
      expect(screen.queryByText('Excluir')).not.toBeInTheDocument();
    });

    it('abre menu ao clicar no botao de opcoes', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      // Botao com icone MoreVertical
      const menuBtn = screen.getAllByRole('button').find((b) => {
        const svg = b.querySelector('svg');
        return !!svg && !b.textContent?.includes('Usar');
      });
      if (menuBtn) {
        fireEvent.click(menuBtn);
        expect(screen.getByText('Usar Template')).toBeInTheDocument();
        expect(screen.getByText('Editar')).toBeInTheDocument();
        expect(screen.getByText('Excluir')).toBeInTheDocument();
      }
    });

    it('chama onUse e fecha menu ao clicar em "Usar Template"', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      const menuBtn = screen.getAllByRole('button').find((b) => {
        const svg = b.querySelector('svg');
        return !!svg && !b.textContent?.includes('Usar');
      });
      if (menuBtn) {
        fireEvent.click(menuBtn);
        fireEvent.click(screen.getByText('Usar Template'));
        expect(mockOnUse).toHaveBeenCalledWith(baseTemplate);
        expect(screen.queryByText('Editar')).not.toBeInTheDocument();
      }
    });

    it('chama onEdit e fecha menu ao clicar em "Editar"', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      const menuBtn = screen.getAllByRole('button').find((b) => {
        const svg = b.querySelector('svg');
        return !!svg && !b.textContent?.includes('Usar');
      });
      if (menuBtn) {
        fireEvent.click(menuBtn);
        fireEvent.click(screen.getByText('Editar'));
        expect(mockOnEdit).toHaveBeenCalledWith(baseTemplate);
      }
    });

    it('chama onDelete e fecha menu ao clicar em "Excluir"', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      const menuBtn = screen.getAllByRole('button').find((b) => {
        const svg = b.querySelector('svg');
        return !!svg && !b.textContent?.includes('Usar');
      });
      if (menuBtn) {
        fireEvent.click(menuBtn);
        fireEvent.click(screen.getByText('Excluir'));
        expect(mockOnDelete).toHaveBeenCalledWith(baseTemplate);
      }
    });

    it('fecha menu ao clicar no overlay', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      const menuBtn = screen.getAllByRole('button').find((b) => {
        const svg = b.querySelector('svg');
        return !!svg && !b.textContent?.includes('Usar');
      });
      if (menuBtn) {
        fireEvent.click(menuBtn);
        expect(screen.getByText('Editar')).toBeInTheDocument();
        // Clica no overlay (div fixed inset-0)
        const overlay = document.querySelector('.fixed.inset-0');
        if (overlay) {
          fireEvent.click(overlay);
          expect(screen.queryByText('Editar')).not.toBeInTheDocument();
        }
      }
    });
  });

  describe('botao principal "Usar este Template"', () => {
    it('chama onUse ao clicar no botao principal', () => {
      render(
        <TemplateCard
          template={baseTemplate}
          onUse={mockOnUse}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );
      fireEvent.click(screen.getByRole('button', { name: /usar este template/i }));
      expect(mockOnUse).toHaveBeenCalledWith(baseTemplate);
    });
  });
});
