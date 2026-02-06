'use client';

import { Calendar, Plus, Search, RefreshCw, AlertCircle, Clock, CheckCircle, XCircle, Star, CalendarClock, Video, MapPin, Phone as PhoneIcon } from 'lucide-react';
import { useState } from 'react';
;
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  useInterviews,
  useInterviewStats,
  useCreateInterview,
  useRescheduleInterview,
  useCancelInterview,
  useCompleteInterview,
} from '@/hooks/recruitment';
import { useQueryClient } from '@tanstack/react-query';

const statusConfig: Record<string, { label: string; color: string }> = {
  scheduled: { label: 'Agendada', color: 'bg-blue-500/20 text-blue-500 border-blue-500/30' },
  confirmed: { label: 'Confirmada', color: 'bg-cyan-500/20 text-cyan-500 border-cyan-500/30' },
  in_progress: { label: 'Em Andamento', color: 'bg-purple-500/20 text-purple-500 border-purple-500/30' },
  completed: { label: 'Concluida', color: 'bg-green-500/20 text-green-500 border-green-500/30' },
  cancelled: { label: 'Cancelada', color: 'bg-red-500/20 text-red-500 border-red-500/30' },
  no_show: { label: 'Ausente', color: 'bg-orange-500/20 text-orange-500 border-orange-500/30' },
  rescheduled: { label: 'Reagendada', color: 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30' },
};

const typeConfig: Record<string, { label: string; icon: any }> = {
  in_person: { label: 'Presencial', icon: MapPin },
  video: { label: 'Video', icon: Video },
  phone: { label: 'Telefone', icon: PhoneIcon },
};

export default function EntrevistasPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    application_id: '',
    interviewer_id: '',
    interview_type: 'in_person',
    scheduled_at: '',
    duration_minutes: 60,
    location: '',
    notes: '',
  });

  // Queries
  const { data: interviewsData, isLoading, isError, error, refetch } = useInterviews();
  const { data: statsData } = useInterviewStats();

  // Mutations
  const createMutation = useCreateInterview();
  const rescheduleMutation = useRescheduleInterview();
  const cancelMutation = useCancelInterview();
  const completeMutation = useCompleteInterview();
  // const evaluateMutation = useEvaluateInterview(); // Hook removed from API

  const interviews = (interviewsData as any)?.items || (interviewsData as any) || [];
  const stats = statsData as any;

  const filteredInterviews = interviews.filter((i: any) =>
    i.candidate_name?.toLowerCase().includes(search.toLowerCase()) ||
    i.position_title?.toLowerCase().includes(search.toLowerCase()) ||
    i.candidate?.name?.toLowerCase().includes(search.toLowerCase()) ||
    i.interviewer_name?.toLowerCase().includes(search.toLowerCase())
  );

  const invalidateQueries = () => {
    queryClient.invalidateQueries({ queryKey: ['/api/v1/recruitment/interviews'] });
    queryClient.invalidateQueries({ queryKey: ['/api/v1/recruitment/interviews/stats'] });
  };

  const handleCreate = async () => {
    try {
      await createMutation.mutateAsync({ data: formData as any });
      setDialogOpen(false);
      setFormData({
        application_id: '',
        interviewer_id: '',
        interview_type: 'in_person',
        scheduled_at: '',
        duration_minutes: 60,
        location: '',
        notes: '',
      });
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao agendar entrevista:', err);
    }
  };

  const handleReschedule = async (interviewId: string) => {
    const newDate = prompt('Nova data e hora (AAAA-MM-DDTHH:MM):');
    if (!newDate) return;
    try {
      await rescheduleMutation.mutateAsync({
        interviewId,
        data: { scheduled_at: newDate },
      } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao reagendar entrevista:', err);
    }
  };

  const handleCancel = async (interviewId: string) => {
    try {
      await cancelMutation.mutateAsync({ interviewId, data: { reason: 'Cancelado pelo usuario' } } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao cancelar entrevista:', err);
    }
  };

  const handleComplete = async (interviewId: string) => {
    try {
      await completeMutation.mutateAsync({ interviewId } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao concluir entrevista:', err);
    }
  };

  const handleEvaluate = async (interviewId: string) => {
    const rating = prompt('Nota (1 a 5):');
    if (!rating) return;
    try {
      // TODO: Re-implement evaluation when API endpoint is available
      console.log('Evaluate interview:', interviewId, 'rating:', rating);
      // await evaluateMutation.mutateAsync({
      //   interviewId,
      //   data: { rating: parseInt(rating), notes: '' },
      // } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao avaliar entrevista:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Calendar className="h-6 w-6" />
            Entrevistas
          </h1>
          <p className="text-muted-foreground">Agenda de entrevistas e avaliacoes de candidatos</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Agendar Entrevista
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Agendar Nova Entrevista</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="application_id">ID da Candidatura</Label>
                    <Input
                      id="application_id"
                      value={formData.application_id}
                      onChange={(e) => setFormData({ ...formData, application_id: e.target.value })}
                      placeholder="ID da candidatura"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="interviewer_id">ID do Entrevistador</Label>
                    <Input
                      id="interviewer_id"
                      value={formData.interviewer_id}
                      onChange={(e) => setFormData({ ...formData, interviewer_id: e.target.value })}
                      placeholder="ID do entrevistador"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="interview_type">Tipo</Label>
                    <Select
                      value={formData.interview_type}
                      onValueChange={(value) => setFormData({ ...formData, interview_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="in_person">Presencial</SelectItem>
                        <SelectItem value="video">Video</SelectItem>
                        <SelectItem value="phone">Telefone</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="duration_minutes">Duracao (min)</Label>
                    <Input
                      id="duration_minutes"
                      type="number"
                      min={15}
                      step={15}
                      value={formData.duration_minutes}
                      onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 60 })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="scheduled_at">Data e Hora</Label>
                  <Input
                    id="scheduled_at"
                    type="datetime-local"
                    value={formData.scheduled_at}
                    onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="location">Local / Link</Label>
                  <Input
                    id="location"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    placeholder="Endereco ou link da reuniao"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="notes">Observacoes</Label>
                  <Input
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    placeholder="Notas adicionais (opcional)"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancelar
                </Button>
                <Button
                  onClick={handleCreate}
                  disabled={!formData.application_id || !formData.scheduled_at || createMutation.isPending}
                >
                  {createMutation.isPending ? 'Agendando...' : 'Agendar'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
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
                <Calendar className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Hoje</p>
                <p className="text-2xl font-bold text-cyan-600">{stats?.today ?? stats?.hoje ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-cyan-50 flex items-center justify-center">
                <CalendarClock className="h-5 w-5 text-cyan-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Agendadas</p>
                <p className="text-2xl font-bold text-purple-600">{stats?.scheduled ?? stats?.agendadas ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-purple-50 flex items-center justify-center">
                <Clock className="h-5 w-5 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Concluidas</p>
                <p className="text-2xl font-bold text-green-600">{stats?.completed ?? stats?.concluidas ?? 0}</p>
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
                <p className="text-sm text-muted-foreground">Canceladas</p>
                <p className="text-2xl font-bold text-red-600">{stats?.cancelled ?? stats?.canceladas ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-red-50 flex items-center justify-center">
                <XCircle className="h-5 w-5 text-red-600" />
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
          placeholder="Buscar por candidato, vaga ou entrevistador..."
          className="pl-10"
        />
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-destructive/10 border border-destructive/30">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive">{(error as Error)?.message || 'Erro ao carregar entrevistas'}</p>
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
          ) : filteredInterviews.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium">Nenhum registro encontrado</h3>
              <p className="text-muted-foreground mt-1">
                {search ? 'Tente ajustar a busca' : 'Agende sua primeira entrevista'}
              </p>
              {!search && (
                <Button className="mt-4" onClick={() => setDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Agendar Entrevista
                </Button>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Candidato</TableHead>
                  <TableHead>Vaga</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Data / Hora</TableHead>
                  <TableHead>Duracao</TableHead>
                  <TableHead>Entrevistador</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredInterviews.map((interview: any) => {
                  const status = statusConfig[interview.status] || statusConfig.scheduled || { label: 'Agendada', color: 'bg-blue-100 text-blue-800' };
                  const type = typeConfig[interview.interview_type] || typeConfig.in_person || { label: 'Presencial', icon: () => null };
                  const TypeIcon = type.icon;
                  const candidateName = interview.candidate_name || interview.candidate?.name || '-';
                  const positionTitle = interview.position_title || interview.position?.title || '-';
                  const isScheduled = ['scheduled', 'confirmed'].includes(interview.status);
                  const isCompleted = interview.status === 'completed';

                  return (
                    <TableRow key={interview.id}>
                      <TableCell>
                        <p className="font-medium">{candidateName}</p>
                      </TableCell>
                      <TableCell>
                        <p className="text-sm">{positionTitle}</p>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <TypeIcon className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{type.label}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-sm font-medium">
                            {interview.scheduled_at
                              ? new Date(interview.scheduled_at).toLocaleDateString('pt-BR')
                              : '-'}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {interview.scheduled_at
                              ? new Date(interview.scheduled_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
                              : ''}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{interview.duration_minutes ?? 60} min</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{interview.interviewer_name || interview.interviewer?.name || '-'}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={status.color}>
                          {status.label}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          {isScheduled && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                title="Reagendar"
                                onClick={() => handleReschedule(interview.id)}
                              >
                                <CalendarClock className="h-4 w-4 text-blue-600" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                title="Concluir"
                                onClick={() => handleComplete(interview.id)}
                              >
                                <CheckCircle className="h-4 w-4 text-green-600" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                title="Cancelar"
                                onClick={() => handleCancel(interview.id)}
                                className="text-red-500 hover:text-red-600 hover:bg-red-500/10"
                              >
                                <XCircle className="h-4 w-4" />
                              </Button>
                            </>
                          )}
                          {isCompleted && (
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Avaliar"
                              onClick={() => handleEvaluate(interview.id)}
                            >
                              <Star className="h-4 w-4 text-yellow-500" />
                            </Button>
                          )}
                          {!isScheduled && !isCompleted && (
                            <span className="text-xs text-muted-foreground">-</span>
                          )}
                        </div>
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
      {!isLoading && filteredInterviews.length > 0 && (
        <div className="text-sm text-muted-foreground text-center">
          Mostrando {filteredInterviews.length} de {interviews.length} entrevistas
        </div>
      )}
    </div>
  );
}
