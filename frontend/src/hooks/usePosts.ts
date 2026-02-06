'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { customInstance } from '@/lib/api-client';
import type { Post, PostFilter, PostStats, PaginatedResponse } from '@/types/operacional';

const BASE_URL = '/api/v1/operacional/posts';

function buildParams(page: number, pageSize: number, filters?: PostFilter): string {
  const params = new URLSearchParams();
  params.append('page', String(page));
  params.append('page_size', String(pageSize));
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
  }
  return params.toString();
}

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

  const lastRequestRef = useRef<string>('');
  const errorCountRef = useRef<number>(0);
  const lastErrorTimeRef = useRef<number>(0);

  const loadPosts = useCallback(async () => {
    const requestKey = JSON.stringify({ page, pageSize, filters });
    const now = Date.now();
    if (
      requestKey === lastRequestRef.current &&
      errorCountRef.current > 0 &&
      now - lastErrorTimeRef.current < Math.min(errorCountRef.current * 2000, 30000)
    ) {
      return;
    }

    setIsLoading(true);
    setError(null);
    lastRequestRef.current = requestKey;

    try {
      const response = await customInstance<PaginatedResponse<Post>>({
        url: `${BASE_URL}/?${buildParams(page, pageSize, filters)}`,
        method: 'GET',
      });
      setPosts(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
      errorCountRef.current = 0;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erro ao carregar postos';
      setError(errorMsg);
      setPosts([]);
      errorCountRef.current += 1;
      lastErrorTimeRef.current = now;
      console.error(`[usePosts] Erro ao carregar postos (tentativa ${errorCountRef.current}):`, errorMsg);
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

export function usePostStats() {
  const [stats, setStats] = useState<PostStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await customInstance<PostStats>({
        url: `${BASE_URL}/stats`,
        method: 'GET',
      });
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar estatísticas');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  return { stats, isLoading, error, refresh: loadStats };
}

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
      const data = await customInstance<Post>({
        url: `${BASE_URL}/${id}`,
        method: 'GET',
      });
      setPost(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar posto');
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
