'use client';

import { motion } from 'framer-motion';
import {
  Building2,
  MapPin,
  Mail,
  Phone,
  Globe,
  Star,
  BadgeCheck,
  Clock,
  Briefcase,
  ChevronRight,
  Award,
  ExternalLink,
} from 'lucide-react';
import { Badge } from '@/core/components/ui/Badge';
import { Button } from '@/core/components/ui/Button';
import type { ServiceProvider } from '../../types';

interface ProviderCardProps {
  provider: ServiceProvider;
  onViewProfile?: (provider: ServiceProvider) => void;
  onContact?: (provider: ServiceProvider) => void;
  servicesCount?: number;
  variant?: 'default' | 'compact' | 'detailed';
}

export function ProviderCard({
  provider,
  onViewProfile,
  onContact,
  servicesCount = 0,
  variant = 'default',
}: ProviderCardProps) {
  const formatResponseTime = (hours: number) => {
    if (hours < 24) {
      return `${hours}h`;
    }
    const days = Math.round(hours / 24);
    return `${days} dia${days > 1 ? 's' : ''}`;
  };

  if (variant === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ x: 4 }}
        className="flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-100 hover:shadow-md transition-all cursor-pointer"
        onClick={() => onViewProfile?.(provider)}
      >
        {/* Avatar */}
        {provider.avatar ? (
          <img
            src={provider.avatar}
            alt={provider.companyName}
            className="w-12 h-12 rounded-full object-cover"
          />
        ) : (
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-conecta-escuro to-conecta-medio flex items-center justify-center">
            <span className="text-white font-bold text-lg">
              {provider.companyName.charAt(0)}
            </span>
          </div>
        )}

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-medium text-gray-900 truncate">
              {provider.companyName}
            </h4>
            {provider.isVerified && (
              <BadgeCheck className="w-4 h-4 text-blue-500 flex-shrink-0" />
            )}
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
              <span>{provider.rating.toFixed(1)}</span>
            </div>
            <div className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              <span className="truncate">{provider.location}</span>
            </div>
          </div>
        </div>

        <ChevronRight className="w-5 h-5 text-gray-400" />
      </motion.div>
    );
  }

  if (variant === 'detailed') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-card border border-gray-100 overflow-hidden"
      >
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-conecta-escuro to-conecta-medio text-white">
          <div className="flex items-start gap-4">
            {provider.avatar ? (
              <img
                src={provider.avatar}
                alt={provider.companyName}
                className="w-20 h-20 rounded-xl object-cover border-2 border-white/20"
              />
            ) : (
              <div className="w-20 h-20 rounded-xl bg-white/20 flex items-center justify-center">
                <Building2 className="w-8 h-8 text-white" />
              </div>
            )}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-xl font-bold">{provider.companyName}</h3>
                {provider.isVerified && (
                  <Badge variant="success" size="sm">
                    <BadgeCheck className="w-3 h-3 mr-1" />
                    Verificado
                  </Badge>
                )}
              </div>
              <p className="text-white/80 text-sm">{provider.contactName}</p>
              <div className="flex items-center gap-4 mt-3 text-sm text-white/70">
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {provider.location}
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  Responde em ~{formatResponseTime(provider.responseTime)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 divide-x border-b">
          <div className="p-4 text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
              <span className="text-xl font-bold text-gray-900">
                {provider.rating.toFixed(1)}
              </span>
            </div>
            <p className="text-sm text-gray-500">Avaliacao</p>
          </div>
          <div className="p-4 text-center">
            <div className="text-xl font-bold text-gray-900 mb-1">
              {provider.completedProjects}
            </div>
            <p className="text-sm text-gray-500">Projetos</p>
          </div>
          <div className="p-4 text-center">
            <div className="text-xl font-bold text-gray-900 mb-1">
              {servicesCount}
            </div>
            <p className="text-sm text-gray-500">Servicos</p>
          </div>
        </div>

        {/* Description */}
        {provider.description && (
          <div className="p-6 border-b">
            <p className="text-gray-600">{provider.description}</p>
          </div>
        )}

        {/* Certifications */}
        {provider.certifications.length > 0 && (
          <div className="p-6 border-b">
            <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
              <Award className="w-4 h-4" />
              Certificacoes
            </h4>
            <div className="flex flex-wrap gap-2">
              {provider.certifications.map((cert, index) => (
                <Badge key={index} variant="default">
                  {cert}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Contact Info */}
        <div className="p-6 bg-gray-50 space-y-3">
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <Mail className="w-4 h-4 text-gray-400" />
            <a href={`mailto:${provider.email}`} className="hover:text-conecta-escuro">
              {provider.email}
            </a>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <Phone className="w-4 h-4 text-gray-400" />
            <a href={`tel:${provider.phone}`} className="hover:text-conecta-escuro">
              {provider.phone}
            </a>
          </div>
          {provider.website && (
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <Globe className="w-4 h-4 text-gray-400" />
              <a
                href={provider.website}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-conecta-escuro flex items-center gap-1"
              >
                {provider.website.replace(/^https?:\/\//, '')}
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="p-6 flex gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => onViewProfile?.(provider)}
          >
            Ver Perfil Completo
          </Button>
          <Button
            className="flex-1"
            onClick={() => onContact?.(provider)}
          >
            Entrar em Contato
          </Button>
        </div>
      </motion.div>
    );
  }

  // Default variant
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      className="bg-white rounded-xl shadow-card border border-gray-100 overflow-hidden hover:shadow-lg transition-all group"
    >
      {/* Header */}
      <div className="p-6">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          {provider.avatar ? (
            <img
              src={provider.avatar}
              alt={provider.companyName}
              className="w-16 h-16 rounded-xl object-cover"
            />
          ) : (
            <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-conecta-escuro to-conecta-medio flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-900 truncate group-hover:text-conecta-escuro transition-colors">
                {provider.companyName}
              </h3>
              {provider.isVerified && (
                <BadgeCheck className="w-5 h-5 text-blue-500 flex-shrink-0" />
              )}
            </div>

            <p className="text-sm text-gray-600 mb-2">{provider.contactName}</p>

            <div className="flex items-center gap-3 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                <span className="font-medium text-gray-900">{provider.rating.toFixed(1)}</span>
              </div>
              <div className="flex items-center gap-1">
                <Briefcase className="w-4 h-4" />
                <span>{provider.completedProjects} projetos</span>
              </div>
            </div>
          </div>
        </div>

        {/* Description */}
        {provider.description && (
          <p className="text-sm text-gray-600 mt-4 line-clamp-2">
            {provider.description}
          </p>
        )}
      </div>

      {/* Services Offered */}
      {servicesCount > 0 && (
        <div className="px-6 pb-4">
          <Badge variant="primary">
            {servicesCount} servico{servicesCount > 1 ? 's' : ''} disponivel{servicesCount > 1 ? 'is' : ''}
          </Badge>
        </div>
      )}

      {/* Certifications Preview */}
      {provider.certifications.length > 0 && (
        <div className="px-6 pb-4 flex flex-wrap gap-1">
          {provider.certifications.slice(0, 3).map((cert, index) => (
            <Badge key={index} variant="default" size="sm">
              {cert}
            </Badge>
          ))}
          {provider.certifications.length > 3 && (
            <Badge variant="default" size="sm">
              +{provider.certifications.length - 3}
            </Badge>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <MapPin className="w-4 h-4" />
          <span>{provider.location}</span>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onViewProfile?.(provider)}
          rightIcon={<ChevronRight className="w-4 h-4" />}
        >
          Ver Perfil
        </Button>
      </div>
    </motion.div>
  );
}

// Mock data para demonstracao
// eslint-disable-next-line react-refresh/only-export-components
export const mockProviders: ServiceProvider[] = [
  {
    id: 'prov-001',
    companyName: 'ServiPro Manutencao',
    contactName: 'Carlos Silva',
    email: 'contato@servipro.com.br',
    phone: '(11) 99999-0001',
    avatar: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=200',
    description: 'Especialistas em manutencao predial com mais de 15 anos de experiencia no mercado. Atendemos condominios residenciais e comerciais em toda Grande Sao Paulo.',
    location: 'Sao Paulo, SP',
    website: 'https://servipro.com.br',
    certifications: ['ISO 9001', 'CREA', 'NR-35'],
    portfolio: [],
    rating: 4.8,
    completedProjects: 156,
    responseTime: 2,
    isVerified: true,
  },
  {
    id: 'prov-002',
    companyName: 'LimpMax Servicos',
    contactName: 'Ana Santos',
    email: 'contato@limpmax.com.br',
    phone: '(11) 99999-0002',
    description: 'Servicos de limpeza profissional para condominios, com foco em sustentabilidade e produtos ecologicos.',
    location: 'Sao Paulo, SP',
    certifications: ['ISO 14001', 'Selo Verde'],
    portfolio: [],
    rating: 4.6,
    completedProjects: 234,
    responseTime: 4,
    isVerified: true,
  },
  {
    id: 'prov-003',
    companyName: 'PortaSeg Vigilancia',
    contactName: 'Roberto Lima',
    email: 'comercial@portaseg.com.br',
    phone: '(11) 99999-0003',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200',
    description: 'Seguranca patrimonial e servicos de portaria 24h com equipe treinada e tecnologia de ponta.',
    location: 'Sao Paulo, SP',
    website: 'https://portaseg.com.br',
    certifications: ['Alvara de Funcionamento', 'Certificado de Seguranca', 'ISO 27001'],
    portfolio: [],
    rating: 4.9,
    completedProjects: 78,
    responseTime: 1,
    isVerified: true,
  },
  {
    id: 'prov-004',
    companyName: 'JardinArte Paisagismo',
    contactName: 'Maria Oliveira',
    email: 'contato@jardinarte.com.br',
    phone: '(11) 99999-0004',
    description: 'Criacao e manutencao de jardins e areas verdes. Projetos personalizados para seu condominio.',
    location: 'Sao Paulo, SP',
    certifications: [],
    portfolio: [],
    rating: 4.5,
    completedProjects: 120,
    responseTime: 6,
    isVerified: false,
  },
];

export default ProviderCard;
