'use client';

import { useState } from 'react';
import {
  FileText, Search, RefreshCw, AlertCircle,
  ChevronRight, XCircle, Send, TrendingUp,
  Clock, CheckCircle, Ban,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  useApplications,
  useApplicationStats,
  useAdvanceApplication,
  useRejectApplication,
  useSendRecruitmentProposal,
} from '@/hooks/recruitment';
import { useQueryClient } from '@tanstack/react-query';

const stageConfig: Record<string, { label: string; color: string }> = {
  applied: { label: 'Inscrito', color: 'bg-blue-500/20 text-blue-500 border-blue-500/30' },
  screening: { label: 'Triagem', color: 'bg-cyan-500/20 text-cyan-500 border-cyan-500/30' },
  interview: { label: 'Entrevista', color: 'bg-purple-500/20 text-purple-500 border-purple-500/30' },
  evaluation: { label: 'Avaliacao', color: 'bg-orange-500/20 text-orange-500 border-orange-500/30' },
  proposal: { label: 'Proposta', color: 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30' },
  hired: { label: 'Contratado', color: 'bg-green-500/20 text-green-500 border-green-500/30' },
  rejected: { label: 'Rejeitado', color: 'bg-red-500/20 text-red-500 border-red-500/30' },
  withdrawn: { label: 'Desistiu', color: 'bg-gray-500/20 text-gray-500 border-gray-500/30' },
};

export default function CandidaturasPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');

  // Queries
  const { data: applicationsData, isLoading, isError, error, refetch } = useApplications();
  const { data: statsData } = useApplicationStats();

  // Mutations
  const advanceMutation = useAdvanceApplication();
  const rejectMutation = useRejectApplication();
  const proposalMutation = useSendRecruitmentProposal();

  const applications = (applicationsData as any)?.items || (applicationsData as any) || [];
  const stats = statsData as any;

  const filteredApplications = applications.filter((a: any) =>
    a.candidate_name?.toLowerCase().includes(search.toLowerCase()) ||
    a.position_title?.toLowerCase().includes(search.toLowerCase()) ||
    a.candidate?.name?.toLowerCase().includes(search.toLowerCase()) ||
    a.position?.title?.toLowerCase().includes(search.toLowerCase())
  );

  const invalidateQueries = () => {
    queryClient.invalidateQueries({ queryKey: ['/api/v1/recruitment/applications'] });
    queryClient.invalidateQueries({ queryKey: ['/api/v1/recruitment/applications/stats'] });
  };

  const handleAdvance = async (applicationId: string) => {
    try {
      await advanceMutation.mutateAsync({ applicationId } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao avancar candidatura:', err);
    }
  };

  const handleReject = async (applicationId: string) => {
    try {
      await rejectMutation.mutateAsync({ applicationId, data: { reason: 'Nao aprovado' } } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao rejeitar candidatura:', err);
    }
  };

  const handleSendProposal = async (applicationId: string) => {
    try {
      await proposalMutation.mutateAsync({ applicationId } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao enviar proposta:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FileText className="h-6 w-6" />
            Candidaturas
          </h1>
          <p className="text-muted-foreground">Acompanhe candidaturas e etapas do processo seletivo</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total</p>
                <p className="text-2xl font-bold">{stats?.total ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center">
                <FileText className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Em Andamento</p>
                <p className="text-2xl font-bold text-cyan-600">{stats?.active_applications ?? stats?.em_andamento ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-cyan-50 flex items-center justify-center">
                <Clock className="h-5 w-5 text-cyan-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Em Entrevista</p>
                <p className="text-2xl font-bold text-purple-600">{stats?.in_interview ?? stats?.em_entrevista ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-purple-50 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Contratados</p>
                <p className="text-2xl font-bold text-green-600">{stats?.hired ?? stats?.contratados ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-green-50 flex items-center justify-center">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Rejeitados</p>
                <p className="text-2xl font-bold text-red-600">{stats?.rejected ?? stats?.rejeitados ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-red-50 flex items-center justify-center">
                <Ban className="h-5 w-5 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por candidato ou vaga..."
          className="pl-10"
        />
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-destructive/10 border border-destructive/30">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive">{(error as Error)?.message || 'Erro ao carregar candidaturas'}</p>
          <Button variant="outline" size="sm" onClick={() => refetch()} className="ml-auto">
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="divide-y">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="p-4 flex items-center gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-56 bg-muted rounded animate-pulse" />
                    <div className="h-3 w-40 bg-muted rounded animate-pulse" />
                  </div>
                  <div className="h-6 w-24 bg-muted rounded animate-pulse" />
                </div>
              ))}
            </div>
          ) : filteredApplications.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium">Nenhum registro encontrado</h3>
              <p className="text-muted-foreground mt-1">
                {search ? 'Tente ajustar a busca' : 'Ainda nao existem candidaturas registradas'}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Candidato</TableHead>
                  <TableHead>Vaga</TableHead>
                  <TableHead>Etapa</TableHead>
                  <TableHead>Data Inscricao</TableHead>
                  <TableHead>Ultima Atualizacao</TableHead>
                  <TableHead className="text-right">Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredApplications.map((application: any) => {
                  const stage = stageConfig[application.stage || application.status] || stageConfig.applied || { label: 'Aplicado', color: 'bg-blue-100 text-blue-800' };
                  const candidateName = application.candidate_name || application.candidate?.name || '-';
                  const positionTitle = application.position_title || application.position?.title || '-';
                  const isActive = !['rejected', 'withdrawn', 'hired'].includes(application.stage || application.status);

                  return (
                    <TableRow key={application.id}>
                      <TableCell>
                        <p className="font-medium">{candidateName}</p>
                        {application.candidate_email && (
                          <p className="text-xs text-muted-foreground">{application.candidate_email}</p>
                        )}
                      </TableCell>
                      <TableCell>
                        <p className="text-sm">{positionTitle}</p>
                        {application.department && (
                          <p className="text-xs text-muted-foreground">{application.department}</p>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={stage.color}>
                          {stage.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {application.applied_at || application.created_at
                            ? new Date(application.applied_at || application.created_at).toLocaleDateString('pt-BR')
                            : '-'}
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {application.updated_at
                            ? new Date(application.updated_at).toLocaleDateString('pt-BR')
                            : '-'}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        {isActive && (
                          <div className="flex items-center justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Avancar etapa"
                              onClick={() => handleAdvance(application.id)}
                              disabled={advanceMutation.isPending}
                            >
                              <ChevronRight className="h-4 w-4 text-green-600" />
                            </Button>
                            {(application.stage === 'evaluation' || application.status === 'evaluation') && (
                              <Button
                                variant="ghost"
                                size="sm"
                                title="Enviar proposta"
                                onClick={() => handleSendProposal(application.id)}
                                disabled={proposalMutation.isPending}
                              >
                                <Send className="h-4 w-4 text-blue-600" />
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Rejeitar"
                              onClick={() => handleReject(application.id)}
                              disabled={rejectMutation.isPending}
                              className="text-red-500 hover:text-red-600 hover:bg-red-500/10"
                            >
                              <XCircle className="h-4 w-4" />
                            </Button>
                          </div>
                        )}
                        {!isActive && (
                          <span className="text-xs text-muted-foreground">Finalizada</span>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Info */}
      {!isLoading && filteredApplications.length > 0 && (
        <div className="text-sm text-muted-foreground text-center">
          Mostrando {filteredApplications.length} de {applications.length} candidaturas
        </div>
      )}
    </div>
  );
}
