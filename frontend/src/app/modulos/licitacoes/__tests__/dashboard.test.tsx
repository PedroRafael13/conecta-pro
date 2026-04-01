/**
 * Testes unitários do Dashboard de Licitações
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { render } from '@/test/helpers/test-utils';
import LicitacoesPage from '../page';
import * as tendersHooks from '@/hooks/bidding/useTenders';
import * as proposalsHooks from '@/hooks/bidding/useProposals';
import * as contractsHooks from '@/hooks/bidding/useContracts';

// Mock dos hooks
vi.mock('@/hooks/bidding/useTenders');
vi.mock('@/hooks/bidding/useProposals');
vi.mock('@/hooks/bidding/useContracts');

describe('Dashboard de Licitações', () => {
  beforeEach(() => {
    // Reset mocks antes de cada teste
    vi.clearAllMocks();
  });

  describe('Renderização básica', () => {
    it('deve renderizar o título e descrição', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 0 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 0 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 0, certidoes_pendentes: 0 },
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert
      expect(screen.getByText('Licitações')).toBeInTheDocument();
      expect(
        screen.getByText(
          'Gestão de licitações públicas, editais, propostas e contratos'
        )
      ).toBeInTheDocument();
    });

    it('deve renderizar os 4 cards de KPIs', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 5 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 3 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 12, certidoes_pendentes: 2 },
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert
      expect(screen.getByText('Editais Abertos')).toBeInTheDocument();
      expect(screen.getByText('Propostas em Análise')).toBeInTheDocument();
      expect(screen.getByText('Contratos Vigentes')).toBeInTheDocument();
      expect(screen.getByText('Certidões Pendentes')).toBeInTheDocument();
    });

    it('deve renderizar os 3 cards de acesso rápido', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 0 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 0 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 0, certidoes_pendentes: 0 },
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert
      expect(screen.getByText('Editais Recentes')).toBeInTheDocument();
      expect(screen.getByText('Minhas Propostas')).toBeInTheDocument();
      expect(screen.getByText('Contratos Ativos')).toBeInTheDocument();
    });
  });

  describe('Valores dos KPIs', () => {
    it('deve exibir o número correto de editais abertos', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 15 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 0 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 0, certidoes_pendentes: 0 },
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert
      expect(screen.getByText('Editais Abertos')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
    });

    it('deve exibir o número correto de propostas em análise', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 0 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 7 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 0, certidoes_pendentes: 0 },
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert
      expect(screen.getByText('Propostas em Análise')).toBeInTheDocument();
      expect(screen.getByText('7')).toBeInTheDocument();
    });

    it('deve exibir o número correto de contratos vigentes', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 0 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 0 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 20, certidoes_pendentes: 0 },
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert
      expect(screen.getByText('Contratos Vigentes')).toBeInTheDocument();
      expect(screen.getByText('20')).toBeInTheDocument();
    });

    it('deve exibir o número correto de certidões pendentes', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 0 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 0 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 0, certidoes_pendentes: 4 },
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert
      expect(screen.getByText('Certidões Pendentes')).toBeInTheDocument();
      expect(screen.getByText('4')).toBeInTheDocument();
    });

    it('deve exibir 0 quando não há dados', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: undefined,
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: undefined,
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: undefined,
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert
      const cards = screen.getAllByText('0');
      expect(cards).toHaveLength(4); // 4 KPIs com valor 0
    });
  });

  describe('Links de navegação', () => {
    beforeEach(() => {
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 5 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 3 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 12, certidoes_pendentes: 2 },
      } as never);
    });

    it('deve ter link correto para editais', () => {
      // Act
      render(<LicitacoesPage />);

      // Assert
      const editaisLink = screen
        .getByText('Editais Abertos')
        .closest('a');
      expect(editaisLink).toHaveAttribute(
        'href',
        '/modulos/licitacoes/editais'
      );
    });

    it('deve ter link correto para propostas', () => {
      // Act
      render(<LicitacoesPage />);

      // Assert
      const propostasLink = screen
        .getByText('Propostas em Análise')
        .closest('a');
      expect(propostasLink).toHaveAttribute(
        'href',
        '/modulos/licitacoes/propostas'
      );
    });

    it('deve ter link correto para contratos', () => {
      // Act
      render(<LicitacoesPage />);

      // Assert
      const contratosLink = screen
        .getByText('Contratos Vigentes')
        .closest('a');
      expect(contratosLink).toHaveAttribute(
        'href',
        '/modulos/licitacoes/contratos'
      );
    });

    it('deve ter link correto para certidões', () => {
      // Act
      render(<LicitacoesPage />);

      // Assert
      const certidoesLink = screen
        .getByText('Certidões Pendentes')
        .closest('a');
      expect(certidoesLink).toHaveAttribute(
        'href',
        '/modulos/licitacoes/certidoes'
      );
    });

    it('deve ter links "Ver todos" nos cards de acesso rápido', () => {
      // Act
      render(<LicitacoesPage />);

      // Assert
      expect(screen.getByText('Ver todos os editais →')).toBeInTheDocument();
      expect(screen.getByText('Ver propostas →')).toBeInTheDocument();
      expect(screen.getByText('Ver contratos →')).toBeInTheDocument();
    });
  });

  describe('Ícones', () => {
    beforeEach(() => {
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: { total_abertos: 5 },
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: { total: 3 },
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: { vigentes: 12, certidoes_pendentes: 2 },
      } as never);
    });

    it('deve renderizar ícones nos cards de KPI', () => {
      // Act
      render(<LicitacoesPage />);

      // Assert
      // Lucide icons são renderizados como SVGs
      const svgs = document.querySelectorAll('svg');
      expect(svgs.length).toBeGreaterThanOrEqual(4); // Pelo menos 4 ícones dos KPIs
    });
  });

  describe('Loading states', () => {
    it('deve funcionar quando os dados estão carregando', () => {
      // Arrange
      vi.spyOn(tendersHooks, 'useTendersDashboard').mockReturnValue({
        data: undefined,
        isLoading: true,
      } as never);
      vi.spyOn(proposalsHooks, 'useEstatisticasPropostas').mockReturnValue({
        data: undefined,
        isLoading: true,
      } as never);
      vi.spyOn(contractsHooks, 'useContractsDashboard').mockReturnValue({
        data: undefined,
        isLoading: true,
      } as never);

      // Act
      render(<LicitacoesPage />);

      // Assert - deve mostrar 0 enquanto carrega
      const cards = screen.getAllByText('0');
      expect(cards).toHaveLength(4);
    });
  });
});
