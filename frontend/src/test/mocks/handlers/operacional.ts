/**
 * MSW Handlers para mock de APIs do módulo Operacional
 */

import { http, HttpResponse } from 'msw';
import {
  mockPosts,
  mockPost,
  mockScales,
  mockScale,
  mockOccurrences,
  mockOccurrence,
  mockEmployees,
  mockEmployee,
  mockDiarists,
  mockDiarist,
} from '../../fixtures/operacional';

const API_BASE_URL = 'http://localhost:8080/api/v1';

// Stores para entidades criadas dinamicamente durante os testes
const dynamicPosts: Map<string, typeof mockPost> = new Map();
const dynamicScales: Map<string, typeof mockScale> = new Map();
const dynamicOccurrences: Map<string, typeof mockOccurrence> = new Map();
const dynamicEmployees: Map<string, typeof mockEmployee> = new Map();
const dynamicDiarists: Map<string, typeof mockDiarist> = new Map();

export const operacionalHandlers = [
  // ========== POSTOS ==========

  // GET /operacional/posts - Listar postos
  http.get(`${API_BASE_URL}/operacional/posts`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const cliente_id = url.searchParams.get('cliente_id');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockPosts, ...Array.from(dynamicPosts.values())];

    if (status) {
      filtered = filtered.filter((p) => p.status === status);
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

  // GET /operacional/posts/:id - Obter posto específico
  http.get(`${API_BASE_URL}/operacional/posts/:id`, ({ params }) => {
    const { id } = params;
    const post = mockPosts.find((p) => p.id === id);

    if (!post) {
      const dynamicPost = dynamicPosts.get(id as string);
      if (dynamicPost) {
        return HttpResponse.json(dynamicPost, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Posto não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(post, { status: 200 });
  }),

  // POST /operacional/posts - Criar posto
  http.post(`${API_BASE_URL}/operacional/posts`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.nome || !body.cliente_id) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Nome e cliente são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newPost = {
      ...mockPost,
      ...body,
      id: `posto-${Date.now()}`,
      data_criacao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    dynamicPosts.set(newPost.id, newPost as typeof mockPost);

    return HttpResponse.json(newPost, { status: 201 });
  }),

  // PATCH /operacional/posts/:id - Atualizar posto
  http.patch(`${API_BASE_URL}/operacional/posts/:id`, async ({ params, request }) => {
    const { id } = params;
    const post = mockPosts.find((p) => p.id === id);
    const dynamicPost = dynamicPosts.get(id as string);

    if (!post && !dynamicPost) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Posto não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const body = await request.json() as Record<string, unknown>;
    const updated = {
      ...(dynamicPost || post || mockPost),
      ...body,
      id: id as string,
      updated_at: new Date().toISOString(),
    };

    dynamicPosts.set(id as string, updated as typeof mockPost);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /operacional/posts/:id - Deletar posto
  http.delete(`${API_BASE_URL}/operacional/posts/:id`, ({ params }) => {
    const { id } = params;
    dynamicPosts.delete(id as string);
    return new HttpResponse(null, { status: 204 });
  }),

  // GET /operacional/posts/stats - Estatísticas de postos
  http.get(`${API_BASE_URL}/operacional/posts/stats`, () => {
    const stats = {
      total: mockPosts.length + dynamicPosts.size,
      ativos: mockPosts.filter((p) => p.status === 'ativo').length,
      inativos: mockPosts.filter((p) => p.status === 'inativo').length,
      manutencao: mockPosts.filter((p) => p.status === 'manutencao').length,
    };

    return HttpResponse.json(stats, { status: 200 });
  }),

  // ========== ESCALAS ==========

  // GET /operacional/scales - Listar escalas
  http.get(`${API_BASE_URL}/operacional/scales`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const posto_id = url.searchParams.get('posto_id');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockScales, ...Array.from(dynamicScales.values())];

    if (status) {
      filtered = filtered.filter((s) => s.status === status);
    }

    if (posto_id) {
      filtered = filtered.filter((s) => s.posto_id === posto_id);
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

  // GET /operacional/scales/:id - Obter escala específica
  http.get(`${API_BASE_URL}/operacional/scales/:id`, ({ params }) => {
    const { id } = params;
    const scale = mockScales.find((s) => s.id === id);

    if (!scale) {
      const dynamicScale = dynamicScales.get(id as string);
      if (dynamicScale) {
        return HttpResponse.json(dynamicScale, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Escala não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(scale, { status: 200 });
  }),

  // POST /operacional/scales - Criar escala
  http.post(`${API_BASE_URL}/operacional/scales`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    const newScale = {
      ...mockScale,
      ...body,
      id: `escala-${Date.now()}`,
      data_criacao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    dynamicScales.set(newScale.id, newScale as typeof mockScale);

    return HttpResponse.json(newScale, { status: 201 });
  }),

  // PATCH /operacional/scales/:id - Atualizar escala
  http.patch(`${API_BASE_URL}/operacional/scales/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json() as Record<string, unknown>;

    const scale = mockScales.find((s) => s.id === id);
    const dynamicScale = dynamicScales.get(id as string);

    const updated = {
      ...(dynamicScale || scale || mockScale),
      ...body,
      id: id as string,
      updated_at: new Date().toISOString(),
    };

    dynamicScales.set(id as string, updated as typeof mockScale);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /operacional/scales/:id/publish - Publicar escala
  http.post(`${API_BASE_URL}/operacional/scales/:id/publish`, ({ params }) => {
    const { id } = params;
    const scale = mockScales.find((s) => s.id === id);
    const dynamicScale = dynamicScales.get(id as string);

    const updated = {
      ...(dynamicScale || scale || mockScale),
      id: id as string,
      status: 'publicada',
      publicada_em: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    dynamicScales.set(id as string, updated as typeof mockScale);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /operacional/scales/:id - Deletar escala
  http.delete(`${API_BASE_URL}/operacional/scales/:id`, ({ params }) => {
    const { id } = params;
    dynamicScales.delete(id as string);
    return new HttpResponse(null, { status: 204 });
  }),

  // GET /operacional/scales/stats - Estatísticas de escalas
  http.get(`${API_BASE_URL}/operacional/scales/stats`, () => {
    const stats = {
      total: mockScales.length + dynamicScales.size,
      rascunho: mockScales.filter((s) => s.status === 'rascunho').length,
      publicada: mockScales.filter((s) => s.status === 'publicada').length,
      em_execucao: mockScales.filter((s) => s.status === 'em_execucao').length,
      concluida: mockScales.filter((s) => s.status === 'concluida').length,
    };

    return HttpResponse.json(stats, { status: 200 });
  }),

  // ========== OCORRÊNCIAS ==========

  // GET /operacional/occurrences - Listar ocorrências
  http.get(`${API_BASE_URL}/operacional/occurrences`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const tipo = url.searchParams.get('tipo');
    const severidade = url.searchParams.get('severidade');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockOccurrences, ...Array.from(dynamicOccurrences.values())];

    if (status) {
      filtered = filtered.filter((o) => o.status === status);
    }

    if (tipo) {
      filtered = filtered.filter((o) => o.tipo === tipo);
    }

    if (severidade) {
      filtered = filtered.filter((o) => o.severidade === severidade);
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

  // GET /operacional/occurrences/:id - Obter ocorrência específica
  http.get(`${API_BASE_URL}/operacional/occurrences/:id`, ({ params }) => {
    const { id } = params;
    const occurrence = mockOccurrences.find((o) => o.id === id);

    if (!occurrence) {
      const dynamicOccurrence = dynamicOccurrences.get(id as string);
      if (dynamicOccurrence) {
        return HttpResponse.json(dynamicOccurrence, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Ocorrência não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(occurrence, { status: 200 });
  }),

  // POST /operacional/occurrences - Criar ocorrência
  http.post(`${API_BASE_URL}/operacional/occurrences`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.titulo || !body.posto_id) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Título e posto são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newOccurrence = {
      ...mockOccurrence,
      ...body,
      id: `ocorrencia-${Date.now()}`,
      data_registro: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    dynamicOccurrences.set(newOccurrence.id, newOccurrence as typeof mockOccurrence);

    return HttpResponse.json(newOccurrence, { status: 201 });
  }),

  // PATCH /operacional/occurrences/:id - Atualizar ocorrência
  http.patch(`${API_BASE_URL}/operacional/occurrences/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json() as Record<string, unknown>;

    const occurrence = mockOccurrences.find((o) => o.id === id);
    const dynamicOccurrence = dynamicOccurrences.get(id as string);

    const updated = {
      ...(dynamicOccurrence || occurrence || mockOccurrence),
      ...body,
      id: id as string,
      updated_at: new Date().toISOString(),
    };

    dynamicOccurrences.set(id as string, updated as typeof mockOccurrence);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /operacional/occurrences/:id/resolve - Resolver ocorrência
  http.post(`${API_BASE_URL}/operacional/occurrences/:id/resolve`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json() as { acoes_tomadas?: string };

    const occurrence = mockOccurrences.find((o) => o.id === id);
    const dynamicOccurrence = dynamicOccurrences.get(id as string);

    const updated = {
      ...(dynamicOccurrence || occurrence || mockOccurrence),
      id: id as string,
      status: 'resolvida',
      acoes_tomadas: body.acoes_tomadas || 'Resolvido',
      data_resolucao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    dynamicOccurrences.set(id as string, updated as typeof mockOccurrence);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /operacional/occurrences/:id - Deletar ocorrência
  http.delete(`${API_BASE_URL}/operacional/occurrences/:id`, ({ params }) => {
    const { id } = params;
    dynamicOccurrences.delete(id as string);
    return new HttpResponse(null, { status: 204 });
  }),

  // GET /operacional/occurrences/stats - Estatísticas de ocorrências
  http.get(`${API_BASE_URL}/operacional/occurrences/stats`, () => {
    const stats = {
      total: mockOccurrences.length + dynamicOccurrences.size,
      abertas: mockOccurrences.filter((o) => o.status === 'aberta').length,
      em_andamento: mockOccurrences.filter((o) => o.status === 'em_andamento').length,
      resolvidas: mockOccurrences.filter((o) => o.status === 'resolvida').length,
      criticas: mockOccurrences.filter((o) => o.severidade === 'critica').length,
    };

    return HttpResponse.json(stats, { status: 200 });
  }),

  // ========== FUNCIONÁRIOS ==========

  // GET /operacional/employees - Listar funcionários
  http.get(`${API_BASE_URL}/operacional/employees`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const cargo = url.searchParams.get('cargo');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockEmployees, ...Array.from(dynamicEmployees.values())];

    if (status) {
      filtered = filtered.filter((e) => e.status === status);
    }

    if (cargo) {
      filtered = filtered.filter((e) => e.cargo === cargo);
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

  // GET /operacional/employees/:id - Obter funcionário específico
  http.get(`${API_BASE_URL}/operacional/employees/:id`, ({ params }) => {
    const { id } = params;
    const employee = mockEmployees.find((e) => e.id === id);

    if (!employee) {
      const dynamicEmployee = dynamicEmployees.get(id as string);
      if (dynamicEmployee) {
        return HttpResponse.json(dynamicEmployee, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Funcionário não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(employee, { status: 200 });
  }),

  // PATCH /operacional/employees/:id - Atualizar funcionário
  http.patch(`${API_BASE_URL}/operacional/employees/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json() as Record<string, unknown>;

    const employee = mockEmployees.find((e) => e.id === id);
    const dynamicEmployee = dynamicEmployees.get(id as string);

    const updated = {
      ...(dynamicEmployee || employee || mockEmployee),
      ...body,
      id: id as string,
      updated_at: new Date().toISOString(),
    };

    dynamicEmployees.set(id as string, updated as typeof mockEmployee);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // ========== DIARISTAS ==========

  // GET /operacional/diaristas - Listar diaristas
  http.get(`${API_BASE_URL}/operacional/diaristas`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const disponivel = url.searchParams.get('disponivel');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockDiarists, ...Array.from(dynamicDiarists.values())];

    if (status) {
      filtered = filtered.filter((d) => d.status === status);
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

  // GET /operacional/diaristas/:id - Obter diarista específico
  http.get(`${API_BASE_URL}/operacional/diaristas/:id`, ({ params }) => {
    const { id } = params;
    const diarist = mockDiarists.find((d) => d.id === id);

    if (!diarist) {
      const dynamicDiarist = dynamicDiarists.get(id as string);
      if (dynamicDiarist) {
        return HttpResponse.json(dynamicDiarist, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Diarista não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(diarist, { status: 200 });
  }),

  // POST /operacional/diaristas - Criar diarista
  http.post(`${API_BASE_URL}/operacional/diaristas`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.nome || !body.cpf) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Nome e CPF são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newDiarist = {
      ...mockDiarist,
      ...body,
      id: `diarista-${Date.now()}`,
      data_cadastro: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    dynamicDiarists.set(newDiarist.id, newDiarist as typeof mockDiarist);

    return HttpResponse.json(newDiarist, { status: 201 });
  }),

  // PUT /operacional/diaristas/:id - Atualizar diarista
  http.put(`${API_BASE_URL}/operacional/diaristas/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json() as Record<string, unknown>;

    const diarist = mockDiarists.find((d) => d.id === id);
    const dynamicDiarist = dynamicDiarists.get(id as string);

    const updated = {
      ...(dynamicDiarist || diarist || mockDiarist),
      ...body,
      id: id as string,
      updated_at: new Date().toISOString(),
    };

    dynamicDiarists.set(id as string, updated as typeof mockDiarist);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /operacional/diaristas/:id - Deletar diarista
  http.delete(`${API_BASE_URL}/operacional/diaristas/:id`, ({ params }) => {
    const { id } = params;
    dynamicDiarists.delete(id as string);
    return new HttpResponse(null, { status: 204 });
  }),

  // GET /operacional/diaristas/statistics/general - Estatísticas de diaristas
  http.get(`${API_BASE_URL}/operacional/diaristas/statistics/general`, () => {
    const stats = {
      total: mockDiarists.length + dynamicDiarists.size,
      ativos: mockDiarists.filter((d) => d.status === 'ativo').length,
      inativos: mockDiarists.filter((d) => d.status === 'inativo').length,
      bloqueados: mockDiarists.filter((d) => d.status === 'bloqueado').length,
      avaliacao_media: 4.5,
      total_trabalhos: 500,
    };

    return HttpResponse.json(stats, { status: 200 });
  }),
];
