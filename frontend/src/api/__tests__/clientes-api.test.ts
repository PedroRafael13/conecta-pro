/**
 * Testes de Integração - Clientes API
 *
 * Testa endpoints de clientes:
 * - Listar clientes
 * - Criar cliente
 * - Atualizar cliente
 * - Deletar cliente
 */

import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import axios from 'axios';
import { clientesHandlers } from '@/test/mocks/handlers/clientes';
import { server } from '@/test/mocks/server';
import {
  mockClientes,
  mockCliente,
  createMockCliente,
} from '@/test/fixtures/clientes';

// Configura axios para testes
const API_URL = 'http://localhost:8080/api/v1';
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

describe('Clientes API - Listar Clientes', () => {
  beforeAll(() => {
    server.use(...clientesHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve listar todos os clientes', async () => {
    const response = await apiClient.get('/clientes');

    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('data');
    expect(response.data).toHaveProperty('total');
    expect(response.data).toHaveProperty('page');
    expect(response.data).toHaveProperty('limit');
    expect(Array.isArray(response.data.data)).toBe(true);
    expect(response.data.data.length).toBe(mockClientes.length);
  });

  it('deve retornar paginação correta', async () => {
    const response = await apiClient.get('/clientes?page=1&limit=2');

    expect(response.status).toBe(200);
    expect(response.data.page).toBe(1);
    expect(response.data.limit).toBe(2);
    expect(response.data.data.length).toBeLessThanOrEqual(2);
    expect(response.data.total_pages).toBe(Math.ceil(mockClientes.length / 2));
  });

  it('deve filtrar clientes por status', async () => {
    const response = await apiClient.get('/clientes?status=ativo');

    expect(response.status).toBe(200);
    expect(response.data.data.every((c: typeof mockCliente) => c.status === 'ativo')).toBe(true);
  });

  it('deve filtrar clientes por categoria', async () => {
    const response = await apiClient.get('/clientes?categoria=empresa');

    expect(response.status).toBe(200);
    expect(response.data.data.every((c: typeof mockCliente) => c.categoria === 'empresa')).toBe(true);
  });

  it('deve buscar clientes por texto', async () => {
    const response = await apiClient.get('/clientes?search=Empresa');

    expect(response.status).toBe(200);
    expect(response.data.data.length).toBeGreaterThan(0);
    expect(response.data.data[0].nome.toLowerCase()).toContain('empresa');
  });

  it('deve buscar clientes por documento', async () => {
    const response = await apiClient.get('/clientes?search=12.345.678/0001-90');

    expect(response.status).toBe(200);
    expect(response.data.data.length).toBeGreaterThan(0);
    expect(response.data.data[0].documento).toContain('12.345.678');
  });

  it('deve retornar lista vazia quando não encontrar resultados', async () => {
    const response = await apiClient.get('/clientes?search=XYZ123NaoExiste');

    expect(response.status).toBe(200);
    expect(response.data.data).toEqual([]);
    expect(response.data.total).toBe(0);
  });
});

describe('Clientes API - Obter Cliente', () => {
  beforeAll(() => {
    server.use(...clientesHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve obter cliente por ID', async () => {
    const response = await apiClient.get('/clientes/cliente-001');

    expect(response.status).toBe(200);
    expect(response.data.id).toBe('cliente-001');
    expect(response.data).toHaveProperty('nome');
    expect(response.data).toHaveProperty('email');
    expect(response.data).toHaveProperty('documento');
    expect(response.data).toHaveProperty('status');
  });

  it('deve retornar todos os dados do cliente', async () => {
    const response = await apiClient.get('/clientes/cliente-001');

    expect(response.status).toBe(200);
    expect(response.data.nome).toBe(mockCliente.nome);
    expect(response.data.email).toBe(mockCliente.email);
    expect(response.data.documento).toBe(mockCliente.documento);
    expect(response.data.tipo_documento).toBe(mockCliente.tipo_documento);
    expect(response.data.status).toBe(mockCliente.status);
    expect(response.data).toHaveProperty('endereco');
    expect(response.data).toHaveProperty('responsavel_nome');
  });

  it('deve retornar erro 404 para cliente inexistente', async () => {
    try {
      await apiClient.get('/clientes/cliente-inexistente');
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(404);
        expect(error.response?.data.detail).toContain('Cliente não encontrado');
      }
    }
  });
});

describe('Clientes API - Criar Cliente', () => {
  beforeAll(() => {
    server.use(...clientesHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve criar novo cliente com dados válidos', async () => {
    const newCliente = {
      nome: 'Novo Cliente Teste',
      email: 'novo.cliente@teste.com',
      documento: '11.222.333/0001-44',
      tipo_documento: 'cnpj',
      telefone: '(11) 4444-5555',
      status: 'ativo',
      categoria: 'empresa',
    };

    const response = await apiClient.post('/clientes', newCliente);

    expect(response.status).toBe(201);
    expect(response.data.nome).toBe(newCliente.nome);
    expect(response.data.email).toBe(newCliente.email);
    expect(response.data.documento).toBe(newCliente.documento);
    expect(response.data).toHaveProperty('id');
    expect(response.data).toHaveProperty('data_cadastro');
  });

  it('deve retornar erro 400 quando nome não for fornecido', async () => {
    const invalidCliente = {
      email: 'teste@teste.com',
      documento: '11.222.333/0001-44',
    };

    try {
      await apiClient.post('/clientes', invalidCliente);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(400);
        expect(error.response?.data.detail).toContain('nome');
      }
    }
  });

  it('deve retornar erro 400 quando email não for fornecido', async () => {
    const invalidCliente = {
      nome: 'Teste',
      documento: '11.222.333/0001-44',
    };

    try {
      await apiClient.post('/clientes', invalidCliente);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(400);
        expect(error.response?.data.detail).toContain('email');
      }
    }
  });

  it('deve retornar erro 400 quando documento não for fornecido', async () => {
    const invalidCliente = {
      nome: 'Teste',
      email: 'teste@teste.com',
    };

    try {
      await apiClient.post('/clientes', invalidCliente);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(400);
        expect(error.response?.data.detail).toContain('documento');
      }
    }
  });

  it('deve retornar erro 409 quando email já existir', async () => {
    const duplicateCliente = {
      nome: 'Teste',
      email: mockCliente.email, // Email já existente
      documento: '99.888.777/0001-66',
    };

    try {
      await apiClient.post('/clientes', duplicateCliente);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(409);
        expect(error.response?.data.detail).toContain('Email já cadastrado');
      }
    }
  });

  it('deve retornar erro 409 quando documento já existir', async () => {
    const duplicateCliente = {
      nome: 'Teste',
      email: 'novo@email.com',
      documento: mockCliente.documento, // Documento já existente
    };

    try {
      await apiClient.post('/clientes', duplicateCliente);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(409);
        expect(error.response?.data.detail).toContain('Documento já cadastrado');
      }
    }
  });

  it('deve criar cliente com endereço completo', async () => {
    const clienteComEndereco = {
      nome: 'Cliente Com Endereço',
      email: 'endereco@teste.com',
      documento: '22.333.444/0001-55',
      tipo_documento: 'cnpj',
      endereco: {
        cep: '04538-132',
        logradouro: 'Rua Funchal',
        numero: '500',
        complemento: 'Sala 100',
        bairro: 'Vila Olímpia',
        cidade: 'São Paulo',
        estado: 'SP',
      },
    };

    const response = await apiClient.post('/clientes', clienteComEndereco);

    expect(response.status).toBe(201);
    expect(response.data.endereco).toEqual(clienteComEndereco.endereco);
  });

  it('deve criar cliente com dados do responsável', async () => {
    const clienteComResponsavel = {
      nome: 'Cliente Com Responsável',
      email: 'responsavel@teste.com',
      documento: '33.444.555/0001-66',
      responsavel_nome: 'João Responsável',
      responsavel_email: 'joao@responsavel.com',
      responsavel_telefone: '(11) 98888-7777',
    };

    const response = await apiClient.post('/clientes', clienteComResponsavel);

    expect(response.status).toBe(201);
    expect(response.data.responsavel_nome).toBe(clienteComResponsavel.responsavel_nome);
    expect(response.data.responsavel_email).toBe(clienteComResponsavel.responsavel_email);
  });
});

describe('Clientes API - Atualizar Cliente', () => {
  beforeAll(() => {
    server.use(...clientesHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve atualizar cliente existente com PUT', async () => {
    const updateData = {
      nome: 'Nome Atualizado',
      telefone: '(11) 99999-8888',
    };

    const response = await apiClient.put('/clientes/cliente-001', updateData);

    expect(response.status).toBe(200);
    expect(response.data.nome).toBe(updateData.nome);
    expect(response.data.telefone).toBe(updateData.telefone);
    expect(response.data).toHaveProperty('updated_at');
  });

  it('deve atualizar cliente com PATCH', async () => {
    const patchData = {
      observacoes: 'Nova observação',
    };

    const response = await apiClient.patch('/clientes/cliente-001', patchData);

    expect(response.status).toBe(200);
    expect(response.data.observacoes).toBe(patchData.observacoes);
    expect(response.data).toHaveProperty('updated_at');
  });

  it('deve retornar erro 404 ao atualizar cliente inexistente', async () => {
    try {
      await apiClient.put('/clientes/cliente-inexistente', { nome: 'Teste' });
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(404);
        expect(error.response?.data.detail).toContain('Cliente não encontrado');
      }
    }
  });

  it('deve retornar erro 409 ao atualizar para email duplicado', async () => {
    try {
      await apiClient.put('/clientes/cliente-001', {
        email: mockClientes[1]!.email, // Email de outro cliente
      });
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(409);
        expect(error.response?.data.detail).toContain('Email já cadastrado');
      }
    }
  });

  it('deve permitir atualizar status do cliente', async () => {
    const response = await apiClient.put('/clientes/cliente-001', {
      status: 'inativo',
    });

    expect(response.status).toBe(200);
    expect(response.data.status).toBe('inativo');
  });

  it('deve permitir atualizar endereço do cliente', async () => {
    const novoEndereco = {
      endereco: {
        cep: '01310-200',
        logradouro: 'Avenida Paulista',
        numero: '2000',
        bairro: 'Bela Vista',
        cidade: 'São Paulo',
        estado: 'SP',
      },
    };

    const response = await apiClient.put('/clientes/cliente-001', novoEndereco);

    expect(response.status).toBe(200);
    expect(response.data.endereco).toEqual(novoEndereco.endereco);
  });
});

describe('Clientes API - Deletar Cliente', () => {
  beforeAll(() => {
    server.use(...clientesHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve deletar cliente existente', async () => {
    const response = await apiClient.delete('/clientes/cliente-001');

    expect(response.status).toBe(204);
    expect(response.data).toBe('');
  });

  it('deve retornar erro 404 ao deletar cliente inexistente', async () => {
    try {
      await apiClient.delete('/clientes/cliente-inexistente');
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(404);
        expect(error.response?.data.detail).toContain('Cliente não encontrado');
      }
    }
  });
});

describe('Clientes API - Endpoints Adicionais', () => {
  beforeAll(() => {
    server.use(...clientesHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve listar contratos do cliente', async () => {
    const response = await apiClient.get('/clientes/cliente-001/contratos');

    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
    expect(response.data[0]).toHaveProperty('id');
    expect(response.data[0]).toHaveProperty('numero');
    expect(response.data[0]).toHaveProperty('status');
    expect(response.data[0].cliente_id).toBe('cliente-001');
  });

  it('deve retornar erro 404 ao listar contratos de cliente inexistente', async () => {
    try {
      await apiClient.get('/clientes/cliente-inexistente/contratos');
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(404);
      }
    }
  });

  it('deve listar contatos do cliente', async () => {
    const response = await apiClient.get('/clientes/cliente-001/contatos');

    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
    expect(response.data[0]).toHaveProperty('nome');
    expect(response.data[0]).toHaveProperty('email');
    expect(response.data[0]).toHaveProperty('cargo');
  });

  it('deve retornar estatísticas de clientes', async () => {
    const response = await apiClient.get('/clientes/stats');

    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('total');
    expect(response.data).toHaveProperty('ativos');
    expect(response.data).toHaveProperty('inativos');
    expect(response.data).toHaveProperty('pendentes');
    expect(response.data).toHaveProperty('novos_este_mes');
    expect(response.data.total).toBe(mockClientes.length);
  });
});

describe('Clientes API - Casos de Uso Completos', () => {
  beforeAll(() => {
    server.use(...clientesHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve realizar fluxo completo de CRUD', async () => {
    // 1. Criar cliente
    const newCliente = createMockCliente({
      id: undefined,
      nome: 'Cliente CRUD Teste',
      email: 'crud@teste.com',
      documento: '77.888.999/0001-11',
    });

    const createResponse = await apiClient.post('/clientes', newCliente);
    expect(createResponse.status).toBe(201);
    const clienteId = createResponse.data.id;

    // 2. Ler cliente
    const readResponse = await apiClient.get(`/clientes/${clienteId}`);
    expect(readResponse.status).toBe(200);
    expect(readResponse.data.nome).toBe(newCliente.nome);

    // 3. Atualizar cliente
    const updateResponse = await apiClient.put(`/clientes/${clienteId}`, {
      nome: 'Nome Atualizado',
    });
    expect(updateResponse.status).toBe(200);
    expect(updateResponse.data.nome).toBe('Nome Atualizado');

    // 4. Deletar cliente
    const deleteResponse = await apiClient.delete(`/clientes/${clienteId}`);
    expect(deleteResponse.status).toBe(204);

    // 5. Verificar que foi deletado
    try {
      await apiClient.get(`/clientes/${clienteId}`);
      expect.fail('Deveria ter lançado erro');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        expect(error.response?.status).toBe(404);
      }
    }
  });

  it('deve filtrar e paginar resultados corretamente', async () => {
    // Busca com filtros combinados
    const response = await apiClient.get('/clientes?status=ativo&categoria=empresa&page=1&limit=5');

    expect(response.status).toBe(200);
    expect(response.data.page).toBe(1);
    expect(response.data.limit).toBe(5);

    // Todos os resultados devem corresponder aos filtros
    response.data.data.forEach((cliente: typeof mockCliente) => {
      expect(cliente.status).toBe('ativo');
      expect(cliente.categoria).toBe('empresa');
    });
  });
});
