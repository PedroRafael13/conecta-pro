/**
 * MSW Handlers para mock de APIs do módulo Licitações
 */

import { http, HttpResponse } from 'msw';
import {
  mockEditais,
  mockEdital,
  mockPropostas,
  mockProposta,
  mockContratos,
  mockContrato,
  mockCertidoes,
  mockCertidao,
  mockDocumentos,
  mockDocumento,
} from '../fixtures/licitacoes';

const API_BASE_URL = 'http://localhost:8080/api/v1';

export const licitacoesHandlers = [
  // ========== EDITAIS ==========

  // GET /editais - Listar editais
  http.get(`${API_BASE_URL}/licitacoes/editais`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const modalidade = url.searchParams.get('modalidade');

    let filtered = [...mockEditais];

    if (status) {
      filtered = filtered.filter((e) => e.status === status);
    }

    if (modalidade) {
      filtered = filtered.filter((e) => e.modalidade === modalidade);
    }

    return HttpResponse.json(filtered);
  }),

  // GET /editais/:id - Obter edital específico
  http.get(`${API_BASE_URL}/licitacoes/editais/:id`, ({ params }) => {
    const { id } = params;
    const edital = mockEditais.find((e) => e.id === id);

    if (!edital) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json(edital);
  }),

  // POST /editais - Criar edital
  http.post(`${API_BASE_URL}/licitacoes/editais`, async ({ request }) => {
    const body = await request.json();
    const newEdital = {
      ...mockEdital,
      ...(body as Record<string, unknown>),
      id: `edital-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(newEdital, { status: 201 });
  }),

  // PUT /editais/:id - Atualizar edital
  http.put(`${API_BASE_URL}/licitacoes/editais/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json();
    const edital = mockEditais.find((e) => e.id === id);

    if (!edital) {
      return new HttpResponse(null, { status: 404 });
    }

    const updated = {
      ...edital,
      ...(body as Record<string, unknown>),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated);
  }),

  // DELETE /editais/:id - Deletar edital
  http.delete(`${API_BASE_URL}/licitacoes/editais/:id`, ({ params }) => {
    const { id } = params;
    const edital = mockEditais.find((e) => e.id === id);

    if (!edital) {
      return new HttpResponse(null, { status: 404 });
    }

    return new HttpResponse(null, { status: 204 });
  }),

  // ========== PROPOSTAS ==========

  // GET /propostas - Listar propostas
  http.get(`${API_BASE_URL}/licitacoes/propostas`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');

    let filtered = [...mockPropostas];

    if (status) {
      filtered = filtered.filter((p) => p.status === status);
    }

    return HttpResponse.json(filtered);
  }),

  // GET /propostas/:id - Obter proposta específica
  http.get(`${API_BASE_URL}/licitacoes/propostas/:id`, ({ params }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);

    if (!proposta) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json(proposta);
  }),

  // POST /propostas - Criar proposta
  http.post(`${API_BASE_URL}/licitacoes/propostas`, async ({ request }) => {
    const body = await request.json();
    const newProposta = {
      ...mockProposta,
      ...(body as Record<string, unknown>),
      id: `proposta-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(newProposta, { status: 201 });
  }),

  // PUT /propostas/:id - Atualizar proposta
  http.put(`${API_BASE_URL}/licitacoes/propostas/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json();
    const proposta = mockPropostas.find((p) => p.id === id);

    if (!proposta) {
      return new HttpResponse(null, { status: 404 });
    }

    const updated = {
      ...proposta,
      ...(body as Record<string, unknown>),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated);
  }),

  // POST /propostas/:id/submit - Submeter proposta
  http.post(`${API_BASE_URL}/licitacoes/propostas/:id/submit`, ({ params }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);

    if (!proposta) {
      return new HttpResponse(null, { status: 404 });
    }

    const submitted = {
      ...proposta,
      status: 'em_analise',
      data_envio: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(submitted);
  }),

  // DELETE /propostas/:id - Deletar proposta
  http.delete(`${API_BASE_URL}/licitacoes/propostas/:id`, ({ params }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);

    if (!proposta) {
      return new HttpResponse(null, { status: 404 });
    }

    return new HttpResponse(null, { status: 204 });
  }),

  // ========== CONTRATOS ==========

  // GET /contratos - Listar contratos
  http.get(`${API_BASE_URL}/licitacoes/contratos`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');

    let filtered = [...mockContratos];

    if (status) {
      filtered = filtered.filter((c) => c.status === status);
    }

    return HttpResponse.json(filtered);
  }),

  // GET /contratos/:id - Obter contrato específico
  http.get(`${API_BASE_URL}/licitacoes/contratos/:id`, ({ params }) => {
    const { id } = params;
    const contrato = mockContratos.find((c) => c.id === id);

    if (!contrato) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json(contrato);
  }),

  // ========== CERTIDÕES ==========

  // GET /certidoes - Listar certidões
  http.get(`${API_BASE_URL}/licitacoes/certidoes`, ({ request }) => {
    const url = new URL(request.url);
    const tipo = url.searchParams.get('tipo');
    const status = url.searchParams.get('status');

    let filtered = [...mockCertidoes];

    if (tipo) {
      filtered = filtered.filter((c) => c.tipo === tipo);
    }

    if (status) {
      filtered = filtered.filter((c) => c.status === status);
    }

    return HttpResponse.json(filtered);
  }),

  // POST /certidoes - Upload certidão
  http.post(`${API_BASE_URL}/licitacoes/certidoes`, async ({ request }) => {
    const body = await request.json();
    const newCertidao = {
      ...mockCertidao,
      ...(body as Record<string, unknown>),
      id: `certidao-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(newCertidao, { status: 201 });
  }),

  // POST /certidoes/:id/renovar - Renovar certidão
  http.post(`${API_BASE_URL}/licitacoes/certidoes/:id/renovar`, ({ params }) => {
    const { id } = params;
    const certidao = mockCertidoes.find((c) => c.id === id);

    if (!certidao) {
      return new HttpResponse(null, { status: 404 });
    }

    const renovada = {
      ...certidao,
      data_emissao: new Date().toISOString(),
      data_validade: new Date(
        Date.now() + 180 * 24 * 60 * 60 * 1000
      ).toISOString(),
      status: 'valida',
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(renovada);
  }),

  // DELETE /certidoes/:id - Deletar certidão
  http.delete(`${API_BASE_URL}/licitacoes/certidoes/:id`, ({ params }) => {
    const { id } = params;
    const certidao = mockCertidoes.find((c) => c.id === id);

    if (!certidao) {
      return new HttpResponse(null, { status: 404 });
    }

    return new HttpResponse(null, { status: 204 });
  }),

  // ========== DOCUMENTOS ==========

  // GET /documentos - Listar documentos
  http.get(`${API_BASE_URL}/licitacoes/documentos`, ({ request }) => {
    const url = new URL(request.url);
    const tipo = url.searchParams.get('tipo');

    let filtered = [...mockDocumentos];

    if (tipo) {
      filtered = filtered.filter((d) => d.tipo === tipo);
    }

    return HttpResponse.json(filtered);
  }),

  // POST /documentos - Upload documento
  http.post(`${API_BASE_URL}/licitacoes/documentos`, async ({ request }) => {
    const body = await request.json();
    const newDocumento = {
      ...mockDocumento,
      ...(body as Record<string, unknown>),
      id: `doc-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(newDocumento, { status: 201 });
  }),

  // DELETE /documentos/:id - Deletar documento
  http.delete(`${API_BASE_URL}/licitacoes/documentos/:id`, ({ params }) => {
    const { id } = params;
    const documento = mockDocumentos.find((d) => d.id === id);

    if (!documento) {
      return new HttpResponse(null, { status: 404 });
    }

    return new HttpResponse(null, { status: 204 });
  }),

  // ========== STATS/DASHBOARD ==========

  // GET /stats - Estatísticas do dashboard
  http.get(`${API_BASE_URL}/licitacoes/stats`, () => {
    return HttpResponse.json({
      editais_ativos: 5,
      propostas_em_analise: 3,
      contratos_vigentes: 12,
      certidoes_validas: 8,
    });
  }),
];

export const handlers = [...licitacoesHandlers];
