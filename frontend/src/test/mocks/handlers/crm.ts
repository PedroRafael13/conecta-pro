/**
 * MSW Handlers para mock de APIs de CRM (Leads, Oportunidades, Propostas)
 */

import { http, HttpResponse } from 'msw';
import {
  mockLeads,
  mockLead,
  mockOportunidades,
  mockOportunidade,
  mockPropostas,
  mockProposta,
} from '../../fixtures/crm';

const API_BASE_URL = 'http://localhost:8080/api/v1';

// Stores para entidades criadas dinamicamente durante os testes
const dynamicLeads: Map<string, typeof mockLead> = new Map();
const dynamicOportunidades: Map<string, typeof mockOportunidade> = new Map();
const dynamicPropostas: Map<string, typeof mockProposta> = new Map();

export const crmHandlers = [
  // ========== LEADS ==========

  // GET /crm/leads - Listar leads
  http.get(`${API_BASE_URL}/crm/leads`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const prioridade = url.searchParams.get('prioridade');
    const origem = url.searchParams.get('origem');
    const search = url.searchParams.get('search');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockLeads];

    if (status) {
      filtered = filtered.filter((l) => l.status === status);
    }

    if (prioridade) {
      filtered = filtered.filter((l) => l.prioridade === prioridade);
    }

    if (origem) {
      filtered = filtered.filter((l) => l.origem === origem);
    }

    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(
        (l) =>
          l.nome.toLowerCase().includes(searchLower) ||
          l.email.toLowerCase().includes(searchLower) ||
          (l.empresa && l.empresa.toLowerCase().includes(searchLower))
      );
    }

    const total = filtered.length;
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedData = filtered.slice(startIndex, endIndex);

    return HttpResponse.json(
      {
        data: paginatedData,
        total,
        page,
        limit,
        total_pages: Math.ceil(total / limit),
      },
      { status: 200 }
    );
  }),

  // GET /crm/leads/:id - Obter lead específico
  http.get(`${API_BASE_URL}/crm/leads/:id`, ({ params }) => {
    const { id } = params;
    const lead = mockLeads.find((l) => l.id === id);

    // Verifica na store dinâmica se não encontrar nos mocks fixos
    if (!lead) {
      const dynamicLead = dynamicLeads.get(id as string);
      if (dynamicLead) {
        return HttpResponse.json(dynamicLead, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Lead não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(lead, { status: 200 });
  }),

  // POST /crm/leads - Criar lead
  http.post(`${API_BASE_URL}/crm/leads`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.nome || !body.email) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Nome e email são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newLead = {
      ...mockLead,
      ...body,
      id: `lead-${Date.now()}`,
      data_criacao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      status: 'novo',
    };

    // Armazena na store dinâmica
    dynamicLeads.set(newLead.id, newLead as typeof mockLead);

    return HttpResponse.json(newLead, { status: 201 });
  }),

  // PUT /crm/leads/:id - Atualizar lead
  http.put(`${API_BASE_URL}/crm/leads/:id`, async ({ params, request }) => {
    const { id } = params;
    const lead = mockLeads.find((l) => l.id === id);

    if (!lead) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Lead não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const body = await request.json() as Record<string, unknown>;
    const updated = {
      ...lead,
      ...body,
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /crm/leads/:id - Deletar lead
  http.delete(`${API_BASE_URL}/crm/leads/:id`, ({ params }) => {
    const { id } = params;
    const lead = mockLeads.find((l) => l.id === id);

    if (!lead) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Lead não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return new HttpResponse(null, { status: 204 });
  }),

  // POST /crm/leads/:id/qualificar - Qualificar lead
  http.post(`${API_BASE_URL}/crm/leads/:id/qualificar`, ({ params }) => {
    const { id } = params;
    const lead = mockLeads.find((l) => l.id === id);
    const dynamicLead = dynamicLeads.get(id as string);

    // Se não encontrar nos mocks fixos, atualiza na store dinâmica
    if (!lead) {
      const baseLead = dynamicLead || mockLead;
      const updated = {
        ...baseLead,
        id: id as string,
        status: 'qualificado',
        updated_at: new Date().toISOString(),
      };
      dynamicLeads.set(id as string, updated as typeof mockLead);
      return HttpResponse.json(updated, { status: 200 });
    }

    const updated = {
      ...lead,
      status: 'qualificado',
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /crm/leads/:id/convert - Converter lead para oportunidade
  http.post(`${API_BASE_URL}/crm/leads/:id/convert`, async ({ params, request }) => {
    const { id } = params;
    const lead = mockLeads.find((l) => l.id === id);
    const dynamicLead = dynamicLeads.get(id as string);

    let body: { valor_estimado?: number } = {};
    try {
      body = await request.json() as { valor_estimado?: number };
    } catch {
      // Body pode estar vazio
    }

    // Usa lead dinâmico, mock ou mockLead como base
    const baseLead = lead || dynamicLead || mockLead;

    const updated = {
      ...baseLead,
      id: id as string,
      status: 'convertido',
      data_conversao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      valor_estimado: body.valor_estimado || baseLead.valor_estimado,
    };

    // Atualiza na store
    dynamicLeads.set(id as string, updated as typeof mockLead);

    // Simula criação de oportunidade
    const oportunidade = {
      ...mockOportunidade,
      id: `oportunidade-${Date.now()}`,
      titulo: `Oportunidade - ${baseLead.nome}`,
      cliente_nome: baseLead.empresa || baseLead.nome,
      valor_estimado: body.valor_estimado || 0,
      data_criacao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Armazena oportunidade na store dinâmica
    dynamicOportunidades.set(oportunidade.id, oportunidade as typeof mockOportunidade);

    return HttpResponse.json(
      { lead: updated, oportunidade },
      { status: 200 }
    );
  }),

  // ========== OPORTUNIDADES ==========

  // GET /crm/oportunidades - Listar oportunidades
  http.get(`${API_BASE_URL}/crm/oportunidades`, ({ request }) => {
    const url = new URL(request.url);
    const etapa = url.searchParams.get('etapa');
    const cliente_id = url.searchParams.get('cliente_id');
    const responsavel_id = url.searchParams.get('responsavel_id');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockOportunidades];

    if (etapa) {
      filtered = filtered.filter((o) => o.etapa === etapa);
    }

    if (cliente_id) {
      filtered = filtered.filter((o) => o.cliente_id === cliente_id);
    }

    if (responsavel_id) {
      filtered = filtered.filter((o) => o.responsavel_id === responsavel_id);
    }

    const total = filtered.length;
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedData = filtered.slice(startIndex, endIndex);

    return HttpResponse.json(
      {
        data: paginatedData,
        total,
        page,
        limit,
        total_pages: Math.ceil(total / limit),
      },
      { status: 200 }
    );
  }),

  // GET /crm/oportunidades/:id - Obter oportunidade específica
  http.get(`${API_BASE_URL}/crm/oportunidades/:id`, ({ params }) => {
    const { id } = params;
    const oportunidade = mockOportunidades.find((o) => o.id === id);

    if (!oportunidade) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Oportunidade não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(oportunidade, { status: 200 });
  }),

  // POST /crm/oportunidades - Criar oportunidade
  http.post(`${API_BASE_URL}/crm/oportunidades`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.titulo || !body.cliente_id) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Título e cliente são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newOportunidade = {
      ...mockOportunidade,
      ...body,
      id: `oportunidade-${Date.now()}`,
      data_criacao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(newOportunidade, { status: 201 });
  }),

  // PUT /crm/oportunidades/:id - Atualizar oportunidade
  http.put(`${API_BASE_URL}/crm/oportunidades/:id`, async ({ params, request }) => {
    const { id } = params;
    const oportunidade = mockOportunidades.find((o) => o.id === id);

    if (!oportunidade) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Oportunidade não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const body = await request.json() as Record<string, unknown>;
    const updated = {
      ...oportunidade,
      ...body,
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /crm/oportunidades/:id/avancar - Avançar etapa da oportunidade
  http.post(`${API_BASE_URL}/crm/oportunidades/:id/avancar`, ({ params }) => {
    const { id } = params;
    const oportunidade = mockOportunidades.find((o) => o.id === id);

    if (!oportunidade) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Oportunidade não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const etapas = ['prospeccao', 'qualificacao', 'proposta', 'negociacao', 'fechamento'];
    const etapaAtual = oportunidade.etapa;
    const indiceAtual = etapas.indexOf(etapaAtual);
    const proximaEtapa = indiceAtual < etapas.length - 1 ? etapas[indiceAtual + 1] : etapaAtual;

    const updated = {
      ...oportunidade,
      etapa: proximaEtapa,
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /crm/oportunidades/:id/ganhar - Marcar oportunidade como ganha
  http.post(`${API_BASE_URL}/crm/oportunidades/:id/ganhar`, async ({ params, request }) => {
    const { id } = params;
    const oportunidade = mockOportunidades.find((o) => o.id === id);

    if (!oportunidade) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Oportunidade não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    let valor_final = oportunidade.valor_estimado;
    try {
      const body = await request.json() as { valor_final?: number };
      valor_final = body.valor_final || oportunidade.valor_estimado;
    } catch {
      // Body vazio ou inválido, usa valor estimado
    }

    const updated = {
      ...oportunidade,
      etapa: 'fechamento',
      probabilidade: 100,
      valor_final,
      data_fechamento: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /crm/oportunidades/:id/perder - Marcar oportunidade como perdida
  http.post(`${API_BASE_URL}/crm/oportunidades/:id/perder`, async ({ params, request }) => {
    const { id } = params;
    const oportunidade = mockOportunidades.find((o) => o.id === id);

    if (!oportunidade) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Oportunidade não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    let motivo = 'Motivo não especificado';
    try {
      const body = await request.json() as { motivo?: string };
      motivo = body.motivo || motivo;
    } catch {
      // Body vazio ou inválido
    }

    const updated = {
      ...oportunidade,
      etapa: 'perdido',
      probabilidade: 0,
      motivo_perda: motivo,
      data_fechamento: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // ========== PROPOSTAS ==========

  // GET /crm/propostas - Listar propostas
  http.get(`${API_BASE_URL}/crm/propostas`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const oportunidade_id = url.searchParams.get('oportunidade_id');
    const cliente_id = url.searchParams.get('cliente_id');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockPropostas];

    if (status) {
      filtered = filtered.filter((p) => p.status === status);
    }

    if (oportunidade_id) {
      filtered = filtered.filter((p) => p.oportunidade_id === oportunidade_id);
    }

    if (cliente_id) {
      filtered = filtered.filter((p) => p.cliente_id === cliente_id);
    }

    const total = filtered.length;
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedData = filtered.slice(startIndex, endIndex);

    return HttpResponse.json(
      {
        data: paginatedData,
        total,
        page,
        limit,
        total_pages: Math.ceil(total / limit),
      },
      { status: 200 }
    );
  }),

  // GET /crm/propostas/:id - Obter proposta específica
  http.get(`${API_BASE_URL}/crm/propostas/:id`, ({ params }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);

    if (!proposta) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Proposta não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(proposta, { status: 200 });
  }),

  // POST /crm/propostas - Criar proposta
  http.post(`${API_BASE_URL}/crm/propostas`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.oportunidade_id || !body.itens) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Oportunidade e itens são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newProposta = {
      ...mockProposta,
      ...body,
      id: `proposta-${Date.now()}`,
      numero: `PROP-2026-${String(mockPropostas.length + 1).padStart(3, '0')}`,
      status: 'rascunho',
      data_emissao: new Date().toISOString(),
      data_criacao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Armazena na store dinâmica
    dynamicPropostas.set(newProposta.id, newProposta as typeof mockProposta);

    return HttpResponse.json(newProposta, { status: 201 });
  }),

  // PUT /crm/propostas/:id - Atualizar proposta
  http.put(`${API_BASE_URL}/crm/propostas/:id`, async ({ params, request }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);

    if (!proposta) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Proposta não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const body = await request.json() as Record<string, unknown>;
    const updated = {
      ...proposta,
      ...body,
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /crm/propostas/:id/enviar - Enviar proposta
  http.post(`${API_BASE_URL}/crm/propostas/:id/enviar`, ({ params }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);
    const dynamicProposta = dynamicPropostas.get(id as string);

    // Se não encontrar nos mocks fixos, atualiza na store dinâmica
    if (!proposta) {
      const baseProposta = dynamicProposta || mockProposta;
      const updated = {
        ...baseProposta,
        id: id as string,
        status: 'enviada',
        updated_at: new Date().toISOString(),
      };
      dynamicPropostas.set(id as string, updated as typeof mockProposta);
      return HttpResponse.json(updated, { status: 200 });
    }

    const updated = {
      ...proposta,
      status: 'enviada',
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /crm/propostas/:id/aprovar - Aprovar proposta
  http.post(`${API_BASE_URL}/crm/propostas/:id/aprovar`, ({ params }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);
    const dynamicProposta = dynamicPropostas.get(id as string);

    // Se não encontrar nos mocks fixos, atualiza na store dinâmica
    if (!proposta) {
      const baseProposta = dynamicProposta || mockProposta;
      const updated = {
        ...baseProposta,
        id: id as string,
        status: 'aprovada',
        data_aprovacao: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      dynamicPropostas.set(id as string, updated as typeof mockProposta);
      return HttpResponse.json(updated, { status: 200 });
    }

    const updated = {
      ...proposta,
      status: 'aprovada',
      data_aprovacao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /crm/propostas/:id/rejeitar - Rejeitar proposta
  http.post(`${API_BASE_URL}/crm/propostas/:id/rejeitar`, async ({ params, request }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);

    if (!proposta) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Proposta não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    let motivo = 'Motivo não especificado';
    try {
      const body = await request.json() as { motivo?: string };
      motivo = body.motivo || motivo;
    } catch {
      // Body vazio ou inválido
    }

    const updated = {
      ...proposta,
      status: 'rejeitada',
      data_rejeicao: new Date().toISOString(),
      motivo_rejeicao: motivo,
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /crm/propostas/:id - Deletar proposta
  http.delete(`${API_BASE_URL}/crm/propostas/:id`, ({ params }) => {
    const { id } = params;
    const proposta = mockPropostas.find((p) => p.id === id);

    if (!proposta) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Proposta não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return new HttpResponse(null, { status: 204 });
  }),

  // ========== DASHBOARD/STATS ==========

  // GET /crm/stats - Estatísticas do CRM
  http.get(`${API_BASE_URL}/crm/stats`, () => {
    const stats = {
      leads: {
        total: mockLeads.length,
        novos: mockLeads.filter((l) => l.status === 'novo').length,
        em_contato: mockLeads.filter((l) => l.status === 'em_contato').length,
        qualificados: mockLeads.filter((l) => l.status === 'qualificado').length,
        convertidos: mockLeads.filter((l) => l.status === 'convertido').length,
      },
      oportunidades: {
        total: mockOportunidades.length,
        em_andamento: mockOportunidades.filter(
          (o) => !['fechamento', 'perdido'].includes(o.etapa)
        ).length,
        ganhas: mockOportunidades.filter((o) => o.etapa === 'fechamento' && o.probabilidade === 100).length,
        perdidas: mockOportunidades.filter((o) => o.etapa === 'perdido').length,
        valor_pipeline: mockOportunidades
          .filter((o) => !['fechamento', 'perdido'].includes(o.etapa))
          .reduce((acc, o) => acc + (o.valor_estimado || 0), 0),
      },
      propostas: {
        total: mockPropostas.length,
        rascunho: mockPropostas.filter((p) => p.status === 'rascunho').length,
        enviadas: mockPropostas.filter((p) => p.status === 'enviada' || p.status === 'em_analise').length,
        aprovadas: mockPropostas.filter((p) => p.status === 'aprovada').length,
        rejeitadas: mockPropostas.filter((p) => p.status === 'rejeitada').length,
        valor_total: mockPropostas
          .filter((p) => p.status === 'aprovada')
          .reduce((acc, p) => acc + p.valor_final, 0),
      },
    };

    return HttpResponse.json(stats, { status: 200 });
  }),
];
