/**
 * Hooks React Query - Integration Settings (Migrado para Orval)
 * Gestão de Integrações
 *
 * MIGRADO: Re-exports dos hooks Orval gerados
 */

// Re-export dos hooks Orval com nomes simplificados
export {
  useListIntegrationsApiV1ClientsClientsClientIdIntegrationsGet as useIntegrations,
  useGetIntegrationApiV1ClientsClientsIntegrationsSettingsIdGet as useIntegration,
  useCreateIntegrationApiV1ClientsClientsClientIdIntegrationsPost as useCreateIntegration,
  useUpdateIntegrationApiV1ClientsClientsIntegrationsSettingsIdPut as useUpdateIntegration,
  useEnableIntegrationApiV1ClientsClientsIntegrationsSettingsIdEnablePost as useEnableIntegration,
  useDisableIntegrationApiV1ClientsClientsIntegrationsSettingsIdDisablePost as useDisableIntegration,
} from '@/types/generated/clients/clients-cadastro';
