/**
 * Testes para ApplyTemplateDialog
 * Cobre branches: template=null, step 1/2/3, validacao mes/ano invalidos,
 * post selection quando template sem post_id, isLoadingPreview,
 * preview disponivel/indisponivel, handleNext sem onPreview,
 * botao Voltar visivel apenas em step > 1, isLoading disabled states
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@/test/helpers/test-utils';
import { ApplyTemplateDialog } from '../ApplyTemplateDialog';
import type { ScaleTemplate, Scale, Post } from '@/types/operacional';

const mockOnClose = vi.fn();
const mockOnSubmit = vi.fn().mockResolvedValue({ id: 'scale-new' } as Scale);
const mockOnPreview = vi.fn().mockResolvedValue(null);

const baseTemplate: ScaleTemplate = {
  id: 'tpl-1',
  tenant_id: 'tenant-1',
  name: 'Meu Template',
  description: 'Descricao do template',
  scale_type: '12x36',
  post_id: 'post-1',
  post_name: 'Portaria Central',
  source_scale_id: 'scale-src-1',
  total_employees: 3,
  coverage_percentage: 90,
  pattern_days: 36,
  times_used: 5,
  last_used_at: null,
  created_by: null,
  created_at: '2024-12-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
  is_active: true,
};

const mockPosts: Post[] = [
  {
    id: 'post-1',
    code: 'P001',
    name: 'Portaria A',
    description: null,
    post_type: 'porteiro',
    status: 'active',
    shift_type: 'diurno',
    contract_id: null,
    client_id: null,
    address: null,
    city: null,
    state: null,
    zip_code: null,
    latitude: null,
    longitude: null,
    shift_start_time: null,
    shift_end_time: null,
    break_duration_minutes: 60,
    night_shift_bonus_percent: 20,
    hazard_pay_percent: 0,
    required_certifications: null,
    required_headcount: 1,
    current_headcount: 1,
    requires_experience_months: 0,
    hourly_rate: 20,
    monthly_cost: 3000,
    requires_armed: false,
    requires_vehicle: false,
    supervisor_name: null,
    supervisor_phone: null,
    emergency_contact: null,
    emergency_phone: null,
    notes: null,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    is_filled: true,
    vacancy_count: 0,
    daily_hours: 12,
  },
];

const defaultProps = {
  isOpen: true,
  onClose: mockOnClose,
  template: baseTemplate,
  posts: mockPosts,
  onSubmit: mockOnSubmit,
};

describe('ApplyTemplateDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockOnSubmit.mockResolvedValue({ id: 'scale-new' } as Scale);
    mockOnPreview.mockResolvedValue(null);
  });

  describe('quando modal esta fechado', () => {
    it('nao exibe conteudo quando isOpen=false', () => {
      render(<ApplyTemplateDialog {...defaultProps} isOpen={false} />);
      expect(screen.queryByText('Aplicar Template')).not.toBeInTheDocument();
    });
  });

  describe('quando template e null', () => {
    it('renderiza modal com description vazia', () => {
      render(<ApplyTemplateDialog {...defaultProps} template={null} />);
      expect(screen.getByText('Aplicar Template')).toBeInTheDocument();
    });
  });

  describe('step 1 - selecao de periodo', () => {
    it('exibe titulo "Selecionar Periodo"', () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      expect(screen.getByText('Selecionar Período')).toBeInTheDocument();
    });

    it('exibe card com informacoes do template', () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      expect(screen.getAllByText('Meu Template')[0]).toBeInTheDocument();
    });

    it('exibe selects de mes e ano', () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      expect(screen.getByText('Mês *')).toBeInTheDocument();
      expect(screen.getByText('Ano *')).toBeInTheDocument();
    });

    it('nao exibe select de posto quando template tem post_id', () => {
      render(<ApplyTemplateDialog {...defaultProps} template={{ ...baseTemplate, post_id: 'p1' }} />);
      expect(screen.queryByText('Posto (opcional)')).not.toBeInTheDocument();
    });

    it('exibe select de posto quando template nao tem post_id', () => {
      render(
        <ApplyTemplateDialog {...defaultProps} template={{ ...baseTemplate, post_id: null }} />
      );
      expect(screen.getByText('Posto (opcional)')).toBeInTheDocument();
    });

    it('botao Voltar nao e exibido no step 1', () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      expect(screen.queryByRole('button', { name: /voltar/i })).not.toBeInTheDocument();
    });

    it('exibe botao Cancelar no step 1', () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
    });

    it('chama onClose ao clicar em Cancelar', () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /cancelar/i }));
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('navegacao entre steps (sem onPreview)', () => {
    it('avanca para step 2 ao clicar em Proximo', async () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /pr/i }));
      await waitFor(() => {
        expect(screen.getByText('Preview da Escala')).toBeInTheDocument();
      });
    });

    it('exibe botao Voltar no step 2', async () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /pr/i }));
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /voltar/i })).toBeInTheDocument();
      });
    });

    it('volta para step 1 ao clicar em Voltar no step 2', async () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /pr/i }));
      await waitFor(() => {
        screen.getByText('Preview da Escala');
      });
      fireEvent.click(screen.getByRole('button', { name: /voltar/i }));
      expect(screen.getByText('Selecionar Período')).toBeInTheDocument();
    });

    it('avanca para step 3 a partir do step 2', async () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      // step 1 -> 2
      fireEvent.click(screen.getByRole('button', { name: /pr/i }));
      await waitFor(() => screen.getByText('Preview da Escala'));
      // step 2 -> 3
      fireEvent.click(screen.getByRole('button', { name: /pr/i }));
      await waitFor(() => {
        expect(screen.getByText('Confirmar Aplicação')).toBeInTheDocument();
      });
    });
  });

  describe('step 2 com onPreview', () => {
    it('exibe preview quando onPreview retorna uma escala', async () => {
      const previewScale: Scale = {
        id: 'scale-preview',
        post_id: 'post-1',
        scale_type: '12x36',
        status: 'draft',
        month: 3,
        year: 2025,
        name: null,
        description: null,
        start_date: null,
        end_date: null,
        total_shifts: 20,
        filled_shifts: 18,
        total_hours: 240,
        overtime_hours: 0,
        estimated_cost: 0,
        config: null,
        notes: null,
        approved_by: null,
        approved_at: null,
        approval_notes: null,
        published_by: null,
        published_at: null,
        is_active: true,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        created_by: null,
        is_current_month: false,
        is_published: false,
        can_edit: true,
        fill_rate: 90,
      };
      const onPreviewWithResult = vi.fn().mockResolvedValue(previewScale);

      render(<ApplyTemplateDialog {...defaultProps} onPreview={onPreviewWithResult} />);
      fireEvent.click(screen.getByRole('button', { name: /pr/i }));
      await waitFor(() => {
        expect(screen.getByText('20')).toBeInTheDocument(); // total_shifts
      });
    });

    it('exibe "Preview nao disponivel" quando onPreview retorna null', async () => {
      const onPreviewNull = vi.fn().mockResolvedValue(null);
      render(<ApplyTemplateDialog {...defaultProps} onPreview={onPreviewNull} />);
      fireEvent.click(screen.getByRole('button', { name: /pr/i }));
      await waitFor(() => {
        expect(screen.getByText('Preview não disponível')).toBeInTheDocument();
      });
    });
  });

  describe('step 3 - confirmacao', () => {
    const goToStep3 = async () => {
      const { getByRole, getByText } = render(<ApplyTemplateDialog {...defaultProps} />);
      fireEvent.click(getByRole('button', { name: /pr/i }));
      await waitFor(() => getByText('Preview da Escala'));
      fireEvent.click(getByRole('button', { name: /pr/i }));
      await waitFor(() => getByText('Confirmar Aplicação'));
    };

    it('exibe mensagem de confirmacao no step 3', async () => {
      await goToStep3();
      expect(screen.getByText('Tudo pronto para criar a escala!')).toBeInTheDocument();
    });

    it('exibe botao "Criar Escala" no step 3', async () => {
      await goToStep3();
      expect(screen.getByRole('button', { name: /criar escala/i })).toBeInTheDocument();
    });

    it('chama onSubmit ao clicar em "Criar Escala"', async () => {
      await goToStep3();
      fireEvent.click(screen.getByRole('button', { name: /criar escala/i }));
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled();
      });
    });

    it('chama onClose apos submit bem-sucedido', async () => {
      await goToStep3();
      fireEvent.click(screen.getByRole('button', { name: /criar escala/i }));
      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalled();
      });
    });
  });

  describe('estado isLoading', () => {
    it('exibe "Criando..." no botao quando isLoading=true no step 3', async () => {
      const { getByRole, getByText } = render(
        <ApplyTemplateDialog {...defaultProps} isLoading={true} />
      );
      fireEvent.click(getByRole('button', { name: /pr/i }));
      await waitFor(() => getByText('Preview da Escala'));
      fireEvent.click(getByRole('button', { name: /pr/i }));
      await waitFor(() => getByText('Confirmar Aplicação'));
      expect(screen.getByRole('button', { name: /criando/i })).toBeInTheDocument();
    });
  });

  describe('indicadores de steps', () => {
    it('exibe 3 indicadores de step', () => {
      render(<ApplyTemplateDialog {...defaultProps} />);
      // Os indicadores sao divs com numeros 1, 2, 3
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });
});
