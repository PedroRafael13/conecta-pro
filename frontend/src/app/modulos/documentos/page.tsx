'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  FolderOpen,
  FileText,
  Upload,
  HardDrive,
  FolderPlus,
  ChevronRight,
  Eye,
  Download,
  Clock,
  AlertTriangle,
} from 'lucide-react';
import Link from 'next/link';
import { folderService, Folder, formatFileSize, FOLDER_TYPES } from '@/lib/services/ged';

export default function DocumentosPage() {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalFolders: 0,
    totalDocuments: 0,
    totalSize: 0,
  });

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await folderService.list({ page_size: 100 });
      setFolders(response.items);

      // Calcular estatísticas
      const totalDocs = response.items.reduce((acc, f) => acc + f.document_count, 0);
      const totalSize = response.items.reduce((acc, f) => acc + f.total_size_bytes, 0);

      setStats({
        totalFolders: response.total,
        totalDocuments: totalDocs,
        totalSize: totalSize,
      });
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Pastas raiz (sem parent_id)
  const rootFolders = folders.filter(f => f.is_root);

  // Ícone por tipo de pasta
  const getFolderIcon = (type: string) => {
    const folderType = FOLDER_TYPES.find(t => t.value === type);
    return folderType?.icon || 'FolderOpen';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Gestão de Documentos</h1>
          <p className="text-muted-foreground">
            Organize, armazene e gerencie seus documentos de forma segura
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/modulos/documentos/arquivos">
            <Button variant="outline">
              <Upload className="h-4 w-4 mr-2" />
              Upload
            </Button>
          </Link>
          <Link href="/modulos/documentos/pastas">
            <Button>
              <FolderPlus className="h-4 w-4 mr-2" />
              Nova Pasta
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="p-3 rounded-lg bg-blue-100 dark:bg-blue-900">
              <FolderOpen className="h-6 w-6 text-blue-600 dark:text-blue-300" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pastas</p>
              <p className="text-2xl font-bold">{stats.totalFolders}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="p-3 rounded-lg bg-green-100 dark:bg-green-900">
              <FileText className="h-6 w-6 text-green-600 dark:text-green-300" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Documentos</p>
              <p className="text-2xl font-bold">{stats.totalDocuments}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="p-3 rounded-lg bg-purple-100 dark:bg-purple-900">
              <HardDrive className="h-6 w-6 text-purple-600 dark:text-purple-300" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Armazenamento</p>
              <p className="text-2xl font-bold">{formatFileSize(stats.totalSize)}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="p-3 rounded-lg bg-orange-100 dark:bg-orange-900">
              <Clock className="h-6 w-6 text-orange-600 dark:text-orange-300" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">A vencer</p>
              <p className="text-2xl font-bold">0</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Access */}
      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/modulos/documentos/arquivos">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardContent className="flex items-center gap-4 pt-6">
              <FileText className="h-10 w-10 text-blue-500" />
              <div className="flex-1">
                <h3 className="font-semibold">Arquivos</h3>
                <p className="text-sm text-muted-foreground">Gerenciar documentos</p>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>

        <Link href="/modulos/documentos/pastas">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardContent className="flex items-center gap-4 pt-6">
              <FolderOpen className="h-10 w-10 text-yellow-500" />
              <div className="flex-1">
                <h3 className="font-semibold">Pastas</h3>
                <p className="text-sm text-muted-foreground">Organizar estrutura</p>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>

        <Link href="/modulos/documentos/kits">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardContent className="flex items-center gap-4 pt-6">
              <FolderPlus className="h-10 w-10 text-green-500" />
              <div className="flex-1">
                <h3 className="font-semibold">Kits de Documentos</h3>
                <p className="text-sm text-muted-foreground">Templates e kits</p>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Pastas Principais */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="h-5 w-5" />
            Pastas Principais
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : rootFolders.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FolderOpen className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Nenhuma pasta encontrada</p>
              <Link href="/modulos/documentos/pastas">
                <Button variant="outline" className="mt-4">
                  <FolderPlus className="h-4 w-4 mr-2" />
                  Criar Pasta
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {rootFolders.map((folder) => (
                <Link
                  key={folder.id}
                  href={`/modulos/documentos/pastas?id=${folder.id}`}
                >
                  <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
                    <CardContent className="pt-4">
                      <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900">
                          <FolderOpen className="h-6 w-6 text-yellow-600 dark:text-yellow-300" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium truncate">{folder.name}</h4>
                          <p className="text-xs text-muted-foreground truncate">
                            {folder.description || 'Sem descrição'}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline" className="text-xs">
                              {folder.document_count} docs
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {formatFileSize(folder.total_size_bytes)}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Atividade Recente */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Atividade Recente
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>Nenhuma atividade recente</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
