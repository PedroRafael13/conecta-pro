/**
 * React Query Hooks - Encryption
 * Hooks para criptografia de dados sensíveis
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { EncryptionService } from '@/services/security-lgpd';
import type { EncryptDataRequestAlgorithm } from '@/services/security-lgpd';

/**
 * Hook para criptografar dados
 */
export function useEncryptData() {
  return useMutation({
    mutationFn: ({
      data,
      algorithm,
      keyId,
    }: {
      data: string;
      algorithm?: EncryptDataRequestAlgorithm;
      keyId?: string;
    }) => EncryptionService.encryptData(data, algorithm, keyId),
  });
}

/**
 * Hook para descriptografar dados
 */
export function useDecryptData() {
  return useMutation({
    mutationFn: ({
      encryptedData,
      keyId,
    }: {
      encryptedData: string;
      keyId?: string;
    }) => EncryptionService.decryptData(encryptedData, keyId),
  });
}

/**
 * Hook para listar algoritmos disponíveis
 */
export function useAlgorithms() {
  return useQuery({
    queryKey: ['lgpd', 'encryption', 'algorithms'],
    queryFn: () => EncryptionService.listAlgorithms(),
    staleTime: 60 * 60 * 1000, // 1 hora (dados estáticos)
  });
}

/**
 * Hook para criptografar CPF
 */
export function useEncryptCPF() {
  return useMutation({
    mutationFn: (cpf: string) => EncryptionService.encryptCPF(cpf),
  });
}

/**
 * Hook para criptografar email
 */
export function useEncryptEmail() {
  return useMutation({
    mutationFn: (email: string) => EncryptionService.encryptEmail(email),
  });
}

/**
 * Hook para criptografar telefone
 */
export function useEncryptPhone() {
  return useMutation({
    mutationFn: (phone: string) => EncryptionService.encryptPhone(phone),
  });
}

/**
 * Hook para criptografar em lote
 */
export function useEncryptBatch() {
  return useMutation({
    mutationFn: (items: string[]) => EncryptionService.encryptBatch(items),
  });
}

/**
 * Hook para descriptografar em lote
 */
export function useDecryptBatch() {
  return useMutation({
    mutationFn: (items: string[]) => EncryptionService.decryptBatch(items),
  });
}
