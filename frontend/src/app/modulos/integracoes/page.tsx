'use client';

import { Plug, Key, Webhook, FileText, RefreshCw, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
;
import { useRouter } from 'next/navigation';
import {
  useIntegrationDashboard,
  useConnectors,
  useAPIKeys,
  useWebhooks,
} from '@/hooks/integrations';

const subPages = [
  {
    title: 'Conectores',
    description: 'Gerenciar conectores externos e integrações com sistemas terceiros',
    href: '/modulos/integracoes/conectores',
    icon: Plug,
    color: 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-950',
  },
  {
    title: 'API Keys',
    description: 'Criar e gerenciar chaves de acesso para APIs externas',
    href: '/modulos/integracoes/api-keys',
    icon: Key,
    color: 'text-amber-600 bg-amber-50 dark:text-amber-400 dark:bg-amber-950',
  },
  {
    title: 'Webhooks',
    description: 'Configurar webhooks para automações e notificações em tempo real',
    href: '/modulos/integracoes/webhooks',
    icon: Webhook,
    color: 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-950',
  },
  {
    title: 'Logs',
    description: 'Visualizar logs de requisições, erros e eventos de integração',
    href: '/modulos/integracoes/logs',
    icon: FileText,
    color: 'text-purple-600 bg-purple-50 dark:text-purple-400 dark:bg-purple-950',
  },
  {
    title: 'Sincronização',
    description: 'Acompanhar e gerenciar filas de sincronização de dados',
    href: '/modulos/integracoes/sync',
    icon: RefreshCw,
    color: 'text-cyan-600 bg-cyan-50 dark:text-cyan-400 dark:bg-cyan-950',
  },
];

export default function IntegracoesPage() {
  const router = useRouter();
  const { data: dashboard, isLoading: dashboardLoading } = useIntegrationDashboard();
  const { data: connectorsData, isLoading: connectorsLoading } = useConnectors();
  const { data: apiKeysData, isLoading: apiKeysLoading } = useAPIKeys();
  const { data: webhooksData, isLoading: webhooksLoading } = useWebhooks();

  const isLoading = dashboardLoading || connectorsLoading || apiKeysLoading || webhooksLoading;

  // Contagens derivadas dos hooks com optional chaining
  const activeConnectors =
    dashboard?.active_connectors ??
    (Array.isArray(connectorsData) ? connectorsData.filter((c: any) => c.is_active || c.ativo).length : connectorsData?.items?.filter((c: any) => c.is_active || c.ativo)?.length ?? 0);

  const totalApiKeys =
    dashboard?.total_api_keys ??
    (Array.isArray(apiKeysData) ? apiKeysData.length : apiKeysData?.items?.length ?? apiKeysData?.total ?? 0);

  const totalWebhooks =
    dashboard?.total_webhooks ??
    (Array.isArray(webhooksData) ? webhooksData.length : webhooksData?.items?.length ?? webhooksData?.total ?? 0);

  const recentErrors = dashboard?.recent_errors ?? dashboard?.errors_count ?? 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Plug className="h-6 w-6" />
            Integrações
          </h1>
          <p className="text-muted-foreground">
            Gestão de conectores, APIs e webhooks
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conectores Ativos</CardTitle>
            <Plug className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            ) : (
              <div className="text-2xl font-bold text-blue-600">
                {activeConnectors}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Keys</CardTitle>
            <Key className="h-4 w-4 text-amber-600" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            ) : (
              <div className="text-2xl font-bold text-amber-600">
                {totalApiKeys}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Webhooks</CardTitle>
            <Webhook className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            ) : (
              <div className="text-2xl font-bold text-green-600">
                {totalWebhooks}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Erros Recentes</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            ) : (
              <div className={`text-2xl font-bold ${recentErrors > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {recentErrors}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Sub-pages Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {subPages.map((page) => (
          <Card
            key={page.href}
            className="hover:shadow-md transition-shadow cursor-pointer h-full"
            onClick={() => router.push(page.href)}
          >
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${page.color}`}>
                  <page.icon className="h-5 w-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm">{page.title}</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {page.description}
                  </p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-1" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
