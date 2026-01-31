/**
 * Service Layer - Sync e Certificates
 *
 * Endpoints: Sincronização de Dados, Gestão de Certificados Digitais, Jobs
 */

import api from '@/lib/api';
import type {
  CertificateUploadResponse,
  CertificateInfoResponse,
  CertificateListResponse,
  CertificateValidationResponse,
  CertificateDeleteResponse,
  JobListResponse,
  JobExecResponse,
  DashboardResponse,
  ExtracaoResponse,
  HistoricoExtracaoResponse,
  AlertaCertificado,
  EventoRecente,
  StandardResponse,
} from '@/types/generated/government';

// Tipos locais para a camada de serviço
export interface IniciarExtracaoParams {
  servico: 'nfe' | 'cte' | 'mdfe' | 'fgts' | 'esocial' | 'sped' | 'todos';
  periodo_inicial: string;
  periodo_final: string;
  modo?: 'completo' | 'incremental';
}

export interface AgendamentoSyncParams {
  servico: string;
  periodicidade: 'diaria' | 'semanal' | 'mensal';
  horario: string;
  ativo: boolean;
}

export interface UploadCertificadoParams {
  arquivo: File;
  senha: string;
  nome?: string;
  validade?: string;
}

export interface JobExecutionParams {
  tipo: string;
  parametros?: Record<string, unknown>;
}

// Tipos locais para agendamentos
interface AgendamentoSync {
  servico: string;
  periodicidade: 'diaria' | 'semanal' | 'mensal';
  horario: string;
  ativo: boolean;
}

/**
 * Inicia extração de dados governamentais
 */
export async function iniciarExtracao(
  params: IniciarExtracaoParams
): Promise<ExtracaoResponse> {
  const { data } = await api.post<ExtracaoResponse>(
    '/api/v1/government/extracao/iniciar',
    {
      servico: params.servico,
      periodo_inicial: params.periodo_inicial,
      periodo_final: params.periodo_final,
      modo: params.modo,
    }
  );
  return data;
}

/**
 * Sincroniza NF-e rapidamente
 */
export async function sincronizarNFeRapido(params: {
  periodo_dias?: number;
}): Promise<StandardResponse> {
  const formData = new FormData();
  if (params.periodo_dias) {
    formData.append('periodo_dias', params.periodo_dias.toString());
  }

  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/extracao/sync-nfe',
    formData
  );
  return data;
}

/**
 * Sincroniza FGTS rapidamente
 */
export async function sincronizarFGTSRapido(params: {
  periodo_meses?: number;
}): Promise<StandardResponse> {
  const formData = new FormData();
  if (params.periodo_meses) {
    formData.append('periodo_meses', params.periodo_meses.toString());
  }

  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/extracao/sync-fgts',
    formData
  );
  return data;
}

/**
 * Sincroniza todos os serviços rapidamente
 */
export async function sincronizarTodosRapido(): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/extracao/sync-todos',
    {}
  );
  return data;
}

/**
 * Consulta status de extração
 */
export async function consultarStatusExtracao(params: {
  extracao_id: string;
}): Promise<ExtracaoResponse> {
  const { data } = await api.get<ExtracaoResponse>(
    `/api/v1/government/extracao/status/${params.extracao_id}`
  );
  return data;
}

/**
 * Consulta histórico de extrações
 */
export async function consultarHistoricoExtracoes(params?: {
  servico?: string;
  data_inicial?: string;
  data_final?: string;
}): Promise<HistoricoExtracaoResponse[]> {
  const { data } = await api.get<HistoricoExtracaoResponse[]>(
    '/api/v1/government/extracao/historico',
    { params }
  );
  return data;
}

/**
 * Agenda sincronização automática
 */
export async function agendarSincronizacao(
  params: AgendamentoSyncParams
): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sync/agendar',
    {
      servico: params.servico,
      periodicidade: params.periodicidade,
      horario: params.horario,
      ativo: params.ativo,
    }
  );
  return data;
}

/**
 * Lista agendamentos de sincronização
 */
export async function listarAgendamentos(): Promise<AgendamentoSync[]> {
  const { data } = await api.get<AgendamentoSync[]>(
    '/api/v1/government/sync/agendamentos'
  );
  return data;
}

/**
 * Executa sincronização em background
 */
export async function executarSyncBackground(params: {
  servico: string;
}): Promise<StandardResponse> {
  const { data } = await api.post<StandardResponse>(
    '/api/v1/government/sync/servico/background',
    params
  );
  return data;
}

/**
 * Upload de certificado digital
 */
export async function uploadCertificado(
  params: UploadCertificadoParams
): Promise<CertificateUploadResponse> {
  const formData = new FormData();
  formData.append('file', params.arquivo);
  formData.append('password', params.senha);
  if (params.nome) formData.append('nome', params.nome);
  if (params.validade) formData.append('validade', params.validade);

  const { data } = await api.post<CertificateUploadResponse>(
    '/api/v1/government/certificates/upload',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );
  return data;
}

/**
 * Valida certificado digital
 */
export async function validarCertificado(params: {
  arquivo: File;
  senha: string;
}): Promise<CertificateValidationResponse> {
  const formData = new FormData();
  formData.append('file', params.arquivo);
  formData.append('password', params.senha);

  const { data } = await api.post<CertificateValidationResponse>(
    '/api/v1/government/certificates/validate',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );
  return data;
}

/**
 * Lista certificados digitais
 */
export async function listarCertificados(): Promise<CertificateListResponse> {
  const { data } = await api.get<CertificateListResponse>(
    '/api/v1/government/certificates/'
  );
  return data;
}

/**
 * Obtém informações de certificado específico
 */
export async function obterInfoCertificado(params: {
  certificate_id: string;
}): Promise<CertificateInfoResponse> {
  const { data } = await api.get<CertificateInfoResponse>(
    `/api/v1/government/certificates/${params.certificate_id}`
  );
  return data;
}

/**
 * Remove certificado digital
 */
export async function removerCertificado(params: {
  certificate_id: string;
}): Promise<CertificateDeleteResponse> {
  const { data } = await api.delete<CertificateDeleteResponse>(
    `/api/v1/government/certificates/${params.certificate_id}`
  );
  return data;
}

/**
 * Testa assinatura com certificado
 */
export async function testarAssinaturaCertificado(params: {
  certificate_id: string;
  texto: string;
}): Promise<StandardResponse> {
  const formData = new FormData();
  formData.append('text', params.texto);

  const { data } = await api.post<StandardResponse>(
    `/api/v1/government/certificates/${params.certificate_id}/test-sign`,
    formData
  );
  return data;
}

/**
 * Lista alertas de certificados próximos ao vencimento
 */
export async function listarAlertasCertificados(): Promise<AlertaCertificado[]> {
  const { data } = await api.get<AlertaCertificado[]>(
    '/api/v1/government/certificates/alertas'
  );
  return data;
}

/**
 * Lista jobs de sincronização disponíveis
 */
export async function listarJobs(): Promise<JobListResponse> {
  const { data } = await api.get<JobListResponse>('/api/v1/government/jobs/');
  return data;
}

/**
 * Executa job agora
 */
export async function executarJobAgora(params: {
  tipo: string;
}): Promise<JobExecResponse> {
  const { data } = await api.post<JobExecResponse>(
    `/api/v1/government/jobs/${params.tipo}/executar`
  );
  return data;
}

/**
 * Consulta histórico de execuções de job
 */
export async function consultarHistoricoJob(params: {
  tipo: string;
}): Promise<JobExecResponse[]> {
  const { data } = await api.get<JobExecResponse[]>(
    `/api/v1/government/jobs/${params.tipo}/historico`
  );
  return data;
}

/**
 * Obtém dashboard de monitoramento
 */
export async function obterDashboardMonitoramento(): Promise<DashboardResponse> {
  const { data } = await api.get<DashboardResponse>(
    '/api/v1/government/dashboard/monitoramento'
  );
  return data;
}

/**
 * Lista eventos recentes
 */
export async function listarEventosRecentes(params?: {
  limite?: number;
}): Promise<EventoRecente[]> {
  const { data } = await api.get<EventoRecente[]>(
    '/api/v1/government/dashboard/eventos-recentes',
    { params }
  );
  return data;
}

/**
 * Health check do módulo
 */
export async function healthCheck(): Promise<{ status: string }> {
  const { data } = await api.get<{ status: string }>(
    '/api/v1/government/health'
  );
  return data;
}

const syncCertificatesService = {
  iniciarExtracao,
  sincronizarNFeRapido,
  sincronizarFGTSRapido,
  sincronizarTodosRapido,
  consultarStatusExtracao,
  consultarHistoricoExtracoes,
  agendarSincronizacao,
  listarAgendamentos,
  executarSyncBackground,
  uploadCertificado,
  validarCertificado,
  listarCertificados,
  obterInfoCertificado,
  removerCertificado,
  testarAssinaturaCertificado,
  listarAlertasCertificados,
  listarJobs,
  executarJobAgora,
  consultarHistoricoJob,
  obterDashboardMonitoramento,
  listarEventosRecentes,
  healthCheck,
};

export default syncCertificatesService;
