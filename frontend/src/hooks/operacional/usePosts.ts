/**
 * Posts Hooks - Gestão de Postos de Trabalho
 *
 * Re-exports dos hooks Orval do módulo operacional-postos
 */

import {
  useListPostsApiV1OperacionalPostsGet,
  useCreatePostApiV1OperacionalPostsPost,
  useGetPostApiV1OperacionalPostsPostIdGet,
  useUpdatePostApiV1OperacionalPostsPostIdPatch,
  useDeletePostApiV1OperacionalPostsPostIdDelete,
  useGetPostStatsApiV1OperacionalPostsPostIdStatsGet,
  useGetActivePostsApiV1OperacionalPostsActiveGet,
  useGetPostsByCondominiumApiV1OperacionalPostsCondominiumCondominiumIdGet,
  useGetVacantPostsApiV1OperacionalPostsVacantGet,
} from '@/types/generated/operacional/operacional-postos/operacional-postos';

// List & Read
export const usePosts = useListPostsApiV1OperacionalPostsGet;
export const usePost = useGetPostApiV1OperacionalPostsPostIdGet;
export const useActivePosts = useGetActivePostsApiV1OperacionalPostsActiveGet;
export const usePostsByCondominium = useGetPostsByCondominiumApiV1OperacionalPostsCondominiumCondominiumIdGet;
export const useVacantPosts = useGetVacantPostsApiV1OperacionalPostsVacantGet;
export const usePostStats = useGetPostStatsApiV1OperacionalPostsPostIdStatsGet;

// Mutations
export const useCreatePost = useCreatePostApiV1OperacionalPostsPost;
export const useUpdatePost = useUpdatePostApiV1OperacionalPostsPostIdPatch;
export const useDeletePost = useDeletePostApiV1OperacionalPostsPostIdDelete;

// Re-export types
export type {
  PostCreate,
  PostUpdate,
  PostResponse,
  PostStats,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
