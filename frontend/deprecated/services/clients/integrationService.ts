/**
 * Service Layer - Integration Settings (DEPRECATED)
 * Gestão de Configurações de Integrações
 *
 * @deprecated Use hooks Orval de @/types/generated/clients/clients-cadastro/clients-cadastro
 *
 * Mapeamento de hooks:
 * - integrationService.list -> useListIntegrationsApiV1ClientsClientsClientIdIntegrationsGet
 * - integrationService.getById -> useGetIntegrationApiV1ClientsClientsIntegrationsSettingsIdGet
 * - integrationService.create -> useCreateIntegrationApiV1ClientsClientsClientIdIntegrationsPost
 * - integrationService.update -> useUpdateIntegrationApiV1ClientsClientsIntegrationsSettingsIdPut
 * - integrationService.enable -> useEnableIntegrationApiV1ClientsClientsIntegrationsSettingsIdEnablePost
 * - integrationService.disable -> useDisableIntegrationApiV1ClientsClientsIntegrationsSettingsIdDisablePost
 */

// Re-export dos hooks Orval para compatibilidade
export {
  useListIntegrationsApiV1ClientsClientsClientIdIntegrationsGet as useListIntegrations,
  useGetIntegrationApiV1ClientsClientsIntegrationsSettingsIdGet as useGetIntegration,
  useCreateIntegrationApiV1ClientsClientsClientIdIntegrationsPost as useCreateIntegration,
  useUpdateIntegrationApiV1ClientsClientsIntegrationsSettingsIdPut as useUpdateIntegration,
  useEnableIntegrationApiV1ClientsClientsIntegrationsSettingsIdEnablePost as useEnableIntegration,
  useDisableIntegrationApiV1ClientsClientsIntegrationsSettingsIdDisablePost as useDisableIntegration,
} from '@/types/generated/clients/clients-cadastro';
