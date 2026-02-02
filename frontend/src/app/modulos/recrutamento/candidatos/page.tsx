'use client';

import { UserPlus, Plus, Search, RefreshCw, MoreHorizontal, Edit2, Trash2, ShieldBan, ShieldCheck, AlertCircle, Mail, Phone, User } from 'lucide-react';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  useCandidates,
  useCandidateStats,
  useCreateCandidate,
  useDeleteCandidate,
  useBlockCandidate,
  useUnblockCandidate,
} from '@/hooks/recruitment';
import { useQueryClient } from '@tanstack/react-query';

const statusConfig: Record<string, { label: string; color: string }> = {
  active: { label: 'Ativo', color: 'bg-green-500/20 text-green-500 border-green-500/30' },
  inactive: { label: 'Inativo', color: 'bg-gray-500/20 text-gray-500 border-gray-500/30' },
  blocked: { label: 'Bloqueado', color: 'bg-red-500/20 text-red-500 border-red-500/30' },
  hired: { label: 'Contratado', color: 'bg-blue-500/20 text-blue-500 border-blue-500/30' },
};

export default function CandidatosPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    cpf: '',
    position_desired: '',
    source: '',
  });

  // Queries
  const { data: candidatesData, isLoading, isError, error, refetch } = useCandidates();
  const { data: statsData } = useCandidateStats();

  // Mutations
  const createMutation = useCreateCandidate();
  const deleteMutation = useDeleteCandidate();
  const blockMutation = useBlockCandidate();
  const unblockMutation = useUnblockCandidate();

  const candidates = (candidatesData as any)?.items || (candidatesData as any) || [];
  const stats = statsData as any;

  const filteredCandidates = candidates.filter((c: any) =>
    c.name?.toLowerCase().includes(search.toLowerCase()) ||
    c.email?.toLowerCase().includes(search.toLowerCase()) ||
    c.phone?.includes(search)
  );

  const invalidateQueries = () => {
    queryClient.invalidateQueries({ queryKey: ['/api/v1/recruitment/candidates'] });
    queryClient.invalidateQueries({ queryKey: ['/api/v1/recruitment/candidates/stats'] });
  };

  const handleCreate = async () => {
    try {
      await createMutation.mutateAsync({ data: formData as any });
      setDialogOpen(false);
      setFormData({ name: '', email: '', phone: '', cpf: '', position_desired: '', source: '' });
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao criar candidato:', err);
    }
  };

  const handleBlock = async (candidateId: string) => {
    try {
      await blockMutation.mutateAsync({ candidateId } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao bloquear candidato:', err);
    }
  };

  const handleUnblock = async (candidateId: string) => {
    try {
      await unblockMutation.mutateAsync({ candidateId } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao desbloquear candidato:', err);
    }
  };

  const handleDelete = async (candidateId: string) => {
    try {
      await deleteMutation.mutateAsync({ candidateId } as any);
      invalidateQueries();
    } catch (err) {
      console.error('Erro ao excluir candidato:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <UserPlus className="h-6 w-6" />
            Candidatos
          </h1>
          <p className="text-muted-foreground">Base de candidatos cadastrados no sistema</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Novo Candidato
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Cadastrar Novo Candidato</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nome Completo</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Nome do candidato"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">E-mail</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="email@exemplo.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Telefone</Label>
                    <Input
                      id="phone"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="(11) 99999-9999"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="cpf">CPF</Label>
                    <Input
                      id="cpf"
                      value={formData.cpf}
                      onChange={(e) => setFormData({ ...formData, cpf: e.target.value })}
                      placeholder="000.000.000-00"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="source">Origem</Label>
                    <Input
                      id="source"
                      value={formData.source}
                      onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                      placeholder="Ex: Site, Indicacao"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="position_desired">Cargo Desejado</Label>
                  <Input
                    id="position_desired"
                    value={formData.position_desired}
                    onChange={(e) => setFormData({ ...formData, position_desired: e.target.value })}
                    placeholder="Ex: Vigilante Patrimonial"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleCreate} disabled={!formData.name || createMutation.isPending}>
                  {createMutation.isPending ? 'Cadastrando...' : 'Cadastrar'}
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
                <User className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Ativos</p>
                <p className="text-2xl font-bold text-green-600">{stats?.active_candidates ?? stats?.ativos ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-green-50 flex items-center justify-center">
                <ShieldCheck className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Bloqueados</p>
                <p className="text-2xl font-bold text-red-600">{stats?.blocked_candidates ?? stats?.bloqueados ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-red-50 flex items-center justify-center">
                <ShieldBan className="h-5 w-5 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Contratados</p>
                <p className="text-2xl font-bold text-blue-600">{stats?.hired_candidates ?? stats?.contratados ?? 0}</p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center">
                <UserPlus className="h-5 w-5 text-blue-600" />
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
          placeholder="Buscar candidatos por nome, e-mail ou telefone..."
          className="pl-10"
        />
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-destructive/10 border border-destructive/30">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive">{(error as Error)?.message || 'Erro ao carregar candidatos'}</p>
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
          ) : filteredCandidates.length === 0 ? (
            <div className="text-center py-12">
              <UserPlus className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium">Nenhum registro encontrado</h3>
              <p className="text-muted-foreground mt-1">
                {search ? 'Tente ajustar a busca' : 'Cadastre seu primeiro candidato'}
              </p>
              {!search && (
                <Button className="mt-4" onClick={() => setDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Candidato
                </Button>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Candidato</TableHead>
                  <TableHead>Contato</TableHead>
                  <TableHead>Cargo Desejado</TableHead>
                  <TableHead>Origem</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Cadastro</TableHead>
                  <TableHead className="text-right">Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCandidates.map((candidate: any) => {
                  const status = statusConfig[candidate.status] || statusConfig.active || { label: 'Ativo', color: 'bg-green-100 text-green-800' };
                  return (
                    <TableRow key={candidate.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <User className="h-4 w-4 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium">{candidate.name}</p>
                            {candidate.cpf && (
                              <p className="text-xs text-muted-foreground">{candidate.cpf}</p>
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {candidate.email && (
                            <div className="flex items-center gap-1 text-sm text-muted-foreground">
                              <Mail className="h-3 w-3" />
                              <span className="truncate max-w-[180px]">{candidate.email}</span>
                            </div>
                          )}
                          {candidate.phone && (
                            <div className="flex items-center gap-1 text-sm text-muted-foreground">
                              <Phone className="h-3 w-3" />
                              {candidate.phone}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{candidate.position_desired || '-'}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">{candidate.source || '-'}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={status.color}>
                          {status.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {candidate.created_at
                            ? new Date(candidate.created_at).toLocaleDateString('pt-BR')
                            : '-'}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button variant="ghost" size="sm" title="Editar">
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          {candidate.status === 'blocked' ? (
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Desbloquear"
                              onClick={() => handleUnblock(candidate.id)}
                            >
                              <ShieldCheck className="h-4 w-4 text-green-600" />
                            </Button>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              title="Bloquear"
                              onClick={() => handleBlock(candidate.id)}
                            >
                              <ShieldBan className="h-4 w-4 text-orange-600" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Excluir"
                            onClick={() => handleDelete(candidate.id)}
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
      {!isLoading && filteredCandidates.length > 0 && (
        <div className="text-sm text-muted-foreground text-center">
          Mostrando {filteredCandidates.length} de {candidates.length} candidatos
        </div>
      )}
    </div>
  );
}
