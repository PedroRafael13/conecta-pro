/**
 * MSW Handlers para mock de APIs do módulo Financial
 */

import { http, HttpResponse } from 'msw';
import {
  mockPayables,
  mockPayable,
  mockReceivables,
  mockReceivable,
  mockCashflowEntries,
  mockCashflowEntry,
  mockCashflowProjection,
  mockNFes,
  mockNFe,
} from '../../fixtures/financial';

const API_BASE_URL = 'http://localhost:8080/api/v1';

// Stores para entidades criadas dinamicamente durante os testes
const dynamicPayables: Map<string, typeof mockPayable> = new Map();
const dynamicReceivables: Map<string, typeof mockReceivable> = new Map();
const dynamicCashflowEntries: Map<string, typeof mockCashflowEntry> = new Map();
const dynamicNFes: Map<string, typeof mockNFe> = new Map();

export const financialHandlers = [
  // ========== CONTAS A PAGAR ==========

  // GET /financial/payables - Listar contas a pagar
  http.get(`${API_BASE_URL}/financial/payables`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const categoria = url.searchParams.get('categoria');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockPayables, ...Array.from(dynamicPayables.values())];

    if (status) {
      filtered = filtered.filter((p) => p.status === status);
    }

    if (categoria) {
      filtered = filtered.filter((p) => p.categoria === categoria);
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

  // GET /financial/payables/:id - Obter conta a pagar específica
  http.get(`${API_BASE_URL}/financial/payables/:id`, ({ params }) => {
    const { id } = params;
    const payable = mockPayables.find((p) => p.id === id);

    if (!payable) {
      const dynamicPayable = dynamicPayables.get(id as string);
      if (dynamicPayable) {
        return HttpResponse.json(dynamicPayable, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Conta a pagar não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(payable, { status: 200 });
  }),

  // POST /financial/payables - Criar conta a pagar
  http.post(`${API_BASE_URL}/financial/payables`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.descricao || !body.valor_original) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Descrição e valor são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newPayable = {
      ...mockPayable,
      ...body,
      id: `payable-${Date.now()}`,
      data_emissao: new Date().toISOString(),
      status: 'pendente',
      updated_at: new Date().toISOString(),
    };

    dynamicPayables.set(newPayable.id, newPayable as typeof mockPayable);

    return HttpResponse.json(newPayable, { status: 201 });
  }),

  // PUT /financial/payables/:id - Atualizar conta a pagar
  http.put(`${API_BASE_URL}/financial/payables/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json() as Record<string, unknown>;

    const payable = mockPayables.find((p) => p.id === id);
    const dynamicPayable = dynamicPayables.get(id as string);

    const updated = {
      ...(dynamicPayable || payable || mockPayable),
      ...body,
      id: id as string,
      updated_at: new Date().toISOString(),
    };

    dynamicPayables.set(id as string, updated as typeof mockPayable);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /financial/payables/:id/pay - Registrar pagamento
  http.post(`${API_BASE_URL}/financial/payables/:id/pay`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json() as { valor_pago?: number };

    const payable = mockPayables.find((p) => p.id === id);
    const dynamicPayable = dynamicPayables.get(id as string);

    const base = dynamicPayable || payable || mockPayable;
    const updated = {
      ...base,
      id: id as string,
      status: 'pago',
      valor_pago: body.valor_pago || base.valor_original,
      data_pagamento: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    dynamicPayables.set(id as string, updated as typeof mockPayable);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /financial/payables/:id - Deletar conta a pagar
  http.delete(`${API_BASE_URL}/financial/payables/:id`, ({ params }) => {
    const { id } = params;
    dynamicPayables.delete(id as string);
    return new HttpResponse(null, { status: 204 });
  }),

  // GET /financial/payables/stats - Estatísticas de contas a pagar
  http.get(`${API_BASE_URL}/financial/payables/stats`, () => {
    const allPayables = [...mockPayables, ...Array.from(dynamicPayables.values())];
    const stats = {
      total: allPayables.length,
      pendente: allPayables.filter((p) => p.status === 'pendente').length,
      pago: allPayables.filter((p) => p.status === 'pago').length,
      vencido: allPayables.filter((p) => p.status === 'vencido').length,
      valor_total_pendente: allPayables
        .filter((p) => p.status === 'pendente')
        .reduce((acc, p) => acc + p.valor_original, 0),
      valor_total_pago: allPayables
        .filter((p) => p.status === 'pago')
        .reduce((acc, p) => acc + (p.valor_pago || 0), 0),
    };

    return HttpResponse.json(stats, { status: 200 });
  }),

  // ========== CONTAS A RECEBER ==========

  // GET /financial/receivables - Listar contas a receber
  http.get(`${API_BASE_URL}/financial/receivables`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const cliente_id = url.searchParams.get('cliente_id');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockReceivables, ...Array.from(dynamicReceivables.values())];

    if (status) {
      filtered = filtered.filter((r) => r.status === status);
    }

    if (cliente_id) {
      filtered = filtered.filter((r) => r.cliente_id === cliente_id);
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

  // GET /financial/receivables/:id - Obter conta a receber específica
  http.get(`${API_BASE_URL}/financial/receivables/:id`, ({ params }) => {
    const { id } = params;
    const receivable = mockReceivables.find((r) => r.id === id);

    if (!receivable) {
      const dynamicReceivable = dynamicReceivables.get(id as string);
      if (dynamicReceivable) {
        return HttpResponse.json(dynamicReceivable, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Conta a receber não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(receivable, { status: 200 });
  }),

  // POST /financial/receivables - Criar conta a receber
  http.post(`${API_BASE_URL}/financial/receivables`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.descricao || !body.valor_original || !body.cliente_id) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Descrição, valor e cliente são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newReceivable = {
      ...mockReceivable,
      ...body,
      id: `receivable-${Date.now()}`,
      data_emissao: new Date().toISOString(),
      status: 'pendente',
      updated_at: new Date().toISOString(),
    };

    dynamicReceivables.set(newReceivable.id, newReceivable as typeof mockReceivable);

    return HttpResponse.json(newReceivable, { status: 201 });
  }),

  // PUT /financial/receivables/:id - Atualizar conta a receber
  http.put(`${API_BASE_URL}/financial/receivables/:id`, async ({ params, request }) => {
    const { id } = params;
    const body = await request.json() as Record<string, unknown>;

    const receivable = mockReceivables.find((r) => r.id === id);
    const dynamicReceivable = dynamicReceivables.get(id as string);

    const updated = {
      ...(dynamicReceivable || receivable || mockReceivable),
      ...body,
      id: id as string,
      updated_at: new Date().toISOString(),
    };

    dynamicReceivables.set(id as string, updated as typeof mockReceivable);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // DELETE /financial/receivables/:id - Deletar conta a receber
  http.delete(`${API_BASE_URL}/financial/receivables/:id`, ({ params }) => {
    const { id } = params;
    dynamicReceivables.delete(id as string);
    return new HttpResponse(null, { status: 204 });
  }),

  // GET /financial/receivables/stats - Estatísticas de contas a receber
  http.get(`${API_BASE_URL}/financial/receivables/stats`, () => {
    const allReceivables = [...mockReceivables, ...Array.from(dynamicReceivables.values())];
    const stats = {
      total: allReceivables.length,
      pendente: allReceivables.filter((r) => r.status === 'pendente').length,
      recebido: allReceivables.filter((r) => r.status === 'recebido').length,
      vencido: allReceivables.filter((r) => r.status === 'vencido').length,
      valor_total_pendente: allReceivables
        .filter((r) => r.status === 'pendente')
        .reduce((acc, r) => acc + r.valor_original, 0),
      valor_total_recebido: allReceivables
        .filter((r) => r.status === 'recebido')
        .reduce((acc, r) => acc + (r.valor_recebido || 0), 0),
    };

    return HttpResponse.json(stats, { status: 200 });
  }),

  // ========== FLUXO DE CAIXA ==========

  // GET /financial/cashflow/entries - Listar entradas de fluxo de caixa
  http.get(`${API_BASE_URL}/financial/cashflow/entries`, ({ request }) => {
    const url = new URL(request.url);
    const tipo = url.searchParams.get('tipo');
    const data_inicio = url.searchParams.get('data_inicio');
    const data_fim = url.searchParams.get('data_fim');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockCashflowEntries, ...Array.from(dynamicCashflowEntries.values())];

    if (tipo) {
      filtered = filtered.filter((e) => e.tipo === tipo);
    }

    if (data_inicio) {
      filtered = filtered.filter((e) => e.data >= data_inicio);
    }

    if (data_fim) {
      filtered = filtered.filter((e) => e.data <= data_fim);
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

  // POST /financial/cashflow/entries - Criar entrada de fluxo de caixa
  http.post(`${API_BASE_URL}/financial/cashflow/entries`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.descricao || !body.valor || !body.tipo) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Descrição, valor e tipo são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newEntry = {
      ...mockCashflowEntry,
      ...body,
      id: `cashflow-${Date.now()}`,
      updated_at: new Date().toISOString(),
    };

    dynamicCashflowEntries.set(newEntry.id, newEntry as typeof mockCashflowEntry);

    return HttpResponse.json(newEntry, { status: 201 });
  }),

  // GET /financial/cashflow/projection - Projeção de fluxo de caixa
  http.get(`${API_BASE_URL}/financial/cashflow/projection`, ({ request }) => {
    const url = new URL(request.url);
    const dias = parseInt(url.searchParams.get('dias') || '30');

    return HttpResponse.json(
      {
        ...mockCashflowProjection,
        periodo: `Próximos ${dias} dias`,
      },
      { status: 200 }
    );
  }),

  // GET /financial/cashflow/dashboard - Dashboard de fluxo de caixa
  http.get(`${API_BASE_URL}/financial/cashflow/dashboard`, () => {
    const allEntries = [...mockCashflowEntries, ...Array.from(dynamicCashflowEntries.values())];
    const dashboard = {
      saldo_atual: 150000,
      entradas_mes: allEntries
        .filter((e) => e.tipo === 'entrada')
        .reduce((acc, e) => acc + e.valor, 0),
      saidas_mes: allEntries
        .filter((e) => e.tipo === 'saida')
        .reduce((acc, e) => acc + e.valor, 0),
      saldo_previsto_30dias: 165000,
      transacoes_pendentes_conciliacao: allEntries.filter((e) => !e.conciliado).length,
    };

    return HttpResponse.json(dashboard, { status: 200 });
  }),

  // ========== NOTAS FISCAIS ==========

  // GET /financial/fiscal/nfe - Listar NFes
  http.get(`${API_BASE_URL}/financial/fiscal/nfe`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const cliente_id = url.searchParams.get('cliente_id');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockNFes, ...Array.from(dynamicNFes.values())];

    if (status) {
      filtered = filtered.filter((n) => n.status === status);
    }

    if (cliente_id) {
      filtered = filtered.filter((n) => n.cliente_id === cliente_id);
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

  // GET /financial/fiscal/nfe/:id - Obter NFe específica
  http.get(`${API_BASE_URL}/financial/fiscal/nfe/:id`, ({ params }) => {
    const { id } = params;
    const nfe = mockNFes.find((n) => n.id === id);

    if (!nfe) {
      const dynamicNFe = dynamicNFes.get(id as string);
      if (dynamicNFe) {
        return HttpResponse.json(dynamicNFe, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'NFe não encontrada' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(nfe, { status: 200 });
  }),

  // POST /financial/fiscal/nfe - Criar NFe
  http.post(`${API_BASE_URL}/financial/fiscal/nfe`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    if (!body.cliente_id || !body.itens) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Cliente e itens são obrigatórios' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newNFe = {
      ...mockNFe,
      ...body,
      id: `nfe-${Date.now()}`,
      numero: String(mockNFes.length + dynamicNFes.size + 1).padStart(6, '0'),
      status: 'rascunho',
      data_emissao: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    dynamicNFes.set(newNFe.id, newNFe as typeof mockNFe);

    return HttpResponse.json(newNFe, { status: 201 });
  }),

  // POST /financial/fiscal/nfe/emitir - Emitir NFe
  http.post(`${API_BASE_URL}/financial/fiscal/nfe/emitir`, async ({ request }) => {
    const body = await request.json() as { nfe_id: string };
    const { nfe_id } = body;

    const nfe = mockNFes.find((n) => n.id === nfe_id);
    const dynamicNFe = dynamicNFes.get(nfe_id);

    const updated = {
      ...(dynamicNFe || nfe || mockNFe),
      id: nfe_id,
      status: 'autorizada',
      chave_acesso: `3526021234567800019055001${Date.now().toString().slice(-20)}`,
      protocolo: `1352602${Date.now().toString().slice(-10)}`,
      updated_at: new Date().toISOString(),
    };

    dynamicNFes.set(nfe_id, updated as typeof mockNFe);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // POST /financial/fiscal/nfe/:id/cancelar - Cancelar NFe
  http.post(`${API_BASE_URL}/financial/fiscal/nfe/:id/cancelar`, ({ params }) => {
    const { id } = params;

    const nfe = mockNFes.find((n) => n.id === id);
    const dynamicNFe = dynamicNFes.get(id as string);

    const updated = {
      ...(dynamicNFe || nfe || mockNFe),
      id: id as string,
      status: 'cancelada',
      updated_at: new Date().toISOString(),
    };

    dynamicNFes.set(id as string, updated as typeof mockNFe);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // GET /financial/fiscal/dashboard - Dashboard fiscal
  http.get(`${API_BASE_URL}/financial/fiscal/dashboard`, () => {
    const allNFes = [...mockNFes, ...Array.from(dynamicNFes.values())];
    const dashboard = {
      total_nfes: allNFes.length,
      autorizadas: allNFes.filter((n) => n.status === 'autorizada').length,
      canceladas: allNFes.filter((n) => n.status === 'cancelada').length,
      rascunho: allNFes.filter((n) => n.status === 'rascunho').length,
      valor_total_autorizado: allNFes
        .filter((n) => n.status === 'autorizada')
        .reduce((acc, n) => acc + n.valor_total, 0),
      valor_total_impostos: allNFes
        .filter((n) => n.status === 'autorizada')
        .reduce((acc, n) => acc + n.valor_impostos, 0),
    };

    return HttpResponse.json(dashboard, { status: 200 });
  }),
];
