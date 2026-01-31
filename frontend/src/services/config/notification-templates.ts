/**
 * Service Layer - Notification Templates
 * Templates de notificação multi-canal
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  NotificationTemplateCreate,
  NotificationTemplateUpdate,
  NotificationTemplateRender,
  NotificationTemplateRenderResponse,
  NotificationTemplateResponse,
  NotificationTemplateList,
} from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

const BASE_PATH = '/api/v1/config/templates';

export interface ListNotificationTemplatesParams {
  skip?: number;
  limit?: number;
  channel?: string;
  category?: string;
  status?: string;
  search?: string;
}

/**
 * Lista templates de notificação
 */
export const listNotificationTemplates = async (
  params?: ListNotificationTemplatesParams
): Promise<NotificationTemplateList> => {
  const { data } = await axiosInstance.get<NotificationTemplateList>(
    BASE_PATH,
    { params }
  );
  return data;
};

/**
 * Cria novo template
 */
export const createNotificationTemplate = async (
  template: NotificationTemplateCreate
): Promise<NotificationTemplateResponse> => {
  const { data } = await axiosInstance.post<NotificationTemplateResponse>(
    BASE_PATH,
    template
  );
  return data;
};

/**
 * Obtém template por ID
 */
export const getNotificationTemplate = async (
  templateId: string
): Promise<NotificationTemplateResponse> => {
  const { data } = await axiosInstance.get<NotificationTemplateResponse>(
    `${BASE_PATH}/${templateId}`
  );
  return data;
};

/**
 * Atualiza template
 */
export const updateNotificationTemplate = async (
  templateId: string,
  updates: NotificationTemplateUpdate
): Promise<NotificationTemplateResponse> => {
  const { data } = await axiosInstance.put<NotificationTemplateResponse>(
    `${BASE_PATH}/${templateId}`,
    updates
  );
  return data;
};

/**
 * Deleta template
 */
export const deleteNotificationTemplate = async (
  templateId: string
): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/${templateId}`);
};

// ==================== Controle de Status ====================

/**
 * Ativa template
 */
export const activateNotificationTemplate = async (
  templateId: string
): Promise<NotificationTemplateResponse> => {
  const { data } = await axiosInstance.post<NotificationTemplateResponse>(
    `${BASE_PATH}/${templateId}/activate`
  );
  return data;
};

/**
 * Desativa template
 */
export const deactivateNotificationTemplate = async (
  templateId: string
): Promise<NotificationTemplateResponse> => {
  const { data } = await axiosInstance.post<NotificationTemplateResponse>(
    `${BASE_PATH}/${templateId}/deactivate`
  );
  return data;
};

// ==================== Renderização ====================

/**
 * Renderiza template com variáveis
 */
export const renderNotificationTemplate = async (
  templateId: string,
  render: NotificationTemplateRender
): Promise<NotificationTemplateRenderResponse> => {
  const { data } =
    await axiosInstance.post<NotificationTemplateRenderResponse>(
      `${BASE_PATH}/${templateId}/render`,
      render
    );
  return data;
};

// ==================== Clonagem ====================

/**
 * Clona template
 */
export const cloneNotificationTemplate = async (
  templateId: string
): Promise<NotificationTemplateResponse> => {
  const { data } = await axiosInstance.post<NotificationTemplateResponse>(
    `${BASE_PATH}/${templateId}/clone`
  );
  return data;
};

// ==================== Helpers ====================

/**
 * Verifica se template está ativo
 */
export const isTemplateActive = (
  template: NotificationTemplateResponse
): boolean => {
  return template.ativo;
};

/**
 * Agrupa templates por canal
 */
export const groupTemplatesByChannel = (
  templates: NotificationTemplateResponse[]
): Record<string, NotificationTemplateResponse[]> => {
  return templates.reduce(
    (acc, template) => {
      const channel = template.channel ?? 'unknown';
      if (!acc[channel]) {
        acc[channel] = [];
      }
      acc[channel].push(template);
      return acc;
    },
    {} as Record<string, NotificationTemplateResponse[]>
  );
};

/**
 * Agrupa templates por categoria
 */
export const groupTemplatesByCategory = (
  templates: NotificationTemplateResponse[]
): Record<string, NotificationTemplateResponse[]> => {
  return templates.reduce(
    (acc, template) => {
      const category = template.category ?? 'general';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(template);
      return acc;
    },
    {} as Record<string, NotificationTemplateResponse[]>
  );
};

/**
 * Busca template por código
 */
export const findTemplateByCode = (
  templates: NotificationTemplateResponse[],
  code: string
): NotificationTemplateResponse | undefined => {
  return templates.find((t) => t.codigo === code);
};

/**
 * Filtra templates por canal
 */
export const filterTemplatesByChannel = (
  templates: NotificationTemplateResponse[],
  channel: string
): NotificationTemplateResponse[] => {
  return templates.filter((t) => t.channel === channel);
};

/**
 * Filtra templates ativos
 */
export const filterActiveTemplates = (
  templates: NotificationTemplateResponse[]
): NotificationTemplateResponse[] => {
  return templates.filter((t) => t.ativo);
};

/**
 * Extrai variáveis do template
 * Procura por padrões {{variavel}} no conteúdo
 */
export const extractTemplateVariables = (content: string): string[] => {
  const regex = /\{\{([^}]+)\}\}/g;
  const matches = content.matchAll(regex);
  const variables = new Set<string>();

  for (const match of matches) {
    const variable = match[1].trim();
    variables.add(variable);
  }

  return Array.from(variables);
};

/**
 * Valida se todas as variáveis foram fornecidas
 * Extrai variáveis de todos os campos de conteúdo do template
 */
export const validateTemplateVariables = (
  template: NotificationTemplateResponse,
  variables: Record<string, unknown>
): { valid: boolean; missing: string[] } => {
  // Concatena conteúdo de todos os canais para extrair variáveis
  const allContent = [
    template.email_subject,
    template.sms_body,
    template.push_title,
    template.push_body,
    template.in_app_title,
    template.in_app_body,
  ]
    .filter(Boolean)
    .join(' ');

  const requiredVars = extractTemplateVariables(allContent);
  const providedVars = Object.keys(variables);
  const missing = requiredVars.filter((v) => !providedVars.includes(v));

  return {
    valid: missing.length === 0,
    missing,
  };
};

// ==================== Canais e Categorias ====================

export const NOTIFICATION_CHANNELS = {
  EMAIL: 'email',
  SMS: 'sms',
  PUSH: 'push',
  WHATSAPP: 'whatsapp',
  IN_APP: 'in_app',
} as const;

export const NOTIFICATION_CATEGORIES = {
  SYSTEM: 'system',
  OPERATIONAL: 'operational',
  FINANCIAL: 'financial',
  MARKETING: 'marketing',
  SECURITY: 'security',
  HR: 'hr',
} as const;

export type NotificationChannel =
  (typeof NOTIFICATION_CHANNELS)[keyof typeof NOTIFICATION_CHANNELS];
export type NotificationCategory =
  (typeof NOTIFICATION_CATEGORIES)[keyof typeof NOTIFICATION_CATEGORIES];

/**
 * Obtém label do canal
 */
export const getChannelLabel = (channel: string): string => {
  const labels: Record<string, string> = {
    email: 'E-mail',
    sms: 'SMS',
    push: 'Push Notification',
    whatsapp: 'WhatsApp',
    in_app: 'In-App',
  };
  return labels[channel] || channel;
};

/**
 * Obtém ícone do canal
 */
export const getChannelIcon = (channel: string): string => {
  const icons: Record<string, string> = {
    email: '📧',
    sms: '💬',
    push: '🔔',
    whatsapp: '📱',
    in_app: '🔵',
  };
  return icons[channel] || '📨';
};

/**
 * Obtém label da categoria
 */
export const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    system: 'Sistema',
    operational: 'Operacional',
    financial: 'Financeiro',
    marketing: 'Marketing',
    security: 'Segurança',
    hr: 'RH',
  };
  return labels[category] || category;
};
