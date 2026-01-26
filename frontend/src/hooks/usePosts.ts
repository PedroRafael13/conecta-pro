'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { postsService } from '@/lib/services/posts';
import type { Post, PostFilter, PostStats, PaginatedResponse } from '@/types/operacional';
import { getErrorMessage } from '@/lib/api';

interface UsePostsOptions {
  autoLoad?: boolean;
  initialPage?: number;
  initialPageSize?: number;
  initialFilters?: PostFilter;
}

interface UsePostsReturn {
  posts: Post[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: PostFilter;
  setFilters: React.Dispatch<React.SetStateAction<PostFilter>>;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => Promise<void>;
}

export function usePosts(options: UsePostsOptions = {}): UsePostsReturn {
  const {
    autoLoad = true,
    initialPage = 1,
    initialPageSize = 20,
    initialFilters = {},
  } = options;

  const [posts, setPosts] = useState<Post[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<PostFilter>(initialFilters);

  const loadPosts = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await postsService.list(page, pageSize, filters);
      setPosts(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setPosts([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, filters]);

  useEffect(() => {
    if (autoLoad) {
      loadPosts();
    }
  }, [autoLoad, loadPosts]);

  return {
    posts,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters,
    setPage,
    setPageSize,
    refresh: loadPosts,
  };
}

// Hook para estatísticas de postos
export function usePostStats() {
  const [stats, setStats] = useState<PostStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await postsService.getStats();
      setStats(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  return { stats, isLoading, error, refresh: loadStats };
}

// Hook para um posto específico
export function usePost(id: string | null) {
  const [post, setPost] = useState<Post | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPost = useCallback(async () => {
    if (!id) {
      setPost(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await postsService.getById(id);
      setPost(data);
    } catch (err) {
      setError(getErrorMessage(err));
      setPost(null);
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadPost();
  }, [loadPost]);

  return { post, isLoading, error, refresh: loadPost };
}
