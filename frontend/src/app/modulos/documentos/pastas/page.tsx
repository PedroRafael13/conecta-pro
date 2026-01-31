'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import {
  FolderOpen,
  FolderPlus,
  ChevronRight,
  Home,
  Search,
  FileText,
  ArrowLeft,
  MoreVertical,
  Edit,
  Trash2,
  FolderInput,
  Lock,
  Unlock,
} from 'lucide-react';
import Link from 'next/link';
import { folderService, Folder, formatFileSize, FOLDER_TYPES } from '@/lib/services/ged';

function PastasContent() {
  const searchParams = useSearchParams();
  const folderId = searchParams.get('id');
  const { toast } = useToast();

  const [folders, setFolders] = useState<Folder[]>([]);
  const [currentFolder, setCurrentFolder] = useState<Folder | null>(null);
  const [breadcrumb, setBreadcrumb] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    folder_type: 'condominio',
    is_public: false,
  });

  const loadFolders = useCallback(async () => {
    try {
      setLoading(true);

      if (folderId) {
        // Carregar pasta atual
        const folder = await folderService.get(folderId);
        setCurrentFolder(folder);

        // Carregar subpastas
        const response = await folderService.list({ parent_id: folderId, page_size: 100 });
        setFolders(response.items);

        setBreadcrumb([folder]);
      } else {
        // Carregar pastas raiz
        setCurrentFolder(null);
        const response = await folderService.list({ page_size: 100 });
        const rootFolders = response.items.filter(f => f.is_root);
        setFolders(rootFolders);
        setBreadcrumb([]);
      }
    } catch (error) {
      console.error('Erro ao carregar pastas:', error);
      toast({
        variant: 'destructive',
        title: 'Erro ao carregar pastas',
        description: 'Não foi possível carregar a lista de pastas.',
      });
    } finally {
      setLoading(false);
    }
  }, [folderId, toast]);

  useEffect(() => {
    loadFolders();
  }, [loadFolders]);

  // Filtrar por busca
  const filteredFolders = folders.filter(f =>
    f.name.toLowerCase().includes(search.toLowerCase()) ||
    f.description?.toLowerCase().includes(search.toLowerCase())
  );

  // Criar nova pasta
  const handleCreateFolder = async () => {
    try {
      await folderService.create({
        ...formData,
        parent_id: folderId || undefined,
      });
      setDialogOpen(false);
      setFormData({ name: '', description: '', folder_type: 'condominio', is_public: false });
      toast({
        variant: 'success',
        title: 'Pasta criada',
        description: `A pasta "${formData.name}" foi criada com sucesso.`,
      });
      loadFolders();
    } catch (error: any) {
      console.error('Erro ao criar pasta:', error);

      // Tratar erro 409 (pasta duplicada)
      if (error?.response?.status === 409 || error?.status === 409) {
        const errorMsg = error?.response?.data?.detail || error?.message || 'Já existe uma pasta com este nome neste local';
        toast({
          variant: 'destructive',
          title: 'Pasta duplicada',
          description: errorMsg,
        });
        return;
      }

      // Outros erros
      toast({
        variant: 'destructive',
        title: 'Erro ao criar pasta',
        description: 'Não foi possível criar a pasta. Tente novamente.',
      });
    }
  };

  // Editar pasta
  const handleEditFolder = async () => {
    if (!selectedFolder) return;
    try {
      await folderService.update(selectedFolder.id, {
        name: formData.name,
        description: formData.description,
        is_public: formData.is_public,
      });
      setEditDialogOpen(false);
      setSelectedFolder(null);
      toast({
        variant: 'success',
        title: 'Pasta atualizada',
        description: `A pasta "${formData.name}" foi atualizada com sucesso.`,
      });
      loadFolders();
    } catch (error: any) {
      console.error('Erro ao atualizar pasta:', error);

      // Tratar erro 409 (nome duplicado)
      if (error?.response?.status === 409 || error?.status === 409) {
        const errorMsg = error?.response?.data?.detail || error?.message || 'Já existe uma pasta com este nome neste local';
        toast({
          variant: 'destructive',
          title: 'Nome duplicado',
          description: errorMsg,
        });
        return;
      }

      // Outros erros
      toast({
        variant: 'destructive',
        title: 'Erro ao atualizar',
        description: 'Não foi possível atualizar a pasta. Tente novamente.',
      });
    }
  };

  // Excluir pasta
  const handleDeleteFolder = async () => {
    if (!selectedFolder) return;
    try {
      await folderService.delete(selectedFolder.id);
      setDeleteDialogOpen(false);
      toast({
        variant: 'success',
        title: 'Pasta excluída',
        description: `A pasta "${selectedFolder.name}" foi excluída com sucesso.`,
      });
      setSelectedFolder(null);
      loadFolders();
    } catch (error) {
      console.error('Erro ao excluir pasta:', error);
      toast({
        variant: 'destructive',
        title: 'Erro ao excluir',
        description: 'Não foi possível excluir a pasta. Verifique se está vazia.',
      });
    }
  };

  // Abrir dialog de edição
  const openEditDialog = (folder: Folder, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedFolder(folder);
    setFormData({
      name: folder.name,
      description: folder.description || '',
      folder_type: folder.folder_type,
      is_public: folder.is_public,
    });
    setEditDialogOpen(true);
  };

  // Abrir dialog de exclusão
  const openDeleteDialog = (folder: Folder, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedFolder(folder);
    setDeleteDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {folderId && (
            <Link href="/modulos/documentos/pastas">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
          )}
          <div>
            <h1 className="text-2xl font-bold">
              {currentFolder ? currentFolder.name : 'Pastas'}
            </h1>
            <p className="text-muted-foreground">
              {currentFolder
                ? currentFolder.description || 'Organize seus documentos em pastas'
                : 'Gerencie a estrutura de pastas do sistema'}
            </p>
          </div>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <FolderPlus className="h-4 w-4 mr-2" />
              Nova Pasta
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Criar Nova Pasta</DialogTitle>
              <DialogDescription>
                Crie uma nova pasta para organizar seus documentos. Preencha os campos abaixo.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nome</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Nome da pasta"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Descrição</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Descrição da pasta (opcional)"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="folder_type">Tipo</Label>
                <Select
                  value={formData.folder_type}
                  onValueChange={(value) => setFormData({ ...formData, folder_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    {FOLDER_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={formData.is_public}
                  onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                  className="rounded"
                />
                <Label htmlFor="is_public">Pasta pública</Label>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleCreateFolder} disabled={!formData.name}>
                Criar Pasta
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm">
        <Link href="/modulos/documentos" className="text-muted-foreground hover:text-foreground">
          <Home className="h-4 w-4" />
        </Link>
        <ChevronRight className="h-4 w-4 text-muted-foreground" />
        <Link
          href="/modulos/documentos/pastas"
          className={`hover:text-foreground ${!folderId ? 'font-medium' : 'text-muted-foreground'}`}
        >
          Pastas
        </Link>
        {breadcrumb.map((folder, index) => (
          <span key={folder.id} className="flex items-center gap-2">
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
            <Link
              href={`/modulos/documentos/pastas?id=${folder.id}`}
              className={index === breadcrumb.length - 1 ? 'font-medium' : 'text-muted-foreground hover:text-foreground'}
            >
              {folder.name}
            </Link>
          </span>
        ))}
      </nav>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar pastas..."
          className="pl-10"
        />
      </div>

      {/* Folders Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : filteredFolders.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <FolderOpen className="h-16 w-16 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium">Nenhuma pasta encontrada</h3>
          <p className="mt-2">
            {search ? 'Tente uma busca diferente' : 'Crie sua primeira pasta'}
          </p>
          {!search && (
            <Button className="mt-4" onClick={() => setDialogOpen(true)}>
              <FolderPlus className="h-4 w-4 mr-2" />
              Criar Pasta
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredFolders.map((folder) => (
            <div key={folder.id} className="relative group">
              <Link href={`/modulos/documentos/pastas?id=${folder.id}`}>
                <Card className="hover:bg-accent/50 transition-colors cursor-pointer h-full">
                  <CardContent className="pt-6">
                    <div className="flex items-start gap-4">
                      <div className="p-3 rounded-lg bg-yellow-100 dark:bg-yellow-900">
                        <FolderOpen className="h-8 w-8 text-yellow-600 dark:text-yellow-300" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold truncate pr-8">{folder.name}</h3>
                          {folder.is_system && (
                            <Badge variant="secondary" className="text-xs">Sistema</Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground truncate mt-1">
                          {folder.description || 'Sem descrição'}
                        </p>
                        <div className="flex items-center gap-3 mt-3 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <FolderOpen className="h-3 w-3" />
                            {folder.subfolder_count}
                          </span>
                          <span className="flex items-center gap-1">
                            <FileText className="h-3 w-3" />
                            {folder.document_count}
                          </span>
                          <span>{formatFileSize(folder.total_size_bytes)}</span>
                        </div>
                        <div className="mt-2 flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {FOLDER_TYPES.find(t => t.value === folder.folder_type)?.label || folder.folder_type}
                          </Badge>
                          {folder.is_public ? (
                            <Unlock className="h-3 w-3 text-green-500" />
                          ) : (
                            <Lock className="h-3 w-3 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>

              {/* Menu de ações */}
              {!folder.is_system && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2 h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => e.preventDefault()}
                    >
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={(e) => openEditDialog(folder, e as unknown as React.MouseEvent)}>
                      <Edit className="h-4 w-4 mr-2" />
                      Editar
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <FolderInput className="h-4 w-4 mr-2" />
                      Mover
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      className="text-destructive"
                      onClick={(e) => openDeleteDialog(folder, e as unknown as React.MouseEvent)}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Excluir
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Info da pasta atual */}
      {currentFolder && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Informações da Pasta</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground">Tipo</p>
              <p className="font-medium">
                {FOLDER_TYPES.find(t => t.value === currentFolder.folder_type)?.label}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Subpastas</p>
              <p className="font-medium">{currentFolder.subfolder_count}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Documentos</p>
              <p className="font-medium">{currentFolder.document_count}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Tamanho Total</p>
              <p className="font-medium">{formatFileSize(currentFolder.total_size_bytes)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Visibilidade</p>
              <p className="font-medium">{currentFolder.is_public ? 'Pública' : 'Privada'}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Caminho</p>
              <p className="font-medium truncate">{currentFolder.full_path}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dialog de edição */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Pasta</DialogTitle>
            <DialogDescription>
              Altere as informações da pasta.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Nome</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Nome da pasta"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">Descrição</Label>
              <Textarea
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Descrição da pasta (opcional)"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="edit-is_public"
                checked={formData.is_public}
                onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                className="rounded"
              />
              <Label htmlFor="edit-is_public">Pasta pública</Label>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleEditFolder} disabled={!formData.name}>
              Salvar
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog de confirmação de exclusão */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir pasta?</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja excluir a pasta "{selectedFolder?.name}"?
              Esta ação não pode ser desfeita. A pasta precisa estar vazia para ser excluída.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction variant="destructive" onClick={handleDeleteFolder}>
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

export default function PastasPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    }>
      <PastasContent />
    </Suspense>
  );
}
