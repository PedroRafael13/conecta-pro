/**
 * Service Layer - Device Management
 *
 * Gerencia registro de dispositivos para push notifications.
 * Suporta múltiplos dispositivos por usuário (Android/iOS).
 *
 * Features:
 * - Registro de tokens FCM/APNs
 * - Gestão de múltiplos devices
 * - Metadata do dispositivo (modelo, OS, versão app)
 * - Cleanup de tokens inválidos
 *
 * @module services/mobile/deviceService
 */

import { api } from '@/lib/api';
import type {
  DeviceTokenCreate,
  DeviceTokenResponse,
} from '@/types/generated/mobile/conectaPROMobileAPI.schemas';

const BASE_URL = '/api/v1/mobile';

/**
 * Registra dispositivo para notificações push.
 *
 * Armazena token FCM (Android) ou APNs (iOS) para envio
 * de push notifications ao dispositivo.
 *
 * @param deviceData - Dados do dispositivo e token
 * @returns Dados do dispositivo registrado
 */
export async function registerDevice(
  deviceData: DeviceTokenCreate
): Promise<DeviceTokenResponse> {
  const response = await api.post<DeviceTokenResponse>(
    `${BASE_URL}/devices/register`,
    deviceData
  );
  return response.data;
}

/**
 * Remove registro de dispositivo.
 *
 * Desativa push notifications para o dispositivo.
 * Útil em logout ou desinstalação do app.
 *
 * @param deviceId - ID único do dispositivo
 * @returns Confirmação de remoção
 */
export async function unregisterDevice(deviceId: string): Promise<{
  message: string;
}> {
  const response = await api.delete(`${BASE_URL}/devices/${deviceId}`);
  return response.data;
}

/**
 * Helper: Obtém ID único do dispositivo.
 *
 * Em ambiente web, gera ID baseado em características do navegador.
 * Em mobile nativo, deve usar device.uuid.
 *
 * @returns ID único do dispositivo
 */
export function getDeviceId(): string {
  // Para web, gerar baseado em características
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('device_id');
    if (stored) return stored;

    const newId = `web-${Date.now()}-${Math.random().toString(36).substring(7)}`;
    localStorage.setItem('device_id', newId);
    return newId;
  }

  // Para mobile nativo, substituir por device.uuid
  return 'unknown';
}

/**
 * Helper: Detecta plataforma do dispositivo.
 *
 * @returns 'android', 'ios' ou 'web'
 */
export function detectPlatform(): 'android' | 'ios' | 'web' {
  if (typeof window === 'undefined') return 'web';

  const userAgent = window.navigator.userAgent.toLowerCase();

  if (/android/i.test(userAgent)) {
    return 'android';
  }

  if (/iphone|ipad|ipod/i.test(userAgent)) {
    return 'ios';
  }

  return 'web';
}

/**
 * Helper: Obtém informações do dispositivo.
 *
 * @returns Objeto com metadata do dispositivo
 */
export function getDeviceInfo(): {
  device_name: string;
  device_model: string;
  os_version: string;
  app_version: string;
} {
  if (typeof window === 'undefined') {
    return {
      device_name: 'Server',
      device_model: 'Node.js',
      os_version: 'Unknown',
      app_version: '1.0.0',
    };
  }

  const userAgent = window.navigator.userAgent;

  return {
    device_name: detectPlatform().toUpperCase(),
    device_model: userAgent,
    os_version: extractOSVersion(userAgent),
    app_version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  };
}

/**
 * Helper: Extrai versão do OS do user agent.
 */
function extractOSVersion(userAgent: string): string {
  const match = userAgent.match(
    /(?:Android|iPhone OS|iPad OS|Mac OS X)\s([\d._]+)/
  );
  return match?.[1] ? match[1].replace(/_/g, '.') : 'Unknown';
}
