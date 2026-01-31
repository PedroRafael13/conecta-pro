/**
 * Data Masking Service
 * Mascaramento de Dados Sensíveis LGPD
 *
 * Serviço para mascaramento de PII (Personally Identifiable Information):
 * - Mascaramento de CPF, email, telefone, nome, endereço, cartão
 * - Níveis de mascaramento (parcial, total, customizado)
 * - Formatos de mascaramento
 */

import { getLgpdMascaramento } from '@/types/generated/security-lgpd/lgpd-mascaramento/lgpd-mascaramento';
import type {
  MaskDataRequest,
  MaskDataRequestCategory,
  MaskDataRequestLevel,
  StandardResponse,
} from '@/types/generated/security-lgpd/conectaPROLGPDSecurityAPI.schemas';
import { AxiosResponse } from 'axios';

const maskingApi = getLgpdMascaramento();

/**
 * Service para mascaramento de dados sensíveis
 */
export class MaskingService {
  /**
   * Mascara dados sensíveis conforme categoria
   */
  static async maskData(
    data: string,
    category: MaskDataRequestCategory,
    level: MaskDataRequestLevel = 'partial'
  ): Promise<AxiosResponse<StandardResponse>> {
    const request: MaskDataRequest = {
      data,
      category,
      level,
    };

    return maskingApi.maskData(request);
  }

  /**
   * Lista formatos de mascaramento disponíveis
   */
  static async listMaskingFormats(): Promise<AxiosResponse<StandardResponse>> {
    return maskingApi.listMaskingFormats();
  }

  /**
   * Mascara CPF (xxx.xxx.xxx-XX)
   */
  static async maskCPF(
    cpf: string,
    level: MaskDataRequestLevel = 'partial'
  ): Promise<string> {
    const response = await this.maskData(cpf, 'cpf', level);
    return response.data.data?.masked_data as string;
  }

  /**
   * Mascara email (user***@domain.com)
   */
  static async maskEmail(
    email: string,
    level: MaskDataRequestLevel = 'partial'
  ): Promise<string> {
    const response = await this.maskData(email, 'email', level);
    return response.data.data?.masked_data as string;
  }

  /**
   * Mascara telefone ((XX) XXXXX-XXXX)
   */
  static async maskPhone(
    phone: string,
    level: MaskDataRequestLevel = 'partial'
  ): Promise<string> {
    const response = await this.maskData(phone, 'phone', level);
    return response.data.data?.masked_data as string;
  }

  /**
   * Mascara nome (João ***)
   */
  static async maskName(
    name: string,
    level: MaskDataRequestLevel = 'partial'
  ): Promise<string> {
    const response = await this.maskData(name, 'name', level);
    return response.data.data?.masked_data as string;
  }

  /**
   * Mascara endereço
   */
  static async maskAddress(
    address: string,
    level: MaskDataRequestLevel = 'partial'
  ): Promise<string> {
    const response = await this.maskData(address, 'address', level);
    return response.data.data?.masked_data as string;
  }

  /**
   * Mascara cartão de crédito
   */
  static async maskCreditCard(
    card: string,
    level: MaskDataRequestLevel = 'partial'
  ): Promise<string> {
    const response = await this.maskData(card, 'credit_card', level);
    return response.data.data?.masked_data as string;
  }

  /**
   * Mascara dados em lote
   */
  static async maskBatch(
    items: Array<{ data: string; category: MaskDataRequestCategory }>
  ): Promise<Array<{ original: string; masked: string; category: string }>> {
    const results = await Promise.all(
      items.map(async (item) => {
        const response = await this.maskData(item.data, item.category);
        return {
          original: item.data,
          masked: response.data.data?.masked_data as string,
          category: item.category,
        };
      })
    );

    return results;
  }

  /**
   * Mascaramento local (frontend-only) para CPF
   * Não envia para o servidor, útil para exibição rápida
   */
  static maskCPFLocal(cpf: string, level: MaskDataRequestLevel = 'partial'): string {
    const cleaned = cpf.replace(/\D/g, '');

    if (level === 'full') {
      return '***.***.***-**';
    }

    if (level === 'partial' && cleaned.length === 11) {
      return `***.${cleaned.substring(3, 6)}.${cleaned.substring(6, 9)}-${cleaned.substring(9)}`;
    }

    return cpf;
  }

  /**
   * Mascaramento local para email
   */
  static maskEmailLocal(email: string, level: MaskDataRequestLevel = 'partial'): string {
    if (level === 'full') {
      return '***@***.***';
    }

    const [localPart, domain] = email.split('@');
    if (!domain) return email;

    if (level === 'partial') {
      const visibleChars = Math.min(3, Math.floor(localPart.length / 2));
      const masked = localPart.substring(0, visibleChars) + '***';
      return `${masked}@${domain}`;
    }

    return email;
  }

  /**
   * Mascaramento local para telefone
   */
  static maskPhoneLocal(phone: string, level: MaskDataRequestLevel = 'partial'): string {
    const cleaned = phone.replace(/\D/g, '');

    if (level === 'full') {
      return '(**) *****-****';
    }

    if (level === 'partial' && cleaned.length >= 10) {
      const ddd = cleaned.substring(0, 2);
      const lastDigits = cleaned.substring(cleaned.length - 4);
      return `(${ddd}) *****-${lastDigits}`;
    }

    return phone;
  }

  /**
   * Formata categoria para exibição
   */
  static formatCategory(category: MaskDataRequestCategory): string {
    const formats: Record<MaskDataRequestCategory, string> = {
      cpf: 'CPF',
      email: 'E-mail',
      phone: 'Telefone',
      name: 'Nome',
      address: 'Endereço',
      credit_card: 'Cartão de Crédito',
    };
    return formats[category];
  }

  /**
   * Formata nível de mascaramento
   */
  static formatLevel(level: MaskDataRequestLevel): string {
    const formats: Record<MaskDataRequestLevel, string> = {
      partial: 'Parcial',
      full: 'Total',
      custom: 'Personalizado',
    };
    return formats[level];
  }

  /**
   * Retorna descrição do nível
   */
  static getLevelDescription(level: MaskDataRequestLevel): string {
    const descriptions: Record<MaskDataRequestLevel, string> = {
      partial: 'Exibe apenas parte dos dados, mantendo alguns caracteres visíveis',
      full: 'Oculta completamente todos os dados',
      custom: 'Aplica regras personalizadas de mascaramento',
    };
    return descriptions[level];
  }

  /**
   * Valida se dado precisa de mascaramento
   */
  static needsMasking(
    data: string,
    category: MaskDataRequestCategory
  ): boolean {
    if (!data || data.length === 0) return false;

    // Patterns para validação
    const patterns: Record<MaskDataRequestCategory, RegExp> = {
      cpf: /^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$/,
      email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      phone: /^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$/,
      name: /^[a-zA-ZÀ-ÿ\s]{3,}$/,
      address: /.{10,}/,
      credit_card: /^\d{4}\s?\d{4}\s?\d{4}\s?\d{4}$/,
    };

    return patterns[category]?.test(data) || false;
  }

  /**
   * Detecta categoria automaticamente
   */
  static detectCategory(data: string): MaskDataRequestCategory | null {
    const patterns: Array<{ category: MaskDataRequestCategory; regex: RegExp }> = [
      { category: 'cpf', regex: /^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$/ },
      { category: 'email', regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
      { category: 'phone', regex: /^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$/ },
      { category: 'credit_card', regex: /^\d{4}\s?\d{4}\s?\d{4}\s?\d{4}$/ },
    ];

    for (const pattern of patterns) {
      if (pattern.regex.test(data)) {
        return pattern.category;
      }
    }

    return null;
  }

  /**
   * Retorna exemplo de mascaramento
   */
  static getMaskingExample(
    category: MaskDataRequestCategory,
    level: MaskDataRequestLevel
  ): { original: string; masked: string } {
    const examples: Record<
      MaskDataRequestCategory,
      Record<MaskDataRequestLevel, { original: string; masked: string }>
    > = {
      cpf: {
        partial: {
          original: '123.456.789-00',
          masked: '***.456.789-00',
        },
        full: { original: '123.456.789-00', masked: '***.***.***-**' },
        custom: {
          original: '123.456.789-00',
          masked: '***.***.789-**',
        },
      },
      email: {
        partial: { original: 'usuario@exemplo.com', masked: 'usu***@exemplo.com' },
        full: { original: 'usuario@exemplo.com', masked: '***@***.***' },
        custom: { original: 'usuario@exemplo.com', masked: 'u*****o@exemplo.com' },
      },
      phone: {
        partial: { original: '(11) 98765-4321', masked: '(11) *****-4321' },
        full: { original: '(11) 98765-4321', masked: '(**) *****-****' },
        custom: { original: '(11) 98765-4321', masked: '(11) ***65-****' },
      },
      name: {
        partial: { original: 'João Silva Santos', masked: 'João ***' },
        full: { original: 'João Silva Santos', masked: '*** ***' },
        custom: { original: 'João Silva Santos', masked: 'J*** S*** S***' },
      },
      address: {
        partial: {
          original: 'Rua das Flores, 123',
          masked: 'Rua das Flores, ***',
        },
        full: { original: 'Rua das Flores, 123', masked: '*** *** ***, ***' },
        custom: {
          original: 'Rua das Flores, 123',
          masked: 'Rua *** ***, 123',
        },
      },
      credit_card: {
        partial: {
          original: '1234 5678 9012 3456',
          masked: '**** **** **** 3456',
        },
        full: {
          original: '1234 5678 9012 3456',
          masked: '**** **** **** ****',
        },
        custom: {
          original: '1234 5678 9012 3456',
          masked: '1234 **** **** 3456',
        },
      },
    };

    return examples[category][level];
  }
}

export default MaskingService;
