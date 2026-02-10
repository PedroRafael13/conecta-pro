'use client';

import { ChevronRight, ChevronDown, Folder as FolderIcon, FolderOpen, Lock, Settings } from 'lucide-react';
import { useState, useEffect } from 'react';
import type { FolderResponse } from '@/types/generated/ged/schemas/folderResponse';
import { folderService } from '@/services/ged/folderService';
import { cn } from '@/lib/utils';

type Folder = FolderResponse;

interface FolderTreeProps {
  onFolderSelect?: (folder: Folder) => void;
  selectedFolderId?: string;
}

interface TreeNode {
  folder: Folder;
  children: TreeNode[];
  isExpanded: boolean;
}

export function FolderTree({ onFolderSelect, selectedFolderId }: FolderTreeProps) {
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTree();
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentional deps
  }, []);

  const loadTree = async () => {
    setLoading(true);
    try {
      const response = await folderService.getTree();
      // Converter flat list para tree structure
      const treeData = buildTree(response);
      setTree(treeData);
    } catch (error) {
      console.error('Erro ao carregar árvore de pastas:', error);
    } finally {
      setLoading(false);
    }
  };

  const buildTree = (folders: Folder[]): TreeNode[] => {
    const map = new Map<string, TreeNode>();
    const roots: TreeNode[] = [];

    // Criar nodes
    folders.forEach((folder) => {
      map.set(folder.id, {
        folder,
        children: [],
        isExpanded: false,
      });
    });

    // Construir hierarquia - usando Map para imutabilidade
    const updatedMap = new Map(map);
    folders.forEach((folder) => {
      const node = updatedMap.get(folder.id)!;
      if (folder.parent_id && updatedMap.has(folder.parent_id)) {
        const parentNode = updatedMap.get(folder.parent_id)!;
        updatedMap.set(folder.parent_id, {
          ...parentNode,
          children: [...parentNode.children, node],
        });
      } else {
        roots.push(node);
      }
    });

    return roots;
  };

  const toggleExpand = (nodeId: string) => {
    const updateNode = (nodes: TreeNode[]): TreeNode[] => {
      return nodes.map((node) => {
        if (node.folder.id === nodeId) {
          return { ...node, isExpanded: !node.isExpanded };
        }
        return { ...node, children: updateNode(node.children) };
      });
    };

    setTree(updateNode(tree));
  };

  const renderNode = (node: TreeNode, level: number = 0) => {
    const { folder, children, isExpanded } = node;
    const hasChildren = children.length > 0;
    const isSelected = folder.id === selectedFolderId;

    return (
      <div key={folder.id}>
        <div
          className={cn(
            'flex items-center gap-1 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-100',
            isSelected && 'bg-blue-50 hover:bg-blue-100'
          )}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => onFolderSelect?.(folder)}
        >
          {/* Expand/Collapse */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (hasChildren) toggleExpand(folder.id);
            }}
            className="p-0.5 hover:bg-gray-200 rounded"
          >
            {hasChildren ? (
              isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )
            ) : (
              <span className="w-4" />
            )}
          </button>

          {/* Ícone */}
          {isExpanded ? (
            <FolderOpen className="h-4 w-4 text-blue-500" />
          ) : (
            <FolderIcon className="h-4 w-4 text-gray-500" />
          )}

          {/* Nome */}
          <span className={cn('text-sm flex-1', isSelected && 'font-semibold')}>
            {folder.name}
          </span>

          {/* Badges */}
          <div className="flex items-center gap-1">
            {!folder.is_public && <Lock className="h-3 w-3 text-gray-400" />}
            {folder.is_system && <Settings className="h-3 w-3 text-gray-400" />}
            {folder.document_count > 0 && (
              <span className="text-xs text-gray-500">({folder.document_count})</span>
            )}
          </div>
        </div>

        {/* Children */}
        {isExpanded && children.length > 0 && (
          <div>{children.map((child) => renderNode(child, level + 1))}</div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900" />
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {tree.length === 0 ? (
        <p className="text-sm text-gray-500 p-4">Nenhuma pasta encontrada</p>
      ) : (
        tree.map((node) => renderNode(node))
      )}
    </div>
  );
}
