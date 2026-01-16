'use client';

import { motion } from 'framer-motion';
import {
  Star,
  MapPin,
  Clock,
  BadgeCheck,
  ShoppingCart,
  Heart,
  ExternalLink,
  Sparkles,
} from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/core/components/ui/Badge';
import { Button } from '@/core/components/ui/Button';
import type { MarketplaceService } from '../../types';

interface ServiceCardProps {
  service: MarketplaceService;
  onRequestQuote?: (service: MarketplaceService) => void;
  onViewDetails?: (service: MarketplaceService) => void;
  onFavorite?: (service: MarketplaceService) => void;
  isFavorite?: boolean;
  variant?: 'default' | 'compact' | 'horizontal';
}

export function ServiceCard({
  service,
  onRequestQuote,
  onViewDetails,
  onFavorite,
  isFavorite = false,
  variant = 'default',
}: ServiceCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const formatCurrency = (value: number, currency: 'BRL' | 'USD') => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency,
    }).format(value);
  };

  const getFirstPricing = () => {
    const first = service.pricing[0];
    if (!first) return null;

    const periodLabels: Record<string, string> = {
      hour: '/hora',
      day: '/dia',
      week: '/semana',
      month: '/mes',
      project: '/projeto',
    };

    return {
      price: formatCurrency(first.price, first.currency),
      period: first.period ? periodLabels[first.period] : '',
    };
  };

  const pricing = getFirstPricing();

  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ y: -4 }}
        className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all cursor-pointer"
        onClick={() => onViewDetails?.(service)}
      >
        <div className="relative h-32">
          {service.images[0] ? (
            <img
              src={service.images[0]}
              alt={service.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-conecta-escuro to-conecta-medio flex items-center justify-center">
              <ShoppingCart className="w-8 h-8 text-white/50" />
            </div>
          )}
          {service.isPremium && (
            <div className="absolute top-2 left-2">
              <Badge variant="orange" size="sm">
                <Sparkles className="w-3 h-3 mr-1" />
                Premium
              </Badge>
            </div>
          )}
        </div>
        <div className="p-3">
          <h4 className="font-medium text-gray-900 text-sm line-clamp-1">
            {service.title}
          </h4>
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center gap-1">
              <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
              <span className="text-xs font-medium">{service.rating.toFixed(1)}</span>
            </div>
            {pricing && (
              <span className="text-sm font-bold text-conecta-escuro">
                {pricing.price}
              </span>
            )}
          </div>
        </div>
      </motion.div>
    );
  }

  if (variant === 'horizontal') {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        whileHover={{ x: 4 }}
        className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all flex"
      >
        <div className="relative w-48 h-36 flex-shrink-0">
          {service.images[0] ? (
            <img
              src={service.images[0]}
              alt={service.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-conecta-escuro to-conecta-medio flex items-center justify-center">
              <ShoppingCart className="w-8 h-8 text-white/50" />
            </div>
          )}
          {service.isPremium && (
            <div className="absolute top-2 left-2">
              <Badge variant="orange" size="sm">
                <Sparkles className="w-3 h-3 mr-1" />
                Premium
              </Badge>
            </div>
          )}
        </div>

        <div className="flex-1 p-4 flex flex-col">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-gray-900 line-clamp-1">
                {service.title}
              </h3>
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                {service.description}
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFavorite?.(service);
              }}
              className={`p-1 rounded-full transition-colors ${
                isFavorite ? 'text-red-500' : 'text-gray-400 hover:text-red-500'
              }`}
            >
              <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
            </button>
          </div>

          <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
              <span className="font-medium">{service.rating.toFixed(1)}</span>
              <span>({service.reviewCount})</span>
            </div>
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              <span>{service.provider.location}</span>
            </div>
          </div>

          <div className="flex items-center justify-between mt-auto pt-3">
            {pricing && (
              <div>
                <span className="text-lg font-bold text-conecta-escuro">
                  {pricing.price}
                </span>
                <span className="text-sm text-gray-500">{pricing.period}</span>
              </div>
            )}
            <Button
              size="sm"
              onClick={() => onRequestQuote?.(service)}
              leftIcon={<ShoppingCart className="w-4 h-4" />}
            >
              Solicitar
            </Button>
          </div>
        </div>
      </motion.div>
    );
  }

  // Default variant
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="bg-white rounded-xl shadow-card border border-gray-100 overflow-hidden hover:shadow-lg transition-all group"
    >
      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        {service.images[0] ? (
          <motion.img
            src={service.images[0]}
            alt={service.title}
            className="w-full h-full object-cover"
            animate={{ scale: isHovered ? 1.05 : 1 }}
            transition={{ duration: 0.3 }}
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-conecta-escuro to-conecta-medio flex items-center justify-center">
            <ShoppingCart className="w-12 h-12 text-white/50" />
          </div>
        )}

        {/* Overlay on hover */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered ? 1 : 0 }}
          className="absolute inset-0 bg-black/40 flex items-center justify-center gap-2"
        >
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onViewDetails?.(service)}
            leftIcon={<ExternalLink className="w-4 h-4" />}
          >
            Ver Detalhes
          </Button>
        </motion.div>

        {/* Badges */}
        <div className="absolute top-3 left-3 flex gap-2">
          {service.isPremium && (
            <Badge variant="orange" size="sm">
              <Sparkles className="w-3 h-3 mr-1" />
              Premium
            </Badge>
          )}
          {service.provider.isVerified && (
            <Badge variant="success" size="sm">
              <BadgeCheck className="w-3 h-3 mr-1" />
              Verificado
            </Badge>
          )}
        </div>

        {/* Favorite Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onFavorite?.(service);
          }}
          className={`
            absolute top-3 right-3 p-2 rounded-full bg-white/90 backdrop-blur-sm
            transition-all shadow-sm
            ${isFavorite ? 'text-red-500' : 'text-gray-400 hover:text-red-500'}
          `}
        >
          <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
        </button>

        {/* Category Badge */}
        <div className="absolute bottom-3 left-3">
          <Badge variant="default" size="sm" className="bg-white/90 backdrop-blur-sm">
            {service.category}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Provider Info */}
        <div className="flex items-center gap-2 mb-3">
          {service.provider.avatar ? (
            <img
              src={service.provider.avatar}
              alt={service.provider.companyName}
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-conecta-escuro/10 flex items-center justify-center">
              <span className="text-sm font-medium text-conecta-escuro">
                {service.provider.companyName.charAt(0)}
              </span>
            </div>
          )}
          <span className="text-sm text-gray-600 line-clamp-1">
            {service.provider.companyName}
          </span>
        </div>

        {/* Title & Description */}
        <h3 className="font-semibold text-gray-900 line-clamp-2 mb-2 group-hover:text-conecta-escuro transition-colors">
          {service.title}
        </h3>
        <p className="text-sm text-gray-600 line-clamp-2 mb-4">
          {service.description}
        </p>

        {/* Stats */}
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            <span className="font-medium text-gray-900">{service.rating.toFixed(1)}</span>
            <span>({service.reviewCount})</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>~{service.provider.responseTime}h</span>
          </div>
        </div>

        {/* Price & Action */}
        <div className="flex items-center justify-between pt-4 border-t">
          {pricing ? (
            <div>
              <span className="text-sm text-gray-500">A partir de</span>
              <div>
                <span className="text-xl font-bold text-conecta-escuro">
                  {pricing.price}
                </span>
                <span className="text-sm text-gray-500">{pricing.period}</span>
              </div>
            </div>
          ) : (
            <span className="text-sm text-gray-500">Sob consulta</span>
          )}

          <Button
            onClick={() => onRequestQuote?.(service)}
            leftIcon={<ShoppingCart className="w-4 h-4" />}
          >
            Solicitar
          </Button>
        </div>
      </div>
    </motion.div>
  );
}

// Mock data para demonstracao
// eslint-disable-next-line react-refresh/only-export-components
export const mockServices: MarketplaceService[] = [
  {
    id: 'svc-001',
    providerId: 'prov-001',
    provider: {
      id: 'prov-001',
      companyName: 'ServiPro Manutencao',
      contactName: 'Carlos Silva',
      email: 'contato@servipro.com.br',
      phone: '(11) 99999-0001',
      description: 'Especialistas em manutencao predial',
      location: 'Sao Paulo, SP',
      certifications: ['ISO 9001', 'CREA'],
      portfolio: [],
      rating: 4.8,
      completedProjects: 156,
      responseTime: 2,
      isVerified: true,
    },
    title: 'Manutencao Predial Completa',
    description: 'Servicos completos de manutencao preventiva e corretiva para condominios residenciais e comerciais.',
    category: 'Manutencao',
    subcategory: 'Predial',
    images: ['https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400'],
    pricing: [
      { id: 'p1', name: 'Basico', price: 5000, currency: 'BRL', period: 'month', features: ['Vistorias mensais', 'Reparos simples'] },
      { id: 'p2', name: 'Completo', price: 12000, currency: 'BRL', period: 'month', features: ['Vistorias semanais', 'Todos os reparos', 'Emergencia 24h'] },
    ],
    features: ['Equipe especializada', 'Materiais de qualidade', 'Garantia de servico'],
    tags: ['manutencao', 'predial', 'condominios'],
    rating: 4.8,
    reviewCount: 89,
    isActive: true,
    isPremium: true,
    createdAt: '2024-01-01',
  },
  {
    id: 'svc-002',
    providerId: 'prov-002',
    provider: {
      id: 'prov-002',
      companyName: 'LimpMax Servicos',
      contactName: 'Ana Santos',
      email: 'contato@limpmax.com.br',
      phone: '(11) 99999-0002',
      description: 'Limpeza profissional para condominios',
      location: 'Sao Paulo, SP',
      certifications: ['ISO 14001'],
      portfolio: [],
      rating: 4.6,
      completedProjects: 234,
      responseTime: 4,
      isVerified: true,
    },
    title: 'Limpeza Profissional de Areas Comuns',
    description: 'Servicos de limpeza e conservacao de areas comuns, halls, escadas e elevadores.',
    category: 'Limpeza',
    subcategory: 'Areas Comuns',
    images: ['https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400'],
    pricing: [
      { id: 'p1', name: 'Diario', price: 3500, currency: 'BRL', period: 'month', features: ['Limpeza diaria', 'Segunda a sexta'] },
    ],
    features: ['Produtos ecologicos', 'Equipe uniformizada', 'Supervisao'],
    tags: ['limpeza', 'conservacao', 'areas-comuns'],
    rating: 4.6,
    reviewCount: 145,
    isActive: true,
    isPremium: false,
    createdAt: '2024-01-15',
  },
  {
    id: 'svc-003',
    providerId: 'prov-003',
    provider: {
      id: 'prov-003',
      companyName: 'PortaSeg Vigilancia',
      contactName: 'Roberto Lima',
      email: 'comercial@portaseg.com.br',
      phone: '(11) 99999-0003',
      description: 'Seguranca patrimonial e portaria',
      location: 'Sao Paulo, SP',
      certifications: ['Alvara de Funcionamento', 'Certificado de Seguranca'],
      portfolio: [],
      rating: 4.9,
      completedProjects: 78,
      responseTime: 1,
      isVerified: true,
    },
    title: 'Servico de Portaria 24 Horas',
    description: 'Portaria profissional com controle de acesso, monitoramento e atendimento cordial.',
    category: 'Seguranca',
    subcategory: 'Portaria',
    images: ['https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400'],
    pricing: [
      { id: 'p1', name: '24h', price: 18000, currency: 'BRL', period: 'month', features: ['Portaria 24h', 'Controle de acesso', 'Registro de visitantes'] },
    ],
    features: ['Porteiros treinados', 'Sistema de controle digital', 'Supervisao'],
    tags: ['portaria', 'seguranca', '24h'],
    rating: 4.9,
    reviewCount: 67,
    isActive: true,
    isPremium: true,
    createdAt: '2024-02-01',
  },
  {
    id: 'svc-004',
    providerId: 'prov-004',
    provider: {
      id: 'prov-004',
      companyName: 'JardinArte',
      contactName: 'Maria Oliveira',
      email: 'contato@jardinarte.com.br',
      phone: '(11) 99999-0004',
      description: 'Paisagismo e manutencao de jardins',
      location: 'Sao Paulo, SP',
      certifications: [],
      portfolio: [],
      rating: 4.5,
      completedProjects: 120,
      responseTime: 6,
      isVerified: false,
    },
    title: 'Paisagismo e Jardinagem',
    description: 'Criacao e manutencao de jardins, paisagismo e cuidados com areas verdes.',
    category: 'Jardinagem',
    images: ['https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400'],
    pricing: [
      { id: 'p1', name: 'Manutencao', price: 2500, currency: 'BRL', period: 'month', features: ['Poda', 'Irrigacao', 'Adubacao'] },
    ],
    features: ['Projetos personalizados', 'Plantas de qualidade', 'Manutencao inclusa'],
    tags: ['jardinagem', 'paisagismo', 'areas-verdes'],
    rating: 4.5,
    reviewCount: 43,
    isActive: true,
    isPremium: false,
    createdAt: '2024-02-10',
  },
];

export default ServiceCard;
