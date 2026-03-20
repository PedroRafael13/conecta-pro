'use client';

import { Briefcase, Plus, Search, RefreshCw, MoreHorizontal, Edit2, Trash2, Globe, XCircle, AlertCircle } from 'lucide-react';
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
  useJobPositions,
  usePositionStats,
  useCreateJobPosition,
  usePublishPosition,
  useClosePosition,
  useDeleteJobPosition,
} from '@/hooks/recruitment';
import { useQueryClient } from '@tanstack/react-query';

const statusConfig: Record<string, { label: string; color: string }> = {
  draft: { label: 'Rascunho', color: 'bg-gray-500/20 text-gray-500 border-gray-500/30' },
  open: { label: 'Aberta', color: 'bg-green-500/20 text-green-500 border-green-500/30' },
  paused: { label: 'Pausada', color: 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30' },
  closed: { label: 'Fechada', color: 'bg-red-500/20 text-red-500 border-red-500/30' },
  published: { label: 'Publicada', color: 'bg-blue-500/20 text-blue-500 border-blue-500/30' },
};

export default function VagasPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    department: '',
    location: '',
    employment_type: 'clt',
    vacancies: 1,
  });

  // Queries
  const { data: positionsData, isLoading, isError, error, refetch } = useJobPositions();
  const { data: statsData } = usePositionStats();

  // Mutations
  const createMutation = useCreateJobPosition();
  const publishMutation = usePublishPosition();
  const closeMutation = useClosePosition();
  const deleteMutation = useDeleteJobPosition();

  const positions = (positionsData as any)?.items || (positionsData as any) || [];
  const stats = statsData as any;

  const filteredPositions = positions.filter((p: any) =>
    p.title?.toLowerCase().includes(search.toLowerCase()) ||
    p.department?.toLowerCase().includes(search.toLowerCase())
  );

  const invalidateQueries = () => {
    queryClient.invalidateQueries({ queryKey: ['/api/v1/recruitment/job-positions'] });
    queryClient.invalidateQueries({ queryKey: ['/api/v1/recruitment/job-positions/stats'] });
  };

  const handleCreate = async () => {
    try {
      await createMutation.mutateAsync({ data: formData as any });
      setDialogOpen(false);
      setFormData({ title: '', description: '', department: '', location: '', employment_type: 'clt', vacancies: 1 });
      invalidateQueries();
    } catch {
      // silenced
    }
  };

  const handlePublish = async (positionId: string) => {
    try {
      await publishMutation.mutateAsync({ positionId } as any);
      invalidateQueries();
    } catch {
      // silenced
    }
  };

  const handleClose = async (positionId: string) => {
    try {
      await closeMutation.mutateAsync({ positionId } as any);
      invalidateQueries();
    } catch {
      // silenced
    }
  };

  const handleDelete = async (positionId: string) => {
    try {
      await deleteMutation.mutateAsync({ positionId } as any);
      invalidateQueries();
    } catch {
      // silenced
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Briefcase className="h-6 w-6" />
            Vagas
          </h1>
          <p className="text-muted-foreground">Gerencie as vagas e posicoes abertas</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Nova Vaga
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Criar Nova Vaga</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Titulo</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="Ex: Vigilante Patrimonial"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Descricao</Label>
                  <Input
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Descricao da vaga"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="department">Departamento</Label>
                    <Input
                      id="department"
                      value={formData.department}
                      onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                      placeholder="Ex: Operacional"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="location">Localizacao</Label>
                    <Input
                      id="location"
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      placeholder="Ex: Sao Paulo"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="employment_type">Tipo de Contrato</Label>
                    <Select
                      value={formData.employment_type}
                      onValueChange={(value) => setFormData({ ...formData, employment_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="clt">CLT</SelectItem>
                        <SelectItem value="pj">PJ</SelectItem>
                        <SelectItem value="temporary">Temporario</SelectItem>
                        <SelectItem value="intern">Estagio</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="vacancies">Numero de Vagas</Label>
                    <Input
                      id="vacancies"
                      type="number"
                      min={1}
                      value={formData.vacancies}
                      onChange={(e) => setFormData({ ...formData, vacancies: parseInt(e.target.value) || 1 })}
                    />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleCreate} disabled={!formData.title || createMutation.isPending}>
                  {createMutation.isPending ? 'Criando...' : 'Criar Vaga'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total</p>
                <p className="text-2xl font-bold">{stats?.total ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center">
                <Briefcase className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Abertas</p>
                <p className="text-2xl font-bold text-green-600">{stats?.open_positions ?? stats?.abertas ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-green-50 flex items-center justify-center">
                <Globe className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pausadas</p>
                <p className="text-2xl font-bold text-yellow-600">{stats?.paused_positions ?? stats?.pausadas ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-yellow-50 flex items-center justify-center">
                <AlertCircle className="h-5 w-5 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Fechadas</p>
                <p className="text-2xl font-bold text-red-600">{stats?.closed_positions ?? stats?.fechadas ?? 0}</p>
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
          placeholder="Buscar vagas por titulo ou departamento..."
          className="pl-10"
        />
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-destructive/10 border border-destructive/30">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive">{(error as Error)?.message || 'Erro ao carregar vagas'}</p>
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
                    <div className="h-4 w-48 bg-muted rounded animate-pulse" />
                    <div className="h-3 w-32 bg-muted rounded animate-pulse" />
                  </div>
                  <div className="h-6 w-20 bg-muted rounded animate-pulse" />
                </div>
              ))}
            </div>
          ) : filteredPositions.length === 0 ? (
            <div className="text-center py-12">
              <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium">Nenhum registro encontrado</h3>
              <p className="text-muted-foreground mt-1">
                {search ? 'Tente ajustar a busca' : 'Crie sua primeira vaga'}
              </p>
              {!search && (
                <Button className="mt-4" onClick={() => setDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Vaga
                </Button>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Titulo</TableHead>
                  <TableHead>Departamento</TableHead>
                  <TableHead>Localizacao</TableHead>
                  <TableHead>Contrato</TableHead>
                  <TableHead>Vagas</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Criado em</TableHead>
                  <TableHead className="text-right">Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredPositions.map((position: any) => {
                  const status = statusConfig[position.status] || statusConfig.draft || { label: 'Rascunho', color: 'bg-gray-100 text-gray-800' };
                  return (
                    <TableRow key={position.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{position.title}</p>
                          {position.description && (
                            <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                              {position.description}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{position.department || '-'}</TableCell>
                      <TableCell>{position.location || '-'}</TableCell>
                      <TableCell>
                        <span className="text-sm capitalize">{position.employment_type || '-'}</span>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{position.vacancies ?? position.vagas ?? '-'}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={status.color}>
                          {status.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {position.created_at
                            ? new Date(position.created_at).toLocaleDateString('pt-BR')
                            : '-'}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Editar"
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          {(position.status === 'draft' || position.status === 'paused') && (
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Publicar"
                              onClick={() => handlePublish(position.id)}
                            >
                              <Globe className="h-4 w-4 text-green-600" />
                            </Button>
                          )}
                          {(position.status === 'open' || position.status === 'published') && (
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Fechar"
                              onClick={() => handleClose(position.id)}
                            >
                              <XCircle className="h-4 w-4 text-orange-600" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Excluir"
                            onClick={() => handleDelete(position.id)}
                            className="text-red-500 hover:text-red-600 hover:bg-red-500/10"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
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
      {!isLoading && filteredPositions.length > 0 && (
        <div className="text-sm text-muted-foreground text-center">
          Mostrando {filteredPositions.length} de {positions.length} vagas
        </div>
      )}
    </div>
  );
}
