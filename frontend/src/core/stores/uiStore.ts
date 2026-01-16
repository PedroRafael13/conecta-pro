import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  globalLoading: boolean;
  loadingMessage: string | null;
}

interface UIActions {
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebarCollapse: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setGlobalLoading: (loading: boolean, message?: string) => void;
}

type UIStore = UIState & UIActions;

export const useUIStore = create<UIStore>((set) => ({
  // State
  sidebarOpen: true,
  sidebarCollapsed: false,
  globalLoading: false,
  loadingMessage: null,

  // Actions
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),

  toggleSidebarCollapse: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  setSidebarCollapsed: (collapsed: boolean) =>
    set({ sidebarCollapsed: collapsed }),

  setGlobalLoading: (loading: boolean, message?: string) =>
    set({
      globalLoading: loading,
      loadingMessage: loading ? message || null : null,
    }),
}));

export default useUIStore;
