'use client';

import { useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Calendar,
  Mail,
  Phone,
  Globe,
  Download,
  Printer,
  Share2,
  CheckCircle,
  Clock,
} from 'lucide-react';
import { Button } from '@/core/components/ui/Button';
import { Badge } from '@/core/components/ui/Badge';
import type { Proposal } from '../../types';

interface ProposalPreviewProps {
  proposal: Proposal;
  companyInfo?: CompanyInfo;
  onDownload?: () => void;
  onPrint?: () => void;
  onShare?: () => void;
}

interface CompanyInfo {
  name: string;
  logo?: string;
  address: string;
  phone: string;
  email: string;
  website: string;
  cnpj: string;
}

const defaultCompanyInfo: CompanyInfo = {
  name: 'Conecta PRO',
  logo: '/logo.png',
  address: 'Av. Paulista, 1000 - Sao Paulo, SP',
  phone: '(11) 3000-0000',
  email: 'contato@conectapro.com.br',
  website: 'www.conectapro.com.br',
  cnpj: '00.000.000/0001-00',
};

const statusConfig: Record<Proposal['status'], { label: string; variant: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'; icon: React.ElementType }> = {
  draft: { label: 'Rascunho', variant: 'default', icon: Clock },
  sent: { label: 'Enviada', variant: 'info', icon: Mail },
  viewed: { label: 'Visualizada', variant: 'primary', icon: Clock },
  accepted: { label: 'Aceita', variant: 'success', icon: CheckCircle },
  rejected: { label: 'Rejeitada', variant: 'danger', icon: Clock },
  expired: { label: 'Expirada', variant: 'warning', icon: Clock },
};

export function ProposalPreview({
  proposal,
  companyInfo = defaultCompanyInfo,
  onDownload,
  onPrint,
  onShare,
}: ProposalPreviewProps) {
  const previewRef = useRef<HTMLDivElement>(null);
  const statusInfo = statusConfig[proposal.status];
  const StatusIcon = statusInfo.icon;

  const formatCurrency = (value: number, currency: 'BRL' | 'USD') => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
  };

  // Extrair produtos de todas as secoes
  const allProducts = proposal.sections
    .filter(s => s.products && s.products.length > 0)
    .flatMap(s => s.products || []);

  // Calcular subtotal e total
  const subtotal = allProducts.reduce((acc, p) => acc + p.total, 0);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-6 p-4 bg-white rounded-lg shadow-sm border"
      >
        <div className="flex items-center gap-3">
          <Badge variant={statusInfo.variant} size="lg">
            <StatusIcon className="w-4 h-4 mr-1" />
            {statusInfo.label}
          </Badge>
          <span className="text-sm text-gray-500">
            Versao {proposal.version}
          </span>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onPrint}
            leftIcon={<Printer className="w-4 h-4" />}
          >
            Imprimir
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onDownload}
            leftIcon={<Download className="w-4 h-4" />}
          >
            PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onShare}
            leftIcon={<Share2 className="w-4 h-4" />}
          >
            Compartilhar
          </Button>
        </div>
      </motion.div>

      {/* Preview Document */}
      <motion.div
        ref={previewRef}
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-lg shadow-lg border overflow-hidden"
        style={{ fontFamily: 'system-ui, sans-serif' }}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-conecta-escuro to-conecta-medio p-8 text-white">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">{companyInfo.name}</h1>
                  <p className="text-white/70 text-sm">CNPJ: {companyInfo.cnpj}</p>
                </div>
              </div>
              <div className="space-y-1 text-sm text-white/80">
                <p className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {companyInfo.email}
                </p>
                <p className="flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  {companyInfo.phone}
                </p>
                <p className="flex items-center gap-2">
                  <Globe className="w-4 h-4" />
                  {companyInfo.website}
                </p>
              </div>
            </div>
            <div className="text-right">
              <h2 className="text-3xl font-bold mb-2">PROPOSTA</h2>
              <p className="text-white/70">#{proposal.id.slice(0, 8).toUpperCase()}</p>
            </div>
          </div>
        </div>

        {/* Info Bar */}
        <div className="bg-gray-50 px-8 py-4 border-b grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Data de Emissao</p>
            <p className="font-medium">{formatDate(proposal.createdAt)}</p>
          </div>
          <div>
            <p className="text-gray-500">Valido Ate</p>
            <p className="font-medium">{formatDate(proposal.validUntil)}</p>
          </div>
          <div className="text-right">
            <p className="text-gray-500">Moeda</p>
            <p className="font-medium">{proposal.currency}</p>
          </div>
        </div>

        {/* Content */}
        <div className="p-8">
          {/* Title */}
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {proposal.title}
            </h3>
            <div className="flex items-center gap-2 text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>Proposta comercial para prestacao de servicos</span>
            </div>
          </div>

          {/* Sections */}
          <div className="space-y-8">
            {proposal.sections.map((section, index) => (
              <motion.div
                key={section.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {section.type === 'intro' && section.content && (
                  <div className="prose max-w-none">
                    <h4 className="text-lg font-semibold text-gray-900 mb-3">
                      {section.title}
                    </h4>
                    <p className="text-gray-600 whitespace-pre-wrap">
                      {section.content}
                    </p>
                  </div>
                )}

                {section.type === 'products' && section.products && section.products.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">
                      {section.title}
                    </h4>
                    <div className="border rounded-lg overflow-hidden">
                      <table className="w-full">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                              Descricao
                            </th>
                            <th className="px-4 py-3 text-center text-sm font-medium text-gray-600 w-20">
                              Qtd
                            </th>
                            <th className="px-4 py-3 text-right text-sm font-medium text-gray-600 w-32">
                              Valor Unit.
                            </th>
                            <th className="px-4 py-3 text-center text-sm font-medium text-gray-600 w-20">
                              Desc.
                            </th>
                            <th className="px-4 py-3 text-right text-sm font-medium text-gray-600 w-32">
                              Total
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y">
                          {section.products.map((product) => (
                            <tr key={product.id} className="hover:bg-gray-50">
                              <td className="px-4 py-4">
                                <p className="font-medium text-gray-900">{product.name}</p>
                                {product.description && (
                                  <p className="text-sm text-gray-500 mt-1">
                                    {product.description}
                                  </p>
                                )}
                              </td>
                              <td className="px-4 py-4 text-center">
                                {product.quantity}
                              </td>
                              <td className="px-4 py-4 text-right">
                                {formatCurrency(product.unitPrice, proposal.currency)}
                              </td>
                              <td className="px-4 py-4 text-center">
                                {product.discount > 0 ? (
                                  <span className="text-red-500">-{product.discount}%</span>
                                ) : (
                                  '-'
                                )}
                              </td>
                              <td className="px-4 py-4 text-right font-medium">
                                {formatCurrency(product.total, proposal.currency)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {section.type === 'terms' && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-3">
                      {section.title}
                    </h4>
                    <p className="text-gray-600 whitespace-pre-wrap text-sm">
                      {section.content}
                    </p>
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          {/* Totals */}
          <div className="mt-8 flex justify-end">
            <div className="w-80 border rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b">
                <span className="font-medium text-gray-900">Resumo Financeiro</span>
              </div>
              <div className="p-4 space-y-3">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>{formatCurrency(subtotal, proposal.currency)}</span>
                </div>
                {subtotal !== proposal.total && (
                  <div className="flex justify-between text-red-500">
                    <span>Desconto</span>
                    <span>-{formatCurrency(subtotal - proposal.total, proposal.currency)}</span>
                  </div>
                )}
                <div className="flex justify-between pt-3 border-t text-lg font-bold text-conecta-escuro">
                  <span>Total</span>
                  <span>{formatCurrency(proposal.total, proposal.currency)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Signature Area */}
          {proposal.status === 'accepted' && proposal.signedBy && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 p-6 border-2 border-green-200 rounded-lg bg-green-50"
            >
              <div className="flex items-center gap-3 text-green-700">
                <CheckCircle className="w-6 h-6" />
                <div>
                  <p className="font-semibold">Proposta Aceita</p>
                  <p className="text-sm">
                    Assinado por {proposal.signedBy} em {formatDate(proposal.signedAt!)}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Pending Signature */}
          {proposal.status === 'sent' && (
            <div className="mt-8 p-6 border-2 border-dashed border-gray-300 rounded-lg">
              <div className="grid grid-cols-2 gap-8">
                <div className="text-center">
                  <div className="border-b border-gray-300 pb-16 mb-2"></div>
                  <p className="text-sm text-gray-500">{companyInfo.name}</p>
                  <p className="text-xs text-gray-400">Contratada</p>
                </div>
                <div className="text-center">
                  <div className="border-b border-gray-300 pb-16 mb-2"></div>
                  <p className="text-sm text-gray-500">Cliente</p>
                  <p className="text-xs text-gray-400">Contratante</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-8 py-4 border-t text-center text-sm text-gray-500">
          <p>{companyInfo.name} - {companyInfo.address}</p>
          <p className="mt-1">
            Este documento foi gerado eletronicamente e nao requer assinatura fisica.
          </p>
        </div>
      </motion.div>
    </div>
  );
}

// Mock data para demonstracao
// eslint-disable-next-line react-refresh/only-export-components
export const mockProposalForPreview: Proposal = {
  id: 'PROP-2024-001',
  contactId: 'contact-001',
  title: 'Proposta de Servicos de Gestao Condominial',
  status: 'sent',
  sections: [
    {
      id: 'sec-1',
      type: 'intro',
      title: 'Apresentacao',
      content: 'Prezado cliente,\n\nTemos o prazer de apresentar nossa proposta comercial para prestacao de servicos de gestao condominial. Nossa empresa possui mais de 10 anos de experiencia no mercado, atendendo condominios de todos os portes com excelencia e dedicacao.\n\nOs servicos propostos visam atender todas as necessidades do seu condominio, garantindo eficiencia operacional e satisfacao dos moradores.',
      order: 1,
    },
    {
      id: 'sec-2',
      type: 'products',
      title: 'Servicos Propostos',
      content: '',
      order: 2,
      products: [
        { id: 'p1', name: 'Gestao Administrativa Completa', description: 'Administracao geral, assembleias, documentacao', quantity: 1, unitPrice: 5500, discount: 0, total: 5500 },
        { id: 'p2', name: 'Portaria 24h', description: 'Equipe de porteiros treinados', quantity: 1, unitPrice: 18000, discount: 5, total: 17100 },
        { id: 'p3', name: 'Limpeza e Conservacao', description: 'Limpeza diaria de areas comuns', quantity: 1, unitPrice: 8500, discount: 0, total: 8500 },
        { id: 'p4', name: 'Manutencao Predial', description: 'Manutencao preventiva e corretiva', quantity: 1, unitPrice: 6000, discount: 10, total: 5400 },
      ],
    },
    {
      id: 'sec-3',
      type: 'terms',
      title: 'Termos e Condicoes',
      content: '1. Proposta valida por 30 dias a partir da data de emissao.\n2. Pagamento mensal, ate o dia 10 de cada mes.\n3. Contrato com vigencia minima de 12 meses.\n4. Reajuste anual pelo IPCA.\n5. Inicio dos servicos em ate 15 dias uteis apos assinatura.',
      order: 3,
    },
  ],
  total: 36500,
  currency: 'BRL',
  validUntil: '2024-03-15',
  sentAt: '2024-02-15',
  createdBy: 'user-001',
  createdAt: '2024-02-10',
  updatedAt: '2024-02-15',
  comments: [],
  version: 1,
};

export default ProposalPreview;
