/**
 * Service Layer - Campo Service (CAMPO)
 * Gestão de técnicos, tickets e serviços de campo
 */

import * as CampoServiceAPI from '@/api/campo/generated/campo/campo';
import type {
  TechnicianInfo,
  TicketRequest,
  TicketUpdate,
  ListTechniciansApiV1CampoGuardianCampoCampoTechniciansGetParams,
} from '@/api/campo/generated/models';

export class CampoServiceMain {
  /**
   * Dashboard principal do módulo CAMPO
   */
  async dashboard(params?: { periodo?: string }) {
    return CampoServiceAPI.campoDashboardApiV1CampoGuardianCampoCampoDashboardGet();
  }

  /**
   * Lista todos os técnicos
   */
  async listarTecnicos(params?: ListTechniciansApiV1CampoGuardianCampoCampoTechniciansGetParams) {
    return CampoServiceAPI.listTechniciansApiV1CampoGuardianCampoCampoTechniciansGet(params);
  }

  /**
   * Cria novo técnico
   */
  async criarTecnico(data: TechnicianInfo) {
    return CampoServiceAPI.createTechnicianApiV1CampoGuardianCampoCampoTechniciansPost(data);
  }

  /**
   * Busca técnico por ID
   * TODO: Endpoint não disponível na API - implementar quando disponível
   */
  async buscarTecnico(tecnicoId: string) {
    throw new Error('Endpoint getTechnicianApiV1CampoCampoTechniciansTecnicoIdGet não disponível na API');
  }

  /**
   * Atualiza dados do técnico
   * TODO: Endpoint não disponível na API - implementar quando disponível
   */
  async atualizarTecnico(tecnicoId: string, data: Partial<TechnicianInfo>) {
    throw new Error('Endpoint updateTechnicianApiV1CampoCampoTechniciansTecnicoIdPatch não disponível na API');
  }

  /**
   * Desativa técnico
   * TODO: Endpoint não disponível na API - implementar quando disponível
   */
  async desativarTecnico(tecnicoId: string) {
    throw new Error('Endpoint deactivateTechnicianApiV1CampoCampoTechniciansTecnicoIdDesativarPost não disponível na API');
  }

  /**
   * Cria novo ticket
   */
  async criarTicket(data: TicketRequest) {
    return CampoServiceAPI.createTicketApiV1CampoGuardianCampoCampoTicketsPost(data);
  }

  /**
   * Lista tickets
   * TODO: Endpoint não disponível na API - implementar quando disponível
   */
  async listarTickets(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    prioridade?: string;
    tecnico_id?: string;
  }) {
    throw new Error('Endpoint listTicketsApiV1CampoCampoTicketsGet não disponível na API');
  }

  /**
   * Busca ticket por ID
   */
  async buscarTicket(ticketId: string) {
    return CampoServiceAPI.getTicketApiV1CampoGuardianCampoCampoTicketsTicketIdGet(ticketId);
  }

  /**
   * Atualiza ticket
   */
  async atualizarTicket(ticketId: string, data: TicketUpdate) {
    return CampoServiceAPI.updateTicketApiV1CampoGuardianCampoCampoTicketsTicketIdPut(ticketId, data);
  }

  /**
   * Atribui ticket a técnico
   */
  async atribuirTicket(ticketId: string, tecnicoId: string) {
    return CampoServiceAPI.assignTechnicianApiV1CampoGuardianCampoCampoTicketsTicketIdAssignTechnicianIdPost(ticketId, tecnicoId);
  }
}

export const campoServiceMain = new CampoServiceMain();
