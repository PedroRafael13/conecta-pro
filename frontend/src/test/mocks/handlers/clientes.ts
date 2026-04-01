/**
 * MSW Handlers para mock de APIs de Clientes
 */

import { http, HttpResponse } from 'msw';
import {
  mockClientes,
  mockCliente,
} from '../../fixtures/clientes';

const API_BASE_URL = 'http://localhost:8080/api/v1';

// Store para clientes criados dinamicamente durante os testes
const dynamicClientes: Map<string, typeof mockCliente> = new Map();

export const clientesHandlers = [
  // ========== LISTAR CLIENTES ==========

  // GET /clientes - Listar todos os clientes
  http.get(`${API_BASE_URL}/clientes`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const categoria = url.searchParams.get('categoria');
    const search = url.searchParams.get('search');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    let filtered = [...mockClientes];

    // Filtrar por status
    if (status) {
      filtered = filtered.filter((c) => c.status === status);
    }

    // Filtrar por categoria
    if (categoria) {
      filtered = filtered.filter((c) => c.categoria === categoria);
    }

    // Busca por texto
    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.nome.toLowerCase().includes(searchLower) ||
          c.email.toLowerCase().includes(searchLower) ||
          c.documento.includes(search)
      );
    }

    // Paginação
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

  // ========== ESTATÍSTICAS (deve vir antes de :id) ==========

  // GET /clientes/stats - Estatísticas de clientes
  http.get(`${API_BASE_URL}/clientes/stats`, () => {
    const stats = {
      total: mockClientes.length,
      ativos: mockClientes.filter((c) => c.status === 'ativo').length,
      inativos: mockClientes.filter((c) => c.status === 'inativo').length,
      pendentes: mockClientes.filter((c) => c.status === 'pendente').length,
      novos_este_mes: 2,
    };

    return HttpResponse.json(stats, { status: 200 });
  }),

  // ========== OBTER CLIENTE ==========

  // GET /clientes/:id - Obter cliente específico
  http.get(`${API_BASE_URL}/clientes/:id`, ({ params }) => {
    const { id } = params;
    const cliente = mockClientes.find((c) => c.id === id);

    // Se não encontrar nos mocks fixos, verifica na store dinâmica
    if (!cliente) {
      const dynamicCliente = dynamicClientes.get(id as string);
      if (dynamicCliente) {
        return HttpResponse.json(dynamicCliente, { status: 200 });
      }
      return new HttpResponse(
        JSON.stringify({ detail: 'Cliente não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(cliente, { status: 200 });
  }),

  // ========== CRIAR CLIENTE ==========

  // POST /clientes - Criar novo cliente
  http.post(`${API_BASE_URL}/clientes`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;

    // Validação básica
    if (!body.nome || !body.email || !body.documento) {
      return new HttpResponse(
        JSON.stringify({
          detail: 'Campos obrigatórios: nome, email, documento'
        }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Verifica duplicidade de email
    const emailExists = mockClientes.some(
      (c) => c.email === body.email
    );
    if (emailExists) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Email já cadastrado' }),
        { status: 409, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Verifica duplicidade de documento
    const docExists = mockClientes.some(
      (c) => c.documento === body.documento
    );
    if (docExists) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Documento já cadastrado' }),
        { status: 409, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const newCliente = {
      ...mockCliente,
      ...body,
      id: `cliente-${Date.now()}`,
      data_cadastro: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Armazena na store dinâmica
    dynamicClientes.set(newCliente.id, newCliente as typeof mockCliente);

    return HttpResponse.json(newCliente, { status: 201 });
  }),

  // ========== ATUALIZAR CLIENTE ==========

  // PUT /clientes/:id - Atualizar cliente
  http.put(`${API_BASE_URL}/clientes/:id`, async ({ params, request }) => {
    const { id } = params;
    const cliente = mockClientes.find((c) => c.id === id);
    const dynamicCliente = dynamicClientes.get(id as string);

    if (!cliente && !dynamicCliente) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Cliente não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const body = await request.json() as Record<string, unknown>;

    const baseCliente = dynamicCliente || cliente || mockCliente;

    // Verifica duplicidade de email se estiver sendo alterado
    if (body.email && body.email !== baseCliente.email) {
      const emailExists = mockClientes.some(
        (c) => c.email === body.email && c.id !== id
      );
      if (emailExists) {
        return new HttpResponse(
          JSON.stringify({ detail: 'Email já cadastrado para outro cliente' }),
          { status: 409, headers: { 'Content-Type': 'application/json' } }
        );
      }
    }

    const updated = {
      ...baseCliente,
      ...body,
      id: id as string,
      updated_at: new Date().toISOString(),
    };

    // Atualiza na store dinâmica
    dynamicClientes.set(id as string, updated as typeof mockCliente);

    return HttpResponse.json(updated, { status: 200 });
  }),

  // PATCH /clientes/:id - Atualização parcial do cliente
  http.patch(`${API_BASE_URL}/clientes/:id`, async ({ params, request }) => {
    const { id } = params;
    const cliente = mockClientes.find((c) => c.id === id);

    if (!cliente) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Cliente não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const body = await request.json() as Record<string, unknown>;

    const updated = {
      ...cliente,
      ...body,
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json(updated, { status: 200 });
  }),

  // ========== DELETAR CLIENTE ==========

  // DELETE /clientes/:id - Deletar cliente
  http.delete(`${API_BASE_URL}/clientes/:id`, ({ params }) => {
    const { id } = params;
    const cliente = mockClientes.find((c) => c.id === id);

    // Remove da store dinâmica se existir
    dynamicClientes.delete(id as string);

    // Retorna sucesso mesmo se não encontrar nos mocks fixos
    if (!cliente) {
      return new HttpResponse(null, { status: 204 });
    }

    return new HttpResponse(null, { status: 204 });
  }),

  // ========== ENDPOINTS ADICIONAIS ==========

  // GET /clientes/:id/contratos - Listar contratos do cliente
  http.get(`${API_BASE_URL}/clientes/:id/contratos`, ({ params }) => {
    const { id } = params;
    const cliente = mockClientes.find((c) => c.id === id);

    if (!cliente) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Cliente não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(
      [
        {
          id: 'contrato-001',
          numero: 'CONT-2026-001',
          cliente_id: id,
          status: 'ativo',
          valor: 150000,
          data_inicio: '2026-01-01T00:00:00Z',
          data_fim: '2026-12-31T23:59:59Z',
        },
      ],
      { status: 200 }
    );
  }),

  // GET /clientes/:id/contatos - Listar contatos do cliente
  http.get(`${API_BASE_URL}/clientes/:id/contatos`, ({ params }) => {
    const { id } = params;
    const cliente = mockClientes.find((c) => c.id === id);

    if (!cliente) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Cliente não encontrado' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(
      [
        {
          id: 'contato-001',
          nome: cliente.responsavel_nome || 'Responsável',
          email: cliente.responsavel_email,
          telefone: cliente.responsavel_telefone,
          cargo: 'Gerente',
          principal: true,
        },
      ],
      { status: 200 }
    );
  }),

];
