'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import {
  FileText,
  Upload,
  Search,
  Download,
  Eye,
  MoreVertical,
  File,
  Image,
  FileSpreadsheet,
  FileIcon,
  Presentation,
  Trash2,
  Edit,
  FolderInput,
  X,
  CheckCircle,
  AlertCircle,
  CloudUpload,
} from 'lucide-react';
import {
  Document,
  Folder,
  formatFileSize,
  DOCUMENT_TYPES,
  DOCUMENT_CATEGORIES,
  DOCUMENT_STATUS,
  getFileIcon,
} from '@/types/generated/ged/conectaPROMóduloGED.schemas';
import { customInstance } from '@/lib/api-client';

interface UploadFile {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export default function ArquivosPage() {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [documents, setDocuments] = useState<Document[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    folder_id: 'all',
    document_type: 'all',
    category: 'all',
    status: 'all',
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Upload state
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFolderId, setSelectedFolderId] = useState<string>('');
  const [selectedDocType, setSelectedDocType] = useState<string>('outros');
  const [selectedCategory, setSelectedCategory] = useState<string>('outros');

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);

      // Carregar pastas para o filtro
      const foldersResponse = await customInstance<{ items: Folder[] }>({
        url: '/api/v1/ged/folders/',
        method: 'GET',
        params: { page_size: 100 },
      });
      setFolders(foldersResponse.items);

      // Carregar documentos
      const params: Record<string, string | number> = {
        page,
        page_size: 20,
      };
      if (filters.folder_id && filters.folder_id !== 'all') params.folder_id = filters.folder_id;
      if (filters.document_type && filters.document_type !== 'all') params.document_type = filters.document_type;
      if (filters.category && filters.category !== 'all') params.category = filters.category;
      if (filters.status && filters.status !== 'all') params.status = filters.status;
      if (search) params.search = search;

      const response = await customInstance<{ items: Document[]; pages: number }>({
        url: '/api/v1/ged/documents/',
        method: 'GET',
        params,
      });
      setDocuments(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      toast({
        variant: 'destructive',
        title: 'Erro ao carregar',
        description: 'Não foi possível carregar os documentos.',
      });
    } finally {
      setLoading(false);
    }
  }, [page, filters, search, toast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Ícone do arquivo
  const FileTypeIcon = ({ extension }: { extension: string }) => {
    const iconName = getFileIcon(extension);
    const icons: Record<string, typeof File> = {
      FileText: FileText,
      Table: FileSpreadsheet,
      Presentation: Presentation,
      Image: Image,
      File: File,
    };
    const Icon = icons[iconName] || FileIcon;
    return <Icon className="h-5 w-5" />;
  };

  // Status badge
  const getStatusBadge = (status: string) => {
    const statusInfo = DOCUMENT_STATUS.find(s => s.value === status);
    const colors: Record<string, string> = {
      gray: 'bg-gray-100 text-gray-800',
      yellow: 'bg-yellow-100 text-yellow-800',
      green: 'bg-green-100 text-green-800',
      red: 'bg-red-100 text-red-800',
      blue: 'bg-blue-100 text-blue-800',
      orange: 'bg-orange-100 text-orange-800',
    };
    return (
      <Badge className={colors[statusInfo?.color || 'gray'] + ' border-0'}>
        {statusInfo?.label || status}
      </Badge>
    );
  };

  // Drag and Drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    addFilesToUpload(files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      addFilesToUpload(files);
    }
  };

  const addFilesToUpload = (files: File[]) => {
    const newFiles: UploadFile[] = files.map(file => ({
      file,
      progress: 0,
      status: 'pending',
    }));
    setUploadFiles(prev => [...prev, ...newFiles]);
  };

  const removeFileFromUpload = (index: number) => {
    setUploadFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Upload de arquivos
  const handleUpload = async () => {
    if (uploadFiles.length === 0) {
      toast({
        variant: 'destructive',
        title: 'Nenhum arquivo selecionado',
        description: 'Selecione ao menos um arquivo para fazer upload.',
      });
      return;
    }

    for (let i = 0; i < uploadFiles.length; i++) {
      const uploadFile = uploadFiles[i];
      if (uploadFile.status !== 'pending') continue;

      setUploadFiles(prev => prev.map((f, idx) =>
        idx === i ? { ...f, status: 'uploading', progress: 0 } : f
      ));

      try {
        // Simular progresso (em produção seria via XMLHttpRequest com upload progress)
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 100));
          setUploadFiles(prev => prev.map((f, idx) =>
            idx === i ? { ...f, progress } : f
          ));
        }

        // Criar FormData para upload
        const formData = new FormData();
        formData.append('file', uploadFile.file);
        formData.append('title', uploadFile.file.name.split('.')[0]);
        formData.append('document_type', selectedDocType);
        formData.append('category', selectedCategory);
        if (selectedFolderId) {
          formData.append('folder_id', selectedFolderId);
        }

        await customInstance({
          url: '/api/v1/ged/documents/upload',
          method: 'POST',
          data: formData,
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        setUploadFiles(prev => prev.map((f, idx) =>
          idx === i ? { ...f, status: 'success', progress: 100 } : f
        ));
      } catch (error) {
        console.error('Erro no upload:', error);
        setUploadFiles(prev => prev.map((f, idx) =>
          idx === i ? { ...f, status: 'error', error: 'Falha no upload' } : f
        ));
      }
    }

    const successCount = uploadFiles.filter(f => f.status === 'success').length;
    const errorCount = uploadFiles.filter(f => f.status === 'error').length;

    if (successCount > 0) {
      toast({
        variant: 'success',
        title: 'Upload concluído',
        description: `${successCount} arquivo(s) enviado(s) com sucesso.`,
      });
      loadData();
    }

    if (errorCount > 0) {
      toast({
        variant: 'destructive',
        title: 'Alguns uploads falharam',
        description: `${errorCount} arquivo(s) não puderam ser enviados.`,
      });
    }
  };

  const closeUploadDialog = () => {
    setUploadDialogOpen(false);
    setUploadFiles([]);
    setSelectedFolderId('');
    setSelectedDocType('outros');
    setSelectedCategory('outros');
  };

  // Ações do documento
  const handleView = async (doc: Document) => {
    try {
      const viewData = await customInstance<{ url: string }>({
        url: `/api/v1/ged/documents/${doc.id}/view-url`,
        method: 'GET',
      });
      window.open(viewData.url, '_blank');
    } catch (error) {
      console.error('Erro ao visualizar:', error);
      toast({
        variant: 'destructive',
        title: 'Erro ao abrir documento',
        description: 'Não foi possível abrir o documento.',
      });
    }
  };

  const handleDownload = async (doc: Document) => {
    try {
      const blob = await customInstance<Blob>({
        url: `/api/v1/ged/documents/${doc.id}/download`,
        method: 'GET',
        responseType: 'blob',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${doc.file_name}.${doc.file_extension}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast({
        variant: 'success',
        title: 'Download iniciado',
        description: `Baixando ${doc.title}...`,
      });
    } catch (error) {
      console.error('Erro no download:', error);
      toast({
        variant: 'destructive',
        title: 'Erro no download',
        description: 'Não foi possível baixar o documento.',
      });
    }
  };

  const handleDelete = async () => {
    if (!selectedDocument) return;
    try {
      await customInstance({
        url: `/api/v1/ged/documents/${selectedDocument.id}`,
        method: 'DELETE',
      });
      setDeleteDialogOpen(false);
      toast({
        variant: 'success',
        title: 'Documento excluído',
        description: `O documento "${selectedDocument.title}" foi excluído.`,
      });
      setSelectedDocument(null);
      loadData();
    } catch (error) {
      console.error('Erro ao excluir:', error);
      toast({
        variant: 'destructive',
        title: 'Erro ao excluir',
        description: 'Não foi possível excluir o documento.',
      });
    }
  };

  const openDeleteDialog = (doc: Document) => {
    setSelectedDocument(doc);
    setDeleteDialogOpen(true);
  };

  const hasActiveFilters = Object.values(filters).some(v => v && v !== 'all') || search;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Arquivos</h1>
          <p className="text-muted-foreground">
            Gerencie seus documentos e arquivos
          </p>
        </div>
        <Button onClick={() => setUploadDialogOpen(true)}>
          <Upload className="h-4 w-4 mr-2" />
          Upload
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar documentos..."
                className="pl-10"
              />
            </div>
            <Select
              value={filters.folder_id}
              onValueChange={(value) => setFilters({ ...filters, folder_id: value })}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Pasta" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas as pastas</SelectItem>
                {folders.map((folder) => (
                  <SelectItem key={folder.id} value={folder.id}>
                    {folder.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={filters.document_type}
              onValueChange={(value) => setFilters({ ...filters, document_type: value })}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os tipos</SelectItem>
                {DOCUMENT_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={filters.status}
              onValueChange={(value) => setFilters({ ...filters, status: value })}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os status</SelectItem>
                {DOCUMENT_STATUS.map((status) => (
                  <SelectItem key={status.value} value={status.value}>
                    {status.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium">Nenhum documento encontrado</h3>
              <p className="mt-2">
                {hasActiveFilters
                  ? 'Tente ajustar os filtros'
                  : 'Faça o upload do seu primeiro documento'}
              </p>
              <Button className="mt-4" onClick={() => setUploadDialogOpen(true)}>
                <Upload className="h-4 w-4 mr-2" />
                Upload
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Documento</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Tamanho</TableHead>
                  <TableHead>Atualizado</TableHead>
                  <TableHead className="w-[100px]">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded bg-muted">
                          <FileTypeIcon extension={doc.file_extension} />
                        </div>
                        <div>
                          <p className="font-medium">{doc.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {doc.file_name}.{doc.file_extension}
                          </p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {DOCUMENT_TYPES.find(t => t.value === doc.document_type)?.label || doc.document_type}
                    </TableCell>
                    <TableCell>
                      {DOCUMENT_CATEGORIES.find(c => c.value === doc.category)?.label || doc.category}
                    </TableCell>
                    <TableCell>{getStatusBadge(doc.status)}</TableCell>
                    <TableCell>{formatFileSize(doc.file_size_bytes)}</TableCell>
                    <TableCell>
                      {new Date(doc.updated_at).toLocaleDateString('pt-BR')}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleView(doc)} title="Visualizar">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDownload(doc)} title="Download">
                          <Download className="h-4 w-4" />
                        </Button>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleView(doc)}>
                              <Eye className="h-4 w-4 mr-2" />
                              Visualizar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDownload(doc)}>
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </DropdownMenuItem>
                            <DropdownMenuItem>
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
                              onClick={() => openDeleteDialog(doc)}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Excluir
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Anterior
          </Button>
          <span className="text-sm text-muted-foreground">
            Página {page} de {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Próxima
          </Button>
        </div>
      )}

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Upload de Documentos</DialogTitle>
            <DialogDescription>
              Arraste arquivos ou clique para selecionar. Você pode enviar múltiplos arquivos.
            </DialogDescription>
          </DialogHeader>

          {/* Drag and Drop Zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging
                ? 'border-primary bg-primary/5'
                : 'border-muted-foreground/25 hover:border-primary/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <CloudUpload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium">
              {isDragging ? 'Solte os arquivos aqui' : 'Arraste arquivos ou clique para selecionar'}
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              PDF, Word, Excel, imagens e outros formatos
            </p>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif,.txt"
            />
          </div>

          {/* Upload Options */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Pasta destino</Label>
              <Select value={selectedFolderId} onValueChange={setSelectedFolderId}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Raiz</SelectItem>
                  {folders.map((folder) => (
                    <SelectItem key={folder.id} value={folder.id}>
                      {folder.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Tipo de documento</Label>
              <Select value={selectedDocType} onValueChange={setSelectedDocType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DOCUMENT_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Categoria</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DOCUMENT_CATEGORIES.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value}>
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Files List */}
          {uploadFiles.length > 0 && (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {uploadFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 bg-muted rounded-lg"
                >
                  <div className="p-2 bg-background rounded">
                    <FileIcon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file.file.name}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">
                        {formatFileSize(file.file.size)}
                      </span>
                      {file.status === 'uploading' && (
                        <div className="flex-1">
                          <Progress value={file.progress} className="h-1" />
                        </div>
                      )}
                      {file.status === 'success' && (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                      {file.status === 'error' && (
                        <AlertCircle className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                  </div>
                  {file.status === 'pending' && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => removeFileFromUpload(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={closeUploadDialog}>
              Cancelar
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploadFiles.length === 0 || uploadFiles.some(f => f.status === 'uploading')}
            >
              <Upload className="h-4 w-4 mr-2" />
              Enviar {uploadFiles.length > 0 && `(${uploadFiles.filter(f => f.status === 'pending').length})`}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir documento?</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja excluir "{selectedDocument?.title}"?
              Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction variant="destructive" onClick={handleDelete}>
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
