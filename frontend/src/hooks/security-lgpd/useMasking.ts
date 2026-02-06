/**
 * React Query Hooks - Data Masking
 * Hooks para mascaramento de dados sensíveis
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { MaskingService } from '@/services/security-lgpd';
import type {
  MaskDataRequestCategory,
  MaskDataRequestLevel,
} from '@/services/security-lgpd';

/**
 * Hook para mascarar dados
 */
export function useMaskData() {
  return useMutation({
    mutationFn: ({
      data,
      category,
      level,
    }: {
      data: string;
      category: MaskDataRequestCategory;
      level?: MaskDataRequestLevel;
    }) => MaskingService.maskData(data, category, level),
  });
}

/**
 * Hook para listar formatos de mascaramento
 */
export function useMaskingFormats() {
  return useQuery({
    queryKey: ['lgpd', 'masking', 'formats'],
    queryFn: () => MaskingService.listMaskingFormats(),
    staleTime: 60 * 60 * 1000, // 1 hora (dados estáticos)
  });
}

/**
 * Hook para mascarar CPF
 */
export function useMaskCPF() {
  return useMutation({
    mutationFn: ({
      cpf,
      level,
    }: {
      cpf: string;
      level?: MaskDataRequestLevel;
    }) => MaskingService.maskCPF(cpf, level),
  });
}

/**
 * Hook para mascarar email
 */
export function useMaskEmail() {
  return useMutation({
    mutationFn: ({
      email,
      level,
    }: {
      email: string;
      level?: MaskDataRequestLevel;
    }) => MaskingService.maskEmail(email, level),
  });
}

/**
 * Hook para mascarar telefone
 */
export function useMaskPhone() {
  return useMutation({
    mutationFn: ({
      phone,
      level,
    }: {
      phone: string;
      level?: MaskDataRequestLevel;
    }) => MaskingService.maskPhone(phone, level),
  });
}

/**
 * Hook para mascarar nome
 */
export function useMaskName() {
  return useMutation({
    mutationFn: ({
      name,
      level,
    }: {
      name: string;
      level?: MaskDataRequestLevel;
    }) => MaskingService.maskName(name, level),
  });
}

/**
 * Hook para mascarar endereço
 */
export function useMaskAddress() {
  return useMutation({
    mutationFn: ({
      address,
      level,
    }: {
      address: string;
      level?: MaskDataRequestLevel;
    }) => MaskingService.maskAddress(address, level),
  });
}

/**
 * Hook para mascarar cartão de crédito
 */
export function useMaskCreditCard() {
  return useMutation({
    mutationFn: ({
      card,
      level,
    }: {
      card: string;
      level?: MaskDataRequestLevel;
    }) => MaskingService.maskCreditCard(card, level),
  });
}

/**
 * Hook para mascarar em lote
 */
export function useMaskBatch() {
  return useMutation({
    mutationFn: (
      items: Array<{ data: string; category: MaskDataRequestCategory }>
    ) => MaskingService.maskBatch(items),
  });
}
