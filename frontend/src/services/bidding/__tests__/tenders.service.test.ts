import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  listarEditais,
  buscarEditalPorId,
  criarEdital,
  atualizarEdital,
  removerEdital,
  listarEditaisAbertos,
  listarEditaisPorSegmento,
  marcarParticipacao,
  alterarStatus,
  buscarPNCP,
  sincronizarPNCP,
  getDashboard,
} from '../tenders.service';

vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import api from '@/lib/api';

describe('tenders.service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('listarEditais', () => {
    it('deve listar editais com filtros', async () => {
      const mockResponse = { items: [{ id: '1' }], total: 1 };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarEditais({ uf: 'SP', status: 'aberto' });

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/tenders/', {
        params: { uf: 'SP', status: 'aberto' },
      });
      expect(result).toEqual(mockResponse);
    });

    it('deve listar editais sem filtros', async () => {
      const mockResponse = { items: [], total: 0 };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarEditais();

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/tenders/', {
        params: undefined,
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('buscarEditalPorId', () => {
    it('deve buscar edital por ID', async () => {
      const mockResponse = { id: '1', titulo: 'Edital Teste' };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await buscarEditalPorId('1');

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/tenders/1');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('criarEdital', () => {
    it('deve criar novo edital', async () => {
      const mockPayload = { titulo: 'Novo Edital' };
      const mockResponse = { id: '1', ...mockPayload };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await criarEdital(mockPayload as any);

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/',
        mockPayload
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('atualizarEdital', () => {
    it('deve atualizar edital existente', async () => {
      const mockPayload = { status: 'fechado' };
      const mockResponse = { id: '1', ...mockPayload };
      vi.mocked(api.put).mockResolvedValue({ data: mockResponse });

      const result = await atualizarEdital('1', mockPayload as any);

      expect(api.put).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/1',
        mockPayload
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('removerEdital', () => {
    it('deve remover edital (soft delete)', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: undefined });

      await removerEdital('1');

      expect(api.delete).toHaveBeenCalledWith('/api/v1/bidding/tenders/1');
    });
  });

  describe('listarEditaisAbertos', () => {
    it('deve listar editais abertos', async () => {
      const mockResponse = { items: [{ id: '1', status: 'aberto' }], total: 1 };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarEditaisAbertos({ uf: 'SP' });

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/tenders/abertos', {
        params: { uf: 'SP' },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('listarEditaisPorSegmento', () => {
    it('deve listar editais por segmento', async () => {
      const mockResponse = { items: [{ id: '1', segmento: 'ti' }], total: 1 };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarEditaisPorSegmento('ti', { page: 1 });

      expect(api.get).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/segmento/ti',
        { params: { page: 1 } }
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('marcarParticipacao', () => {
    it('deve marcar participação em edital', async () => {
      const mockParams = { tender_id: '1', participando: true };
      const mockResponse = { id: '1', participando: true };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await marcarParticipacao(mockParams);

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/1/participar',
        { participando: true }
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('alterarStatus', () => {
    it('deve alterar status de edital', async () => {
      const mockParams = { tender_id: '1', novo_status: 'concluido' };
      const mockResponse = { id: '1', status: 'concluido' };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await alterarStatus(mockParams);

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/1/status',
        { novo_status: 'concluido' }
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('buscarPNCP', () => {
    it('deve buscar editais no PNCP', async () => {
      const mockParams = { uf: 'SP', modalidade: 'pregao' };
      const mockResponse = { total: 10, items: [] };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await buscarPNCP(mockParams);

      expect(api.get).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/pncp/buscar',
        { params: mockParams }
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('sincronizarPNCP', () => {
    it('deve sincronizar editais com PNCP', async () => {
      const mockResponse = { message: 'Sincronizado', total_sincronizado: 5 };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await sincronizarPNCP({ uf: 'SP', dias_retroativos: 7 });

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/sync-pncp',
        { uf: 'SP', dias_retroativos: 7 }
      );
      expect(result).toEqual(mockResponse);
    });

    it('deve sincronizar sem parâmetros', async () => {
      const mockResponse = { message: 'Sincronizado', total_sincronizado: 10 };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await sincronizarPNCP();

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/sync-pncp',
        undefined
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getDashboard', () => {
    it('deve retornar dashboard de editais', async () => {
      const mockResponse = { total_editais: 100, abertos: 20 };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await getDashboard({ uf: 'SP', periodo_dias: 30 });

      expect(api.get).toHaveBeenCalledWith(
        '/api/v1/bidding/tenders/dashboard',
        { params: { uf: 'SP', periodo_dias: 30 } }
      );
      expect(result).toEqual(mockResponse);
    });
  });
});
