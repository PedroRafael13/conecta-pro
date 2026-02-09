/**
 * Testes de Integração - CRM API
 *
 * Testa endpoints de CRM:
 * - Leads
 * - Oportunidades
 * - Propostas
 */

import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import axios from 'axios';
import { crmHandlers } from '@/test/mocks/handlers/crm';
import { server } from '@/test/mocks/server';
import {
  mockLeads,
  mockLead,
  mockOportunidades,
  mockOportunidade,
  mockPropostas,
  mockProposta,
  createMockLead,
  createMockOportunidade,
  createMockProposta,
} from '@/test/fixtures/crm';

// Configura axios para testes
const API_URL = 'http://localhost:8080/api/v1';
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ========== LEADS ==========

describe('CRM API - Leads', () => {
  beforeAll(() => {
    server.use(...crmHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  describe('Listar Leads', () => {
    it('deve listar todos os leads', async () => {
      const response = await apiClient.get('/crm/leads');

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('data');
      expect(response.data).toHaveProperty('total');
      expect(Array.isArray(response.data.data)).toBe(true);
      expect(response.data.data.length).toBe(mockLeads.length);
    });

    it('deve paginar resultados', async () => {
      const response = await apiClient.get('/crm/leads?page=1&limit=2');

      expect(response.status).toBe(200);
      expect(response.data.page).toBe(1);
      expect(response.data.limit).toBe(2);
      expect(response.data.data.length).toBeLessThanOrEqual(2);
    });

    it('deve filtrar leads por status', async () => {
      const response = await apiClient.get('/crm/leads?status=novo');

      expect(response.status).toBe(200);
      expect(response.data.data.every((l: typeof mockLead) => l.status === 'novo')).toBe(true);
    });

    it('deve filtrar leads por prioridade', async () => {
      const response = await apiClient.get('/crm/leads?prioridade=alta');

      expect(response.status).toBe(200);
      expect(response.data.data.every((l: typeof mockLead) => l.prioridade === 'alta')).toBe(true);
    });

    it('deve filtrar leads por origem', async () => {
      const response = await apiClient.get('/crm/leads?origem=site');

      expect(response.status).toBe(200);
      expect(response.data.data.every((l: typeof mockLead) => l.origem === 'site')).toBe(true);
    });

    it('deve buscar leads por texto', async () => {
      const response = await apiClient.get('/crm/leads?search=Carlos');

      expect(response.status).toBe(200);
      expect(response.data.data.length).toBeGreaterThan(0);
      expect(response.data.data[0].nome.toLowerCase()).toContain('carlos');
    });
  });

  describe('Obter Lead', () => {
    it('deve obter lead por ID', async () => {
      const response = await apiClient.get('/crm/leads/lead-001');

      expect(response.status).toBe(200);
      expect(response.data.id).toBe('lead-001');
      expect(response.data).toHaveProperty('nome');
      expect(response.data).toHaveProperty('email');
      expect(response.data).toHaveProperty('status');
    });

    it('deve retornar erro 404 para lead inexistente', async () => {
      try {
        await apiClient.get('/crm/leads/lead-inexistente');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
          expect(error.response?.data.detail).toContain('Lead não encontrado');
        }
      }
    });
  });

  describe('Criar Lead', () => {
    it('deve criar novo lead', async () => {
      const newLead = {
        nome: 'Novo Lead Teste',
        email: 'novo.lead@teste.com',
        telefone: '(11) 97777-6666',
        empresa: 'Empresa Teste',
        cargo: 'Diretor',
        origem: 'site',
        prioridade: 'media',
      };

      const response = await apiClient.post('/crm/leads', newLead);

      expect(response.status).toBe(201);
      expect(response.data.nome).toBe(newLead.nome);
      expect(response.data.email).toBe(newLead.email);
      expect(response.data.status).toBe('novo');
      expect(response.data).toHaveProperty('id');
      expect(response.data).toHaveProperty('data_criacao');
    });

    it('deve retornar erro 400 quando nome não for fornecido', async () => {
      try {
        await apiClient.post('/crm/leads', { email: 'teste@teste.com' });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
          expect(error.response?.data.detail).toContain('Nome e email são obrigatórios');
        }
      }
    });

    it('deve retornar erro 400 quando email não for fornecido', async () => {
      try {
        await apiClient.post('/crm/leads', { nome: 'Teste' });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
        }
      }
    });
  });

  describe('Atualizar Lead', () => {
    it('deve atualizar lead existente', async () => {
      const updateData = {
        nome: 'Nome Atualizado',
        prioridade: 'urgente',
      };

      const response = await apiClient.put('/crm/leads/lead-001', updateData);

      expect(response.status).toBe(200);
      expect(response.data.nome).toBe(updateData.nome);
      expect(response.data.prioridade).toBe(updateData.prioridade);
      expect(response.data).toHaveProperty('updated_at');
    });

    it('deve retornar erro 404 ao atualizar lead inexistente', async () => {
      try {
        await apiClient.put('/crm/leads/lead-inexistente', { nome: 'Teste' });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });

  describe('Deletar Lead', () => {
    it('deve deletar lead existente', async () => {
      const response = await apiClient.delete('/crm/leads/lead-001');

      expect(response.status).toBe(204);
    });

    it('deve retornar erro 404 ao deletar lead inexistente', async () => {
      try {
        await apiClient.delete('/crm/leads/lead-inexistente');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });

  describe('Qualificar Lead', () => {
    it('deve qualificar lead', async () => {
      const response = await apiClient.post('/crm/leads/lead-001/qualificar');

      expect(response.status).toBe(200);
      expect(response.data.status).toBe('qualificado');
      expect(response.data).toHaveProperty('updated_at');
    });

    it('deve retornar erro 404 ao qualificar lead inexistente', async () => {
      try {
        await apiClient.post('/crm/leads/lead-inexistente/qualificar');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });

  describe('Converter Lead', () => {
    it('deve converter lead em oportunidade', async () => {
      const response = await apiClient.post('/crm/leads/lead-001/convert', {
        valor_estimado: 100000,
      });

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('lead');
      expect(response.data).toHaveProperty('oportunidade');
      expect(response.data.lead.status).toBe('convertido');
      expect(response.data.lead).toHaveProperty('data_conversao');
      expect(response.data.oportunidade).toHaveProperty('id');
    });

    it('deve converter lead sem valor estimado', async () => {
      const response = await apiClient.post('/crm/leads/lead-001/convert');

      expect(response.status).toBe(200);
      expect(response.data.lead.status).toBe('convertido');
    });
  });
});

// ========== OPORTUNIDADES ==========

describe('CRM API - Oportunidades', () => {
  beforeAll(() => {
    server.use(...crmHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  describe('Listar Oportunidades', () => {
    it('deve listar todas as oportunidades', async () => {
      const response = await apiClient.get('/crm/oportunidades');

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('data');
      expect(response.data).toHaveProperty('total');
      expect(Array.isArray(response.data.data)).toBe(true);
    });

    it('deve filtrar por etapa', async () => {
      const response = await apiClient.get('/crm/oportunidades?etapa=proposta');

      expect(response.status).toBe(200);
      expect(response.data.data.every((o: typeof mockOportunidade) => o.etapa === 'proposta')).toBe(true);
    });

    it('deve filtrar por cliente', async () => {
      const response = await apiClient.get('/crm/oportunidades?cliente_id=cliente-001');

      expect(response.status).toBe(200);
      expect(response.data.data.every((o: typeof mockOportunidade) => o.cliente_id === 'cliente-001')).toBe(true);
    });

    it('deve filtrar por responsável', async () => {
      const response = await apiClient.get('/crm/oportunidades?responsavel_id=user-001');

      expect(response.status).toBe(200);
      expect(response.data.data.every((o: typeof mockOportunidade) => o.responsavel_id === 'user-001')).toBe(true);
    });
  });

  describe('Obter Oportunidade', () => {
    it('deve obter oportunidade por ID', async () => {
      const response = await apiClient.get('/crm/oportunidades/oportunidade-001');

      expect(response.status).toBe(200);
      expect(response.data.id).toBe('oportunidade-001');
      expect(response.data).toHaveProperty('titulo');
      expect(response.data).toHaveProperty('cliente_id');
      expect(response.data).toHaveProperty('etapa');
      expect(response.data).toHaveProperty('valor_estimado');
    });

    it('deve retornar erro 404 para oportunidade inexistente', async () => {
      try {
        await apiClient.get('/crm/oportunidades/op-inexistente');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
          expect(error.response?.data.detail).toContain('Oportunidade não encontrada');
        }
      }
    });
  });

  describe('Criar Oportunidade', () => {
    it('deve criar nova oportunidade', async () => {
      const newOportunidade = {
        titulo: 'Nova Oportunidade Teste',
        cliente_id: 'cliente-001',
        cliente_nome: 'Cliente Teste',
        responsavel_id: 'user-001',
        etapa: 'prospeccao',
        valor_estimado: 50000,
        origem: 'indicacao',
      };

      const response = await apiClient.post('/crm/oportunidades', newOportunidade);

      expect(response.status).toBe(201);
      expect(response.data.titulo).toBe(newOportunidade.titulo);
      expect(response.data.cliente_id).toBe(newOportunidade.cliente_id);
      expect(response.data).toHaveProperty('id');
      expect(response.data).toHaveProperty('data_criacao');
    });

    it('deve retornar erro 400 quando título não for fornecido', async () => {
      try {
        await apiClient.post('/crm/oportunidades', {
          cliente_id: 'cliente-001',
        });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
          expect(error.response?.data.detail).toContain('Título e cliente são obrigatórios');
        }
      }
    });

    it('deve retornar erro 400 quando cliente não for fornecido', async () => {
      try {
        await apiClient.post('/crm/oportunidades', {
          titulo: 'Teste',
        });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
        }
      }
    });
  });

  describe('Atualizar Oportunidade', () => {
    it('deve atualizar oportunidade', async () => {
      const updateData = {
        titulo: 'Título Atualizado',
        valor_estimado: 60000,
      };

      const response = await apiClient.put('/crm/oportunidades/oportunidade-001', updateData);

      expect(response.status).toBe(200);
      expect(response.data.titulo).toBe(updateData.titulo);
      expect(response.data.valor_estimado).toBe(updateData.valor_estimado);
    });

    it('deve retornar erro 404 ao atualizar oportunidade inexistente', async () => {
      try {
        await apiClient.put('/crm/oportunidades/op-inexistente', { titulo: 'Teste' });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });

  describe('Avançar Etapa', () => {
    it('deve avançar etapa da oportunidade', async () => {
      const response = await apiClient.post('/crm/oportunidades/oportunidade-001/avancar');

      expect(response.status).toBe(200);
      expect(response.data.etapa).toBeDefined();
      expect(response.data).toHaveProperty('updated_at');
    });

    it('deve retornar erro 404 ao avançar oportunidade inexistente', async () => {
      try {
        await apiClient.post('/crm/oportunidades/op-inexistente/avancar');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });

  describe('Ganhar Oportunidade', () => {
    it('deve marcar oportunidade como ganha', async () => {
      const response = await apiClient.post('/crm/oportunidades/oportunidade-001/ganhar', {
        valor_final: 260000,
      });

      expect(response.status).toBe(200);
      expect(response.data.etapa).toBe('fechamento');
      expect(response.data.probabilidade).toBe(100);
      expect(response.data.valor_final).toBe(260000);
      expect(response.data).toHaveProperty('data_fechamento');
    });

    it('deve ganhar oportunidade sem valor final', async () => {
      const response = await apiClient.post('/crm/oportunidades/oportunidade-001/ganhar');

      expect(response.status).toBe(200);
      expect(response.data.etapa).toBe('fechamento');
      expect(response.data.probabilidade).toBe(100);
    });
  });

  describe('Perder Oportunidade', () => {
    it('deve marcar oportunidade como perdida', async () => {
      const response = await apiClient.post('/crm/oportunidades/oportunidade-001/perder', {
        motivo: 'Preço muito alto',
      });

      expect(response.status).toBe(200);
      expect(response.data.etapa).toBe('perdido');
      expect(response.data.probabilidade).toBe(0);
      expect(response.data.motivo_perda).toBe('Preço muito alto');
      expect(response.data).toHaveProperty('data_fechamento');
    });

    it('deve perder oportunidade sem motivo específico', async () => {
      const response = await apiClient.post('/crm/oportunidades/oportunidade-001/perder');

      expect(response.status).toBe(200);
      expect(response.data.etapa).toBe('perdido');
      expect(response.data.motivo_perda).toBe('Motivo não especificado');
    });
  });
});

// ========== PROPOSTAS ==========

describe('CRM API - Propostas', () => {
  beforeAll(() => {
    server.use(...crmHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  describe('Listar Propostas', () => {
    it('deve listar todas as propostas', async () => {
      const response = await apiClient.get('/crm/propostas');

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('data');
      expect(response.data).toHaveProperty('total');
      expect(Array.isArray(response.data.data)).toBe(true);
    });

    it('deve filtrar por status', async () => {
      const response = await apiClient.get('/crm/propostas?status=aprovada');

      expect(response.status).toBe(200);
      expect(response.data.data.every((p: typeof mockProposta) => p.status === 'aprovada')).toBe(true);
    });

    it('deve filtrar por oportunidade', async () => {
      const response = await apiClient.get('/crm/propostas?oportunidade_id=oportunidade-001');

      expect(response.status).toBe(200);
      expect(response.data.data.every((p: typeof mockProposta) => p.oportunidade_id === 'oportunidade-001')).toBe(true);
    });

    it('deve filtrar por cliente', async () => {
      const response = await apiClient.get('/crm/propostas?cliente_id=cliente-003');

      expect(response.status).toBe(200);
      expect(response.data.data.every((p: typeof mockProposta) => p.cliente_id === 'cliente-003')).toBe(true);
    });
  });

  describe('Obter Proposta', () => {
    it('deve obter proposta por ID', async () => {
      const response = await apiClient.get('/crm/propostas/proposta-001');

      expect(response.status).toBe(200);
      expect(response.data.id).toBe('proposta-001');
      expect(response.data).toHaveProperty('numero');
      expect(response.data).toHaveProperty('status');
      expect(response.data).toHaveProperty('valor_total');
      expect(response.data).toHaveProperty('itens');
    });

    it('deve retornar erro 404 para proposta inexistente', async () => {
      try {
        await apiClient.get('/crm/propostas/prop-inexistente');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
          expect(error.response?.data.detail).toContain('Proposta não encontrada');
        }
      }
    });
  });

  describe('Criar Proposta', () => {
    it('deve criar nova proposta', async () => {
      const newProposta = {
        oportunidade_id: 'oportunidade-001',
        cliente_id: 'cliente-001',
        valor_total: 100000,
        itens: [
          {
            id: 'item-1',
            descricao: 'Serviço A',
            quantidade: 1,
            valor_unitario: 100000,
            valor_total: 100000,
          },
        ],
      };

      const response = await apiClient.post('/crm/propostas', newProposta);

      expect(response.status).toBe(201);
      expect(response.data.oportunidade_id).toBe(newProposta.oportunidade_id);
      expect(response.data.status).toBe('rascunho');
      expect(response.data).toHaveProperty('id');
      expect(response.data).toHaveProperty('numero');
    });

    it('deve retornar erro 400 quando oportunidade não for fornecida', async () => {
      try {
        await apiClient.post('/crm/propostas', {
          itens: [],
        });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
          expect(error.response?.data.detail).toContain('Oportunidade e itens são obrigatórios');
        }
      }
    });

    it('deve retornar erro 400 quando itens não forem fornecidos', async () => {
      try {
        await apiClient.post('/crm/propostas', {
          oportunidade_id: 'op-001',
        });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(400);
        }
      }
    });
  });

  describe('Atualizar Proposta', () => {
    it('deve atualizar proposta', async () => {
      const updateData = {
        observacoes: 'Nova observação',
        desconto: 5000,
      };

      const response = await apiClient.put('/crm/propostas/proposta-001', updateData);

      expect(response.status).toBe(200);
      expect(response.data.observacoes).toBe(updateData.observacoes);
      expect(response.data.desconto).toBe(updateData.desconto);
    });

    it('deve retornar erro 404 ao atualizar proposta inexistente', async () => {
      try {
        await apiClient.put('/crm/propostas/prop-inexistente', { observacoes: 'Test' });
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });

  describe('Enviar Proposta', () => {
    it('deve enviar proposta', async () => {
      const response = await apiClient.post('/crm/propostas/proposta-001/enviar');

      expect(response.status).toBe(200);
      expect(response.data.status).toBe('enviada');
    });

    it('deve retornar erro 404 ao enviar proposta inexistente', async () => {
      try {
        await apiClient.post('/crm/propostas/prop-inexistente/enviar');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });

  describe('Aprovar Proposta', () => {
    it('deve aprovar proposta', async () => {
      const response = await apiClient.post('/crm/propostas/proposta-001/aprovar');

      expect(response.status).toBe(200);
      expect(response.data.status).toBe('aprovada');
      expect(response.data).toHaveProperty('data_aprovacao');
    });
  });

  describe('Rejeitar Proposta', () => {
    it('deve rejeitar proposta com motivo', async () => {
      const response = await apiClient.post('/crm/propostas/proposta-001/rejeitar', {
        motivo: 'Condições comerciais inadequadas',
      });

      expect(response.status).toBe(200);
      expect(response.data.status).toBe('rejeitada');
      expect(response.data.motivo_rejeicao).toBe('Condições comerciais inadequadas');
      expect(response.data).toHaveProperty('data_rejeicao');
    });

    it('deve rejeitar proposta sem motivo específico', async () => {
      const response = await apiClient.post('/crm/propostas/proposta-001/rejeitar');

      expect(response.status).toBe(200);
      expect(response.data.status).toBe('rejeitada');
      expect(response.data.motivo_rejeicao).toBe('Motivo não especificado');
    });
  });

  describe('Deletar Proposta', () => {
    it('deve deletar proposta', async () => {
      const response = await apiClient.delete('/crm/propostas/proposta-001');

      expect(response.status).toBe(204);
    });

    it('deve retornar erro 404 ao deletar proposta inexistente', async () => {
      try {
        await apiClient.delete('/crm/propostas/prop-inexistente');
        expect.fail('Deveria ter lançado erro');
      } catch (error) {
        if (axios.isAxiosError(error)) {
          expect(error.response?.status).toBe(404);
        }
      }
    });
  });
});

// ========== DASHBOARD/STATS ==========

describe('CRM API - Dashboard/Stats', () => {
  beforeAll(() => {
    server.use(...crmHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve retornar estatísticas do CRM', async () => {
    const response = await apiClient.get('/crm/stats');

    expect(response.status).toBe(200);

    // Estatísticas de leads
    expect(response.data).toHaveProperty('leads');
    expect(response.data.leads).toHaveProperty('total');
    expect(response.data.leads).toHaveProperty('novos');
    expect(response.data.leads).toHaveProperty('convertidos');

    // Estatísticas de oportunidades
    expect(response.data).toHaveProperty('oportunidades');
    expect(response.data.oportunidades).toHaveProperty('total');
    expect(response.data.oportunidades).toHaveProperty('em_andamento');
    expect(response.data.oportunidades).toHaveProperty('ganhas');
    expect(response.data.oportunidades).toHaveProperty('perdidas');
    expect(response.data.oportunidades).toHaveProperty('valor_pipeline');

    // Estatísticas de propostas
    expect(response.data).toHaveProperty('propostas');
    expect(response.data.propostas).toHaveProperty('total');
    expect(response.data.propostas).toHaveProperty('rascunho');
    expect(response.data.propostas).toHaveProperty('aprovadas');
    expect(response.data.propostas).toHaveProperty('valor_total');
  });
});

// ========== FLUXOS COMPLETOS ==========

describe('CRM API - Fluxos Completos', () => {
  beforeAll(() => {
    server.use(...crmHandlers);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('deve realizar fluxo completo: Lead → Oportunidade → Proposta → Aprovação', async () => {
    // 1. Criar lead
    const leadData = createMockLead({
      nome: 'Lead Completo Teste',
      email: 'fluxo@teste.com',
      status: 'novo',
    });
    const leadResponse = await apiClient.post('/crm/leads', leadData);
    expect(leadResponse.status).toBe(201);
    const leadId = leadResponse.data.id;

    // 2. Qualificar lead
    const qualificarResponse = await apiClient.post(`/crm/leads/${leadId}/qualificar`);
    expect(qualificarResponse.status).toBe(200);
    expect(qualificarResponse.data.status).toBe('qualificado');

    // 3. Converter lead em oportunidade
    const convertResponse = await apiClient.post(`/crm/leads/${leadId}/convert`, {
      valor_estimado: 150000,
    });
    expect(convertResponse.status).toBe(200);
    expect(convertResponse.data.lead.status).toBe('convertido');
    const oportunidadeId = convertResponse.data.oportunidade.id;

    // 4. Criar proposta para a oportunidade
    const propostaData = {
      oportunidade_id: oportunidadeId,
      cliente_id: 'cliente-001',
      valor_total: 150000,
      itens: [
        {
          id: 'item-1',
          descricao: 'Serviço Completo',
          quantidade: 1,
          valor_unitario: 150000,
          valor_total: 150000,
        },
      ],
    };
    const propostaResponse = await apiClient.post('/crm/propostas', propostaData);
    expect(propostaResponse.status).toBe(201);
    const propostaId = propostaResponse.data.id;

    // 5. Enviar proposta
    const enviarResponse = await apiClient.post(`/crm/propostas/${propostaId}/enviar`);
    expect(enviarResponse.status).toBe(200);
    expect(enviarResponse.data.status).toBe('enviada');

    // 6. Aprovar proposta
    const aprovarResponse = await apiClient.post(`/crm/propostas/${propostaId}/aprovar`);
    expect(aprovarResponse.status).toBe(200);
    expect(aprovarResponse.data.status).toBe('aprovada');
    expect(aprovarResponse.data).toHaveProperty('data_aprovacao');
  });

  it('deve realizar fluxo de perda: Oportunidade → Perdida', async () => {
    // Perder oportunidade
    const response = await apiClient.post('/crm/oportunidades/oportunidade-001/perder', {
      motivo: 'Concorrente com preço menor',
    });

    expect(response.status).toBe(200);
    expect(response.data.etapa).toBe('perdido');
    expect(response.data.probabilidade).toBe(0);
    expect(response.data.motivo_perda).toBe('Concorrente com preço menor');
  });
});
