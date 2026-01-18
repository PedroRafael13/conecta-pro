'use client';

/**
 * Dashboard de Monitoramento da Integração Sólides
 * Sprint 33: Integration Framework
 *
 * Funcionalidades:
 * - Status de conexão e saúde
 * - Estatísticas de sincronização
 * - Logs de sincronização recentes
 * - Gerenciamento de conflitos
 * - Botões de ação (sync manual)
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Users,
  Building2,
  Briefcase,
  FileWarning,
  Calendar,
  Activity,
  Settings,
  Zap,
  ArrowUpDown,
  ChevronRight,
  ExternalLink,
  AlertCircle,
  CheckCheck,
  X,
  Play,
  Pause,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  Badge,
  StatCard,
  StatGrid,
  DataTable,
  Modal,
  Spinner,
  EmptyState,
  Tooltip,
  Progress,
  type Column,
} from '@/design-system/components';
import { useSolidesIntegration } from './useSolidesIntegration';
import type {
  SyncLog,
  SyncConflict,
  IntegrationStatus,
  ConflictStrategy,
  EntityType,
} from './types';

// ==================== STATUS CONFIGS ====================

const statusConfig: Record<IntegrationStatus, {
  label: string;
  color: 'success' | 'warning' | 'danger' | 'neutral';
  icon: typeof CheckCircle2;
  description: string;
}> = {
  healthy: {
    label: 'Saudável',
    color: 'success',
    icon: CheckCircle2,
    description: 'Integração funcionando normalmente',
  },
  warning: {
    label: 'Atenção',
    color: 'warning',
    icon: AlertTriangle,
    description: 'Existem pendências ou conflitos',
  },
  error: {
    label: 'Erro',
    color: 'danger',
    icon: XCircle,
    description: 'Falha na conexão ou sincronização',
  },
  disconnected: {
    label: 'Desconectado',
    color: 'neutral',
    icon: WifiOff,
    description: 'Integração não configurada',
  },
};

const syncStatusColors: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
  completed: 'success',
  running: 'info',
  pending: 'warning',
  failed: 'danger',
};

const entityIcons: Record<EntityType, typeof Users> = {
  colaboradores: Users,
  departamentos: Building2,
  cargos: Briefcase,
  ocorrencias: FileWarning,
  absenteismos: Calendar,
};

const entityLabels: Record<EntityType, string> = {
  colaboradores: 'Colaboradores',
  departamentos: 'Departamentos',
  cargos: 'Cargos',
  ocorrencias: 'Ocorrências',
  absenteismos: 'Absenteísmos',
};

// ==================== COMPONENTS ====================

interface StatusIndicatorProps {
  status: IntegrationStatus;
  latency?: number | null;
}

function StatusIndicator({ status, latency }: StatusIndicatorProps) {
  const config = statusConfig[status];
  const StatusIcon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex items-center gap-4 p-4 rounded-xl bg-bg-tertiary"
    >
      <div
        className={`relative p-3 rounded-xl ${
          status === 'healthy'
            ? 'bg-success/10'
            : status === 'warning'
            ? 'bg-warning/10'
            : status === 'error'
            ? 'bg-danger/10'
            : 'bg-bg-elevated'
        }`}
      >
        <StatusIcon
          className={`w-6 h-6 ${
            status === 'healthy'
              ? 'text-success'
              : status === 'warning'
              ? 'text-warning'
              : status === 'error'
              ? 'text-danger'
              : 'text-text-muted'
          }`}
        />
        {status === 'healthy' && (
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-success rounded-full animate-pulse" />
        )}
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-text-primary">{config.label}</span>
          <Badge variant={config.color} size="sm">
            {status === 'healthy' ? 'Online' : status === 'error' ? 'Offline' : 'Pendente'}
          </Badge>
        </div>
        <p className="text-sm text-text-secondary mt-0.5">{config.description}</p>
        {latency && (
          <p className="text-xs text-text-muted mt-1">
            Latência: {latency}ms
          </p>
        )}
      </div>
    </motion.div>
  );
}

interface SyncProgressProps {
  synced: number;
  total: number;
  label: string;
}

function SyncProgress({ synced, total, label }: SyncProgressProps) {
  const percentage = total > 0 ? Math.round((synced / total) * 100) : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-text-secondary">{label}</span>
        <span className="font-mono font-medium text-text-primary">
          {synced.toLocaleString()} / {total.toLocaleString()}
        </span>
      </div>
      <Progress value={percentage} variant={percentage === 100 ? 'success' : 'default'} />
      <p className="text-xs text-text-muted text-right">{percentage}% sincronizado</p>
    </div>
  );
}

// ==================== MAIN COMPONENT ====================

export function SolidesIntegrationPage() {
  const {
    config,
    syncStatus,
    health,
    logs,
    conflicts,
    loading,
    error,
    metrics,
    isConnected,
    triggerFullSync,
    triggerIncrementalSync,
    resolveConflict,
    ignoreConflict,
    refreshAll,
  } = useSolidesIntegration();

  // Local state
  const [syncing, setSyncing] = useState(false);
  const [selectedConflict, setSelectedConflict] = useState<SyncConflict | null>(null);
  const [showConfigModal, setShowConfigModal] = useState(false);

  // ==================== HANDLERS ====================

  const handleSync = useCallback(
    async (type: 'full' | 'incremental') => {
      setSyncing(true);
      try {
        if (type === 'full') {
          await triggerFullSync();
        } else {
          await triggerIncrementalSync();
        }
      } catch (err) {
        console.error('Erro ao sincronizar:', err);
      } finally {
        setSyncing(false);
      }
    },
    [triggerFullSync, triggerIncrementalSync]
  );

  const handleResolveConflict = useCallback(
    async (strategy: ConflictStrategy) => {
      if (!selectedConflict) return;

      await resolveConflict(selectedConflict.id, { strategy });
      setSelectedConflict(null);
    },
    [selectedConflict, resolveConflict]
  );

  const handleIgnoreConflict = useCallback(async () => {
    if (!selectedConflict) return;

    await ignoreConflict(selectedConflict.id);
    setSelectedConflict(null);
  }, [selectedConflict, ignoreConflict]);

  // ==================== TABLE COLUMNS ====================

  const logColumns: Column<SyncLog>[] = [
    {
      key: 'started_at',
      header: 'Data/Hora',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-text-muted" />
          <span className="font-mono text-sm">
            {new Date(row.started_at).toLocaleString('pt-BR', {
              day: '2-digit',
              month: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      ),
    },
    {
      key: 'sync_type',
      header: 'Tipo',
      render: (row) => (
        <Badge variant={row.sync_type === 'full' ? 'primary' : 'secondary'} size="sm">
          {row.sync_type === 'full' ? 'Completa' : 'Incremental'}
        </Badge>
      ),
    },
    {
      key: 'entity_type',
      header: 'Entidade',
      render: (row) => {
        const Icon = entityIcons[row.entity_type] || Activity;
        return (
          <div className="flex items-center gap-2">
            <Icon className="w-4 h-4 text-text-muted" />
            <span>{entityLabels[row.entity_type] || row.entity_type}</span>
          </div>
        );
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge
          variant={syncStatusColors[row.status] || 'neutral'}
          leftIcon={
            row.status === 'completed' ? (
              <CheckCheck className="w-3 h-3" />
            ) : row.status === 'failed' ? (
              <X className="w-3 h-3" />
            ) : row.status === 'running' ? (
              <RefreshCw className="w-3 h-3 animate-spin" />
            ) : undefined
          }
        >
          {row.status === 'completed'
            ? 'Concluído'
            : row.status === 'failed'
            ? 'Falhou'
            : row.status === 'running'
            ? 'Executando'
            : 'Pendente'}
        </Badge>
      ),
    },
    {
      key: 'total_processed',
      header: 'Processados',
      render: (row) => (
        <div className="text-right">
          <span className="font-mono font-medium">
            {row.total_processed.toLocaleString()}
          </span>
          <div className="text-xs text-text-muted">
            +{row.created_count} / ~{row.updated_count}
            {row.error_count > 0 && (
              <span className="text-danger ml-1">/ !{row.error_count}</span>
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'duration_seconds',
      header: 'Duração',
      render: (row) => (
        <span className="font-mono text-sm text-text-secondary">
          {row.duration_seconds ? `${row.duration_seconds}s` : '-'}
        </span>
      ),
    },
  ];

  const conflictColumns: Column<SyncConflict>[] = [
    {
      key: 'detected_at',
      header: 'Detectado',
      render: (row) => (
        <span className="font-mono text-sm">
          {new Date(row.detected_at).toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      ),
    },
    {
      key: 'entity_type',
      header: 'Entidade',
      render: (row) => {
        const Icon = entityIcons[row.entity_type] || Activity;
        return (
          <div className="flex items-center gap-2">
            <Icon className="w-4 h-4 text-text-muted" />
            <span>{entityLabels[row.entity_type] || row.entity_type}</span>
          </div>
        );
      },
    },
    {
      key: 'entity_id',
      header: 'ID',
      render: (row) => (
        <span className="font-mono text-sm text-text-secondary">
          {row.entity_id.slice(0, 8)}...
        </span>
      ),
    },
    {
      key: 'changed_fields',
      header: 'Campos',
      render: (row) => (
        <div className="flex flex-wrap gap-1">
          {row.changed_fields.slice(0, 3).map((field) => (
            <Badge key={field} variant="neutral" size="sm">
              {field}
            </Badge>
          ))}
          {row.changed_fields.length > 3 && (
            <Badge variant="neutral" size="sm">
              +{row.changed_fields.length - 3}
            </Badge>
          )}
        </div>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelectedConflict(row)}
          rightIcon={<ChevronRight className="w-4 h-4" />}
        >
          Resolver
        </Button>
      ),
    },
  ];

  // ==================== LOADING STATE ====================

  if (loading.config && !config) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Spinner size="lg" />
        </div>
      </MainLayout>
    );
  }

  // ==================== DISCONNECTED STATE ====================

  if (!config?.is_enabled) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-display font-bold text-text-primary">
                Integração Sólides
              </h1>
              <p className="text-text-secondary mt-1">
                Sincronização de colaboradores e dados de RH
              </p>
            </div>
          </div>

          <EmptyState
            icon={<WifiOff className="w-12 h-12" />}
            title="Integração não configurada"
            description="Configure a integração com o Sólides para sincronizar dados de colaboradores, departamentos e ocorrências."
            action={{
              label: 'Configurar Integração',
              onClick: () => setShowConfigModal(true),
              icon: <Settings className="w-4 h-4" />,
            }}
          />
        </div>
      </MainLayout>
    );
  }

  // ==================== MAIN RENDER ====================

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Integração Sólides
            </h1>
            <p className="text-text-secondary mt-1">
              Monitoramento e sincronização de dados de RH
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Tooltip content="Atualizar dados">
              <Button
                variant="ghost"
                size="icon"
                onClick={refreshAll}
                disabled={loading.status}
              >
                <RefreshCw
                  className={`w-4 h-4 ${loading.status ? 'animate-spin' : ''}`}
                />
              </Button>
            </Tooltip>
            <Button
              variant="secondary"
              leftIcon={<ArrowUpDown className="w-4 h-4" />}
              onClick={() => handleSync('incremental')}
              disabled={syncing || !isConnected}
              isLoading={syncing}
            >
              Sync Incremental
            </Button>
            <Button
              variant="primary"
              leftIcon={<Zap className="w-4 h-4" />}
              onClick={() => handleSync('full')}
              disabled={syncing || !isConnected}
              isLoading={syncing}
            >
              Sincronizar Agora
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-xl bg-danger/10 border border-danger/30"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-danger" />
              <p className="text-sm text-danger">{error}</p>
            </div>
          </motion.div>
        )}

        {/* Status and Stats Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Status Card */}
          <Card>
            <CardHeader title="Status da Conexão" />
            <CardBody>
              <StatusIndicator
                status={metrics.overallStatus}
                latency={health?.latency_ms}
              />
              <div className="mt-4 pt-4 border-t border-border-subtle">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">Última sincronização</span>
                  <span className="font-medium text-text-primary">
                    {metrics.lastSyncFormatted}
                  </span>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Stats Grid */}
          <div className="lg:col-span-2">
            <StatGrid columns={4}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <StatCard
                  title="Total Colaboradores"
                  value={metrics.totalEmployees.toLocaleString()}
                  icon={<Users className="w-6 h-6" />}
                  iconColor="primary"
                />
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <StatCard
                  title="Sincronizados"
                  value={metrics.syncedEmployees.toLocaleString()}
                  icon={<CheckCircle2 className="w-6 h-6" />}
                  iconColor="success"
                  change={metrics.syncPercentage}
                  changeLabel="do total"
                />
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <StatCard
                  title="Pendentes"
                  value={metrics.pendingSync.toLocaleString()}
                  icon={<Clock className="w-6 h-6" />}
                  iconColor="warning"
                />
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <StatCard
                  title="Conflitos"
                  value={metrics.pendingConflicts}
                  icon={<AlertTriangle className="w-6 h-6" />}
                  iconColor={metrics.pendingConflicts > 0 ? 'danger' : 'success'}
                />
              </motion.div>
            </StatGrid>
          </div>
        </div>

        {/* Sync Progress by Entity */}
        <Card>
          <CardHeader
            title="Progresso por Entidade"
            subtitle="Status de sincronização por tipo de dado"
          />
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(syncStatus?.entities || {}).map(([key, entity]) => {
                const entityKey = key as EntityType;
                const Icon = entityIcons[entityKey] || Activity;

                return (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="p-4 rounded-xl bg-bg-tertiary"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 rounded-lg bg-bg-elevated">
                        <Icon className="w-5 h-5 text-text-secondary" />
                      </div>
                      <div>
                        <h4 className="font-medium text-text-primary">
                          {entityLabels[entityKey] || key}
                        </h4>
                        {entity.last_sync_at && (
                          <p className="text-xs text-text-muted">
                            Última: {new Date(entity.last_sync_at).toLocaleString('pt-BR', {
                              day: '2-digit',
                              month: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </p>
                        )}
                      </div>
                    </div>
                    <SyncProgress
                      synced={entity.synced_count}
                      total={entity.total_count}
                      label="Sincronizados"
                    />
                    {entity.error_count > 0 && (
                      <div className="mt-2 flex items-center gap-2 text-danger text-sm">
                        <AlertCircle className="w-4 h-4" />
                        <span>{entity.error_count} erro(s)</span>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </CardBody>
        </Card>

        {/* Logs and Conflicts Row */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Sync Logs */}
          <Card>
            <CardHeader
              title="Logs de Sincronização"
              subtitle="Histórico recente de sincronizações"
              action={
                <Button
                  variant="ghost"
                  size="sm"
                  rightIcon={<ExternalLink className="w-4 h-4" />}
                >
                  Ver todos
                </Button>
              }
            />
            <CardBody className="p-0">
              <DataTable
                columns={logColumns}
                data={logs.slice(0, 10)}
                loading={loading.logs}
                emptyState={{
                  icon: <Activity className="w-8 h-8" />,
                  title: 'Nenhum log encontrado',
                  description: 'Execute uma sincronização para ver os logs',
                }}
              />
            </CardBody>
          </Card>

          {/* Conflicts */}
          <Card>
            <CardHeader
              title="Conflitos Pendentes"
              subtitle="Dados que necessitam de revisão manual"
              action={
                conflicts.length > 0 && (
                  <Badge variant="danger">
                    {conflicts.length} pendente{conflicts.length > 1 ? 's' : ''}
                  </Badge>
                )
              }
            />
            <CardBody className="p-0">
              <DataTable
                columns={conflictColumns}
                data={conflicts.slice(0, 10)}
                loading={loading.conflicts}
                emptyState={{
                  icon: <CheckCircle2 className="w-8 h-8" />,
                  title: 'Nenhum conflito',
                  description: 'Todos os dados estão sincronizados corretamente',
                }}
              />
            </CardBody>
          </Card>
        </div>

        {/* Conflict Resolution Modal */}
        <AnimatePresence>
          {selectedConflict && (
            <Modal
              isOpen={!!selectedConflict}
              onClose={() => setSelectedConflict(null)}
              title="Resolver Conflito"
              size="lg"
            >
              <div className="space-y-6">
                {/* Conflict Info */}
                <div className="p-4 rounded-xl bg-bg-tertiary">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-text-muted">Entidade:</span>
                      <span className="ml-2 font-medium text-text-primary">
                        {entityLabels[selectedConflict.entity_type]}
                      </span>
                    </div>
                    <div>
                      <span className="text-text-muted">ID:</span>
                      <span className="ml-2 font-mono text-text-primary">
                        {selectedConflict.entity_id.slice(0, 12)}...
                      </span>
                    </div>
                    <div className="col-span-2">
                      <span className="text-text-muted">Campos alterados:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {selectedConflict.changed_fields.map((field) => (
                          <Badge key={field} variant="warning" size="sm">
                            {field}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Data Comparison */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-text-secondary mb-2">
                      Dados Sólides
                    </h4>
                    <pre className="p-3 rounded-lg bg-bg-tertiary text-xs font-mono overflow-auto max-h-48">
                      {JSON.stringify(selectedConflict.solides_data, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-text-secondary mb-2">
                      Dados Conecta
                    </h4>
                    <pre className="p-3 rounded-lg bg-bg-tertiary text-xs font-mono overflow-auto max-h-48">
                      {JSON.stringify(selectedConflict.conecta_data, null, 2)}
                    </pre>
                  </div>
                </div>

                {/* Resolution Options */}
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-text-primary">
                    Escolha como resolver:
                  </h4>
                  <div className="grid grid-cols-2 gap-3">
                    <Button
                      variant="secondary"
                      onClick={() => handleResolveConflict('solides_wins')}
                      className="justify-start"
                    >
                      <div className="text-left">
                        <p className="font-medium">Usar dados Sólides</p>
                        <p className="text-xs text-text-muted">
                          Sobrescrever dados locais
                        </p>
                      </div>
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => handleResolveConflict('conecta_wins')}
                      className="justify-start"
                    >
                      <div className="text-left">
                        <p className="font-medium">Manter dados Conecta</p>
                        <p className="text-xs text-text-muted">
                          Ignorar alterações do Sólides
                        </p>
                      </div>
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => handleResolveConflict('most_recent')}
                      className="justify-start"
                    >
                      <div className="text-left">
                        <p className="font-medium">Mais recente</p>
                        <p className="text-xs text-text-muted">
                          Usar dados mais atualizados
                        </p>
                      </div>
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={handleIgnoreConflict}
                      className="justify-start"
                    >
                      <div className="text-left">
                        <p className="font-medium">Ignorar</p>
                        <p className="text-xs text-text-muted">
                          Não tomar ação agora
                        </p>
                      </div>
                    </Button>
                  </div>
                </div>
              </div>
            </Modal>
          )}
        </AnimatePresence>
      </div>
    </MainLayout>
  );
}

export default SolidesIntegrationPage;
