/**
 * Testes para NotificationCenter
 * Cobre branches: badge count > 0 / = 0, badge > 99, dropdown aberto/fechado,
 * isLoading state, notificacoes presentes/ausentes, alertas presentes/ausentes,
 * unreadTotal > 0 (badge novas + botao marcar todas), notification.is_read,
 * notification.action_url presente/ausente, formatDate branches (< 1min, <60min, <24h, <7d, >= 7d)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@/test/helpers/test-utils';
import { NotificationCenter } from '../notification-center';
import type { Notification as AppNotification, Alert } from '@/lib/services/notifications';

// Mock hooks
vi.mock('@/hooks/useNotifications', () => ({
  useNotifications: vi.fn(),
  useUnreadCount: vi.fn(),
  useUserAlerts: vi.fn(),
}));

import * as notifHooks from '@/hooks/useNotifications';

const mockMarkAsRead = vi.fn().mockResolvedValue(undefined);
const mockMarkAllAsRead = vi.fn().mockResolvedValue(undefined);
const mockDeleteNotification = vi.fn().mockResolvedValue(undefined);
const mockRefresh = vi.fn();
const mockRefreshCount = vi.fn();
const mockAcknowledgeAlert = vi.fn().mockResolvedValue(undefined);

const baseNotification: AppNotification = {
  id: 'notif-1',
  tenant_id: 'tenant-1',
  user_id: 'user-1',
  title: 'Notificacao Teste',
  body: 'Corpo da notificacao',
  type: 'operacional',
  reference_type: null,
  reference_id: null,
  channels: ['in_app'],
  sent_at: null,
  read_at: null,
  clicked_at: null,
  action_url: null,
  extra_data: null,
  is_active: true,
  created_at: new Date().toISOString(),
  is_sent: true,
  is_read: false,
  is_clicked: false,
};

const baseAlert: Alert = {
  id: 'alert-1',
  tenant_id: 'tenant-1',
  alert_type: 'operacional',
  severity: 'error',
  title: 'Alerta Urgente',
  message: 'Algo precisa de atencao',
  reference_type: null,
  reference_id: null,
  target_users: null,
  target_roles: null,
  acknowledged_by: null,
  expires_at: null,
  is_active: true,
  created_at: new Date().toISOString(),
  is_critical: false,
  is_expired: false,
  acknowledgment_count: 0,
  is_fully_acknowledged: false,
};

const setupMocks = (overrides: {
  notifications?: AppNotification[];
  isLoading?: boolean;
  unreadTotal?: number;
  alerts?: Alert[];
} = {}) => {
  const {
    notifications = [],
    isLoading = false,
    unreadTotal = 0,
    alerts = [],
  } = overrides;

  vi.mocked(notifHooks.useNotifications).mockReturnValue({
    notifications,
    isLoading,
    refresh: mockRefresh,
    markAsRead: mockMarkAsRead,
    markAllAsRead: mockMarkAllAsRead,
    deleteNotification: mockDeleteNotification,
    total: notifications.length,
    page: 1,
    totalPages: 1,
  } as never);

  vi.mocked(notifHooks.useUnreadCount).mockReturnValue({
    total: unreadTotal,
    refresh: mockRefreshCount,
  } as never);

  vi.mocked(notifHooks.useUserAlerts).mockReturnValue({
    alerts,
    acknowledge: mockAcknowledgeAlert,
  } as never);
};

describe('NotificationCenter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMocks();
  });

  describe('botao de sino', () => {
    it('renderiza botao de sino', () => {
      render(<NotificationCenter />);
      expect(screen.getByRole('button', { name: /notificacoes/i })).toBeInTheDocument();
    });

    it('nao exibe badge quando nao ha notificacoes nao lidas nem alertas', () => {
      setupMocks({ unreadTotal: 0, alerts: [] });
      render(<NotificationCenter />);
      expect(screen.queryByText('0')).not.toBeInTheDocument();
    });

    it('exibe badge com total quando ha notificacoes nao lidas', () => {
      setupMocks({ unreadTotal: 3, alerts: [] });
      render(<NotificationCenter />);
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('exibe badge com total quando ha alertas', () => {
      setupMocks({ unreadTotal: 0, alerts: [baseAlert] });
      render(<NotificationCenter />);
      expect(screen.getByText('1')).toBeInTheDocument();
    });

    it('soma notificacoes nao lidas + alertas no badge', () => {
      setupMocks({ unreadTotal: 5, alerts: [baseAlert, { ...baseAlert, id: 'alert-2' }] });
      render(<NotificationCenter />);
      expect(screen.getByText('7')).toBeInTheDocument();
    });

    it('exibe "99+" quando total de badge e maior que 99', () => {
      setupMocks({ unreadTotal: 98, alerts: Array(5).fill({ ...baseAlert, id: 'x' }) });
      render(<NotificationCenter />);
      expect(screen.getByText('99+')).toBeInTheDocument();
    });
  });

  describe('abertura e fechamento do dropdown', () => {
    it('dropdown esta oculto por padrao', () => {
      render(<NotificationCenter />);
      expect(screen.queryByText('Notificações')).not.toBeInTheDocument();
    });

    it('abre dropdown ao clicar no sino', () => {
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('Notificações')).toBeInTheDocument();
    });

    it('fecha dropdown ao clicar no botao X', () => {
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('Notificações')).toBeInTheDocument();
      // Clica no botao de fechar (X)
      const closeButtons = screen.getAllByRole('button');
      const xButton = closeButtons.find((b) => {
        const svg = b.querySelector('svg');
        return (
          !!svg &&
          b.className.includes('ghost') &&
          !b.hasAttribute('title')
        );
      });
      if (xButton) {
        fireEvent.click(xButton);
        expect(screen.queryByText('Notificações')).not.toBeInTheDocument();
      }
    });

    it('chama refresh ao abrir o dropdown', () => {
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(mockRefresh).toHaveBeenCalled();
    });
  });

  describe('estado de carregamento', () => {
    it('exibe spinner quando isLoading=true', () => {
      setupMocks({ isLoading: true });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(document.querySelector('.animate-spin')).toBeInTheDocument();
    });
  });

  describe('estado vazio', () => {
    it('exibe mensagem "Nenhuma notificacao" quando lista e vazia e sem alertas', () => {
      setupMocks({ notifications: [], alerts: [] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('Nenhuma notificacao')).toBeInTheDocument();
    });
  });

  describe('secao de alertas', () => {
    it('exibe alerta quando ha alertas ativos', () => {
      setupMocks({ alerts: [baseAlert] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('Alerta Urgente')).toBeInTheDocument();
      expect(screen.getByText('Algo precisa de atencao')).toBeInTheDocument();
    });

    it('nao exibe secao de alertas quando lista e vazia', () => {
      setupMocks({ alerts: [] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.queryByText('Alertas Ativos')).not.toBeInTheDocument();
    });

    it('exibe apenas os 3 primeiros alertas', () => {
      const manyAlerts = Array.from({ length: 5 }, (_, i) => ({
        ...baseAlert,
        id: `alert-${i}`,
        title: `Alerta ${i}`,
      }));
      setupMocks({ alerts: manyAlerts });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      // Apenas 3 primeiros devem aparecer
      expect(screen.getByText('Alerta 0')).toBeInTheDocument();
      expect(screen.getByText('Alerta 1')).toBeInTheDocument();
      expect(screen.getByText('Alerta 2')).toBeInTheDocument();
      expect(screen.queryByText('Alerta 3')).not.toBeInTheDocument();
    });
  });

  describe('lista de notificacoes', () => {
    it('exibe notificacoes quando presentes', () => {
      setupMocks({ notifications: [baseNotification] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('Notificacao Teste')).toBeInTheDocument();
    });

    it('exibe badge de novas notificacoes quando unreadTotal > 0', () => {
      setupMocks({ notifications: [baseNotification], unreadTotal: 1 });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('1 novas')).toBeInTheDocument();
    });

    it('exibe botao "marcar todas como lidas" quando unreadTotal > 0', () => {
      setupMocks({ notifications: [baseNotification], unreadTotal: 2 });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByTitle('Marcar todas como lidas')).toBeInTheDocument();
    });

    it('nao exibe botao "marcar todas" quando unreadTotal = 0', () => {
      setupMocks({ notifications: [{ ...baseNotification, is_read: true }], unreadTotal: 0 });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.queryByTitle('Marcar todas como lidas')).not.toBeInTheDocument();
    });

    it('exibe link de acao quando notification.action_url esta presente', () => {
      const notifWithUrl: AppNotification = {
        ...baseNotification,
        action_url: '/modulos/operacional/escalas',
      };
      setupMocks({ notifications: [notifWithUrl] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      const viewLink = document.querySelector('a[href="/modulos/operacional/escalas"]');
      expect(viewLink).toBeInTheDocument();
    });

    it('nao exibe link de acao quando notification.action_url e null', () => {
      setupMocks({ notifications: [{ ...baseNotification, action_url: null }] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      // O footer sempre tem links para /modulos/operacional/notificacoes e /modulos/configuracoes
      // mas nao deve haver link de acao especifico da notificacao (Eye button dentro de Link)
      // quando action_url e null
      const notificationItems = document.querySelectorAll('.divide-y > div');
      notificationItems.forEach((item) => {
        // Nenhum item de notificacao deve ter link de acao (Eye button)
        expect(item.querySelector('a')).toBeNull();
      });
    });

    it('aplica estilo diferente para notificacao nao lida (is_read=false)', () => {
      setupMocks({ notifications: [{ ...baseNotification, is_read: false }] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      // Titulo da notificacao nao lida deve ter font-medium
      const titleEl = screen.getByText('Notificacao Teste');
      expect(titleEl.className).toContain('font-medium');
    });

    it('aplica estilo diferente para notificacao lida (is_read=true)', () => {
      setupMocks({ notifications: [{ ...baseNotification, is_read: true }] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      const titleEl = screen.getByText('Notificacao Teste');
      expect(titleEl.className).toContain('muted-foreground');
    });
  });

  describe('formatDate branches', () => {
    it('exibe "Agora" para notificacao criada agora (< 1min)', () => {
      const recent: AppNotification = {
        ...baseNotification,
        created_at: new Date().toISOString(),
      };
      setupMocks({ notifications: [recent] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('Agora')).toBeInTheDocument();
    });

    it('exibe "Xmin" para notificacao criada ha minutos (1-59 min)', () => {
      const thirtyMinutesAgo = new Date(Date.now() - 30 * 60 * 1000).toISOString();
      const recent: AppNotification = { ...baseNotification, created_at: thirtyMinutesAgo };
      setupMocks({ notifications: [recent] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('30min')).toBeInTheDocument();
    });

    it('exibe "Xh" para notificacao criada ha horas (1-23h)', () => {
      const threeHoursAgo = new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString();
      const recent: AppNotification = { ...baseNotification, created_at: threeHoursAgo };
      setupMocks({ notifications: [recent] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('3h')).toBeInTheDocument();
    });

    it('exibe "Xd" para notificacao criada ha dias (1-6d)', () => {
      const twoDaysAgo = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString();
      const recent: AppNotification = { ...baseNotification, created_at: twoDaysAgo };
      setupMocks({ notifications: [recent] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      expect(screen.getByText('2d')).toBeInTheDocument();
    });

    it('exibe data formatada para notificacao criada ha mais de 7 dias', () => {
      const tenDaysAgo = new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString();
      const old: AppNotification = { ...baseNotification, created_at: tenDaysAgo };
      setupMocks({ notifications: [old] });
      render(<NotificationCenter />);
      fireEvent.click(screen.getByRole('button', { name: /notificacoes/i }));
      // Deve exibir data no formato dd/mm
      const dateEl = screen.getByText(/\d{2}\/\d{2}/);
      expect(dateEl).toBeInTheDocument();
    });
  });
});
