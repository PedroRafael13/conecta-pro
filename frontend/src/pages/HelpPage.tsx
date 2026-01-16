'use client';

import { useState } from 'react';
import {
  HelpCircle,
  Book,
  MessageCircle,
  Video,
  FileText,
  Search,
  ChevronRight,
  ExternalLink,
  Mail,
  Phone,
  Clock,
} from 'lucide-react';
import { MainLayout } from '@/layouts/MainLayout';
import { Card, CardHeader, CardBody, Input, Badge } from '@/design-system/components';

const helpCategories = [
  {
    id: 'getting-started',
    icon: Book,
    title: 'Primeiros Passos',
    description: 'Aprenda o basico da plataforma',
    articles: 12,
  },
  {
    id: 'crm',
    icon: MessageCircle,
    title: 'CRM & Vendas',
    description: 'Leads, oportunidades e propostas',
    articles: 18,
  },
  {
    id: 'financial',
    icon: FileText,
    title: 'Financeiro',
    description: 'Contas, fluxo de caixa e cobranca',
    articles: 24,
  },
  {
    id: 'hr',
    icon: Clock,
    title: 'RH & Ponto',
    description: 'Colaboradores, folha e ponto eletronico',
    articles: 15,
  },
];

const popularArticles = [
  { id: 1, title: 'Como criar uma nova proposta comercial', category: 'CRM', views: 1250 },
  { id: 2, title: 'Configurar regras de faturamento automatico', category: 'Financeiro', views: 980 },
  { id: 3, title: 'Integrar sistema de ponto eletronico', category: 'RH', views: 876 },
  { id: 4, title: 'Gerar relatorios personalizados', category: 'Relatorios', views: 754 },
  { id: 5, title: 'Configurar notificacoes por email', category: 'Sistema', views: 623 },
];

const videoTutorials = [
  { id: 1, title: 'Tour completo pela plataforma', duration: '12:34', thumbnail: null },
  { id: 2, title: 'Gerenciando leads e oportunidades', duration: '08:45', thumbnail: null },
  { id: 3, title: 'Configurando o fluxo financeiro', duration: '15:20', thumbnail: null },
];

export function HelpPage() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto">
          <div className="w-16 h-16 bg-accent-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <HelpCircle className="w-8 h-8 text-accent-primary" />
          </div>
          <h1 className="text-3xl font-display font-bold text-text-primary">
            Central de Ajuda
          </h1>
          <p className="text-text-secondary mt-2">
            Encontre respostas, tutoriais e suporte para usar a plataforma
          </p>
        </div>

        {/* Search */}
        <div className="max-w-2xl mx-auto">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-muted" />
            <input
              type="text"
              placeholder="Buscar artigos, tutoriais, FAQs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-bg-secondary border border-border-default rounded-xl text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary"
            />
          </div>
        </div>

        {/* Categories Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {helpCategories.map((category) => (
            <Card
              key={category.id}
              className="group cursor-pointer hover:border-accent-primary/50 transition-all"
            >
              <CardBody className="p-6">
                <div className="w-12 h-12 bg-accent-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-accent-primary/20 transition-colors">
                  <category.icon className="w-6 h-6 text-accent-primary" />
                </div>
                <h3 className="font-semibold text-text-primary mb-1">{category.title}</h3>
                <p className="text-sm text-text-secondary mb-3">{category.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-muted">{category.articles} artigos</span>
                  <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-accent-primary transition-colors" />
                </div>
              </CardBody>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Popular Articles */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader title="Artigos Populares" />
              <CardBody className="p-0">
                <div className="divide-y divide-border-default">
                  {popularArticles.map((article) => (
                    <div
                      key={article.id}
                      className="p-4 hover:bg-bg-tertiary cursor-pointer transition-colors flex items-center justify-between"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-bg-tertiary rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 text-text-muted" />
                        </div>
                        <div>
                          <h4 className="font-medium text-text-primary">{article.title}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="neutral" size="sm">{article.category}</Badge>
                            <span className="text-xs text-text-muted">{article.views} visualizacoes</span>
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-text-muted" />
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Video Tutorials & Contact */}
          <div className="space-y-6">
            {/* Video Tutorials */}
            <Card>
              <CardHeader title="Video Tutoriais" />
              <CardBody className="space-y-3">
                {videoTutorials.map((video) => (
                  <div
                    key={video.id}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-tertiary cursor-pointer transition-colors"
                  >
                    <div className="w-16 h-10 bg-bg-tertiary rounded-lg flex items-center justify-center">
                      <Video className="w-5 h-5 text-text-muted" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-text-primary line-clamp-1">{video.title}</p>
                      <p className="text-xs text-text-muted">{video.duration}</p>
                    </div>
                  </div>
                ))}
              </CardBody>
            </Card>

            {/* Contact Support */}
            <Card className="bg-gradient-to-br from-accent-primary/10 to-accent-secondary/10 border-accent-primary/20">
              <CardBody className="p-6 text-center">
                <div className="w-12 h-12 bg-accent-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MessageCircle className="w-6 h-6 text-accent-primary" />
                </div>
                <h3 className="font-semibold text-text-primary mb-2">Precisa de Ajuda?</h3>
                <p className="text-sm text-text-secondary mb-4">
                  Nossa equipe esta pronta para ajudar
                </p>
                <div className="space-y-2 text-sm">
                  <a
                    href="mailto:suporte@conectaplus.com.br"
                    className="flex items-center justify-center gap-2 text-text-secondary hover:text-accent-primary transition-colors"
                  >
                    <Mail className="w-4 h-4" />
                    suporte@conectaplus.com.br
                  </a>
                  <a
                    href="tel:+551140028922"
                    className="flex items-center justify-center gap-2 text-text-secondary hover:text-accent-primary transition-colors"
                  >
                    <Phone className="w-4 h-4" />
                    (11) 4002-8922
                  </a>
                </div>
              </CardBody>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

export default HelpPage;
