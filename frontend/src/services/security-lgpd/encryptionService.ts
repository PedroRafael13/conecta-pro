/**
 * Encryption Service
 * Serviço de Criptografia de Dados Sensíveis LGPD
 *
 * Implementa criptografia conforme requisitos LGPD:
 * - Criptografia de dados (AES-256-GCM, AES-256-CBC, Fernet, ChaCha20-Poly1305, RSA-OAEP)
 * - Descriptografia segura
 * - Gestão de algoritmos
 */

import { getLgpdCriptografia } from '@/types/generated/security-lgpd/lgpd-criptografia/lgpd-criptografia';
import type {
  EncryptDataRequest,
  DecryptDataRequest,
  EncryptDataRequestAlgorithm,
  StandardResponse,
} from '@/types/generated/security-lgpd/conectaPROLGPDSecurityAPI.schemas';
import { AxiosResponse } from 'axios';

const encryptionApi = getLgpdCriptografia();

/**
 * Service para criptografia de dados sensíveis
 */
export class EncryptionService {
  /**
   * Criptografa dados sensíveis
   * @param data Dados a serem criptografados
   * @param algorithm Algoritmo de criptografia (padrão: AES-256-GCM)
   * @param keyId ID da chave (opcional)
   */
  static async encryptData(
    data: string,
    algorithm: EncryptDataRequestAlgorithm = 'AES-256-GCM',
    keyId?: string
  ): Promise<AxiosResponse<StandardResponse>> {
    const request: EncryptDataRequest = {
      data,
      algorithm,
      key_id: keyId,
    };

    return encryptionApi.encryptData(request);
  }

  /**
   * Descriptografa dados
   * @param encryptedData Dados criptografados em base64
   * @param keyId ID da chave
   */
  static async decryptData(
    encryptedData: string,
    keyId?: string
  ): Promise<AxiosResponse<StandardResponse>> {
    const request: DecryptDataRequest = {
      encrypted_data: encryptedData,
      key_id: keyId,
    };

    return encryptionApi.decryptData(request);
  }

  /**
   * Lista algoritmos de criptografia disponíveis
   */
  static async listAlgorithms(): Promise<AxiosResponse<StandardResponse>> {
    return encryptionApi.listAlgorithms();
  }

  /**
   * Criptografa CPF
   * Helper específico para CPF
   */
  static async encryptCPF(cpf: string): Promise<string> {
    const response = await EncryptionService.encryptData(cpf, 'AES-256-GCM');
    return response.data.data?.encrypted_data as string;
  }

  /**
   * Criptografa Email
   * Helper específico para email
   */
  static async encryptEmail(email: string): Promise<string> {
    const response = await EncryptionService.encryptData(email, 'AES-256-GCM');
    return response.data.data?.encrypted_data as string;
  }

  /**
   * Criptografa Telefone
   * Helper específico para telefone
   */
  static async encryptPhone(phone: string): Promise<string> {
    const response = await EncryptionService.encryptData(phone, 'AES-256-GCM');
    return response.data.data?.encrypted_data as string;
  }

  /**
   * Criptografa em lote
   * @param items Array de dados a serem criptografados
   */
  static async encryptBatch(
    items: string[]
  ): Promise<Array<{ original: string; encrypted: string }>> {
    const results = await Promise.all(
      items.map(async (item) => {
        const response = await this.encryptData(item);
        return {
          original: item,
          encrypted: response.data.data?.encrypted_data as string,
        };
      })
    );

    return results;
  }

  /**
   * Descriptografa em lote
   * @param items Array de dados criptografados
   */
  static async decryptBatch(
    items: string[]
  ): Promise<Array<{ encrypted: string; decrypted: string }>> {
    const results = await Promise.all(
      items.map(async (item) => {
        const response = await this.decryptData(item);
        return {
          encrypted: item,
          decrypted: response.data.data?.decrypted_data as string,
        };
      })
    );

    return results;
  }

  /**
   * Formata nome do algoritmo para exibição
   */
  static formatAlgorithmName(algorithm: EncryptDataRequestAlgorithm): string {
    const names: Record<string, string> = {
      'AES-256-GCM': 'AES-256-GCM (Recomendado)',
      'AES-256-CBC': 'AES-256-CBC',
      'Fernet': 'Fernet (Symmetric)',
      'ChaCha20-Poly1305': 'ChaCha20-Poly1305',
      'RSA-OAEP': 'RSA-OAEP (Asymmetric)',
    };

    return names[algorithm] || algorithm;
  }

  /**
   * Retorna descrição do algoritmo
   */
  static getAlgorithmDescription(
    algorithm: EncryptDataRequestAlgorithm
  ): string {
    const descriptions: Record<string, string> = {
      'AES-256-GCM':
        'Advanced Encryption Standard com modo GCM. Oferece criptografia autenticada de alta segurança.',
      'AES-256-CBC':
        'Advanced Encryption Standard com modo CBC. Algoritmo padrão da indústria.',
      'Fernet':
        'Criptografia simétrica com autenticação. Ideal para tokens e sessões.',
      'ChaCha20-Poly1305':
        'Cifra de stream moderna e rápida com autenticação.',
      'RSA-OAEP':
        'Criptografia assimétrica RSA. Ideal para chaves e pequenos dados.',
    };

    return descriptions[algorithm] || 'Algoritmo de criptografia';
  }

  /**
   * Valida se dados estão criptografados
   */
  static isEncrypted(data: string): boolean {
    // Base64 pattern validation
    const base64Pattern = /^[A-Za-z0-9+/]+={0,2}$/;
    return base64Pattern.test(data) && data.length > 20;
  }

  /**
   * Calcula força da criptografia
   */
  static getStrengthLevel(
    algorithm: EncryptDataRequestAlgorithm
  ): 'high' | 'medium' | 'standard' {
    if (algorithm === 'AES-256-GCM' || algorithm === 'ChaCha20-Poly1305') {
      return 'high';
    }
    if (algorithm === 'RSA-OAEP') {
      return 'medium';
    }
    return 'standard';
  }
}

export default EncryptionService;
