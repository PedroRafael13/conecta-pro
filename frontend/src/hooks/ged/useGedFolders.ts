/**
 * GED Folders Hooks - Gestao de Pastas
 *
 * Re-exports dos hooks Orval do modulo GED pastas
 */

import {
  useListFoldersApiV1GedFoldersGet,
  useGetFolderApiV1GedFoldersFolderIdGet,
  useCreateFolderApiV1GedFoldersPost,
  useUpdateFolderApiV1GedFoldersFolderIdPut,
  useDeleteFolderApiV1GedFoldersFolderIdDelete,
  useGetRootFoldersApiV1GedFoldersRootListGet,
  useGetChildrenApiV1GedFoldersFolderIdChildrenGet,
  useGetTreeApiV1GedFoldersTreeViewGet,
  useSearchFoldersApiV1GedFoldersSearchQueryGet,
} from '@/types/generated/ged/ged-pastas/ged-pastas';

// Queries
export const useFolders = useListFoldersApiV1GedFoldersGet;
export const useFolder = useGetFolderApiV1GedFoldersFolderIdGet;
export const useRootFolders = useGetRootFoldersApiV1GedFoldersRootListGet;
export const useFolderChildren = useGetChildrenApiV1GedFoldersFolderIdChildrenGet;
export const useFolderTree = useGetTreeApiV1GedFoldersTreeViewGet;
export const useSearchFolders = useSearchFoldersApiV1GedFoldersSearchQueryGet;

// Mutations
export const useCreateFolder = useCreateFolderApiV1GedFoldersPost;
export const useUpdateFolder = useUpdateFolderApiV1GedFoldersFolderIdPut;
export const useDeleteFolder = useDeleteFolderApiV1GedFoldersFolderIdDelete;

// Re-export types
export type {
  FolderResponse,
  FolderCreate,
  FolderUpdate,
  FolderListResponse,
  ListFoldersApiV1GedFoldersGetParams,
} from '@/types/generated/ged/schemas';
