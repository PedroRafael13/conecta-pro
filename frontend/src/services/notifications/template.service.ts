/**
 * Template Service
 *
 * Service layer para gerenciamento de templates de notificação
 * Cobre: criação, atualização, listagem, versionamento
 */

import { api } from '@/lib/api';
import type {
  TemplateCreate,
  TemplateUpdate,
  TemplateResponse,
  TemplateVariableSchema,
} from '@/types/generated/notifications/conectaPRONotificationsModule.schemas';

/**
 * Interface para variável de template tipada (para uso interno)
 */
interface TypedTemplateVariable {
  name: string;
  type?: string;
  required?: boolean;
  default?: unknown;
  description?: string;
}

/**
 * Converte variável genérica para tipada
 */
function toTypedVariable(v: { [key: string]: unknown }): TypedTemplateVariable {
  return {
    name: String(v.name ?? ''),
    type: v.type as string | undefined,
    required: Boolean(v.required),
    default: v.default,
    description: v.description as string | undefined,
  };
}

export class TemplateService {
  private readonly basePath = '/api/v1/notifications/templates';

  /**
   * Lista templates de notificação
   */
  async list(params?: {
    category?: string;
    template_status?: string;
    active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<TemplateResponse[]> {
    const response = await api.get<TemplateResponse[]>(this.basePath, { params });
    return response.data;
  }

  /**
   * Cria novo template
   */
  async create(data: TemplateCreate): Promise<TemplateResponse> {
    const response = await api.post<TemplateResponse>(this.basePath, data);
    return response.data;
  }

  /**
   * Obtém detalhes de um template
   */
  async get(templateId: string): Promise<TemplateResponse> {
    const response = await api.get<TemplateResponse>(`${this.basePath}/${templateId}`);
    return response.data;
  }

  /**
   * Atualiza template existente
   */
  async update(
    templateId: string,
    data: TemplateUpdate
  ): Promise<TemplateResponse> {
    const response = await api.patch<TemplateResponse>(`${this.basePath}/${templateId}`, data);
    return response.data;
  }

  /**
   * Busca template por slug
   */
  async getBySlug(slug: string): Promise<TemplateResponse | null> {
    const templates = await this.list({ active: true });
    return templates.find((t) => t.slug === slug) || null;
  }

  /**
   * Lista templates por categoria
   */
  async listByCategory(category: string): Promise<TemplateResponse[]> {
    return this.list({ category, active: true });
  }

  /**
   * Valida variáveis do template
   */
  validateVariables(
    template: TemplateResponse,
    variables: Record<string, unknown>
  ): { valid: boolean; missing: string[] } {
    const templateVars = (template.variables || []).map(toTypedVariable);
    const provided = Object.keys(variables);
    const required = templateVars
      .filter((v) => v.required)
      .map((v) => v.name);

    const missing = required.filter((r) => !provided.includes(r));

    return {
      valid: missing.length === 0,
      missing,
    };
  }

  /**
   * Renderiza template com variáveis
   */
  renderTemplate(content: string, variables: Record<string, unknown>): string {
    let rendered = content;

    Object.entries(variables).forEach(([key, value]) => {
      const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
      rendered = rendered.replace(regex, String(value));
    });

    return rendered;
  }
}

export const templateService = new TemplateService();
