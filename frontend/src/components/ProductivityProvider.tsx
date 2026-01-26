'use client';

import { useState, useCallback, createContext, useContext } from 'react';
import { CommandPalette } from './CommandPalette';
import { GlobalSearch } from './GlobalSearch';
import { HelpOverlay } from './HelpOverlay';
import { useGlobalShortcuts } from '@/hooks/useKeyboardShortcuts';

interface ProductivityContextType {
  openSearch: () => void;
  closeSearch: () => void;
  openCommandPalette: () => void;
  closeCommandPalette: () => void;
  openHelp: () => void;
  closeHelp: () => void;
  toggleSidebar: () => void;
}

const ProductivityContext = createContext<ProductivityContextType | undefined>(undefined);

export function useProductivity() {
  const context = useContext(ProductivityContext);
  if (!context) {
    throw new Error('useProductivity must be used within ProductivityProvider');
  }
  return context;
}

interface ProductivityProviderProps {
  children: React.ReactNode;
  onSidebarToggle?: () => void;
}

export function ProductivityProvider({ children, onSidebarToggle }: ProductivityProviderProps) {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const openSearch = useCallback(() => {
    setIsCommandPaletteOpen(false);
    setIsHelpOpen(false);
    setIsSearchOpen(true);
  }, []);

  const closeSearch = useCallback(() => {
    setIsSearchOpen(false);
  }, []);

  const openCommandPalette = useCallback(() => {
    setIsSearchOpen(false);
    setIsHelpOpen(false);
    setIsCommandPaletteOpen(true);
  }, []);

  const closeCommandPalette = useCallback(() => {
    setIsCommandPaletteOpen(false);
  }, []);

  const openHelp = useCallback(() => {
    setIsSearchOpen(false);
    setIsCommandPaletteOpen(false);
    setIsHelpOpen(true);
  }, []);

  const closeHelp = useCallback(() => {
    setIsHelpOpen(false);
  }, []);

  const toggleSidebar = useCallback(() => {
    onSidebarToggle?.();
  }, [onSidebarToggle]);

  const handleModalClose = useCallback(() => {
    if (isSearchOpen) closeSearch();
    if (isCommandPaletteOpen) closeCommandPalette();
    if (isHelpOpen) closeHelp();
  }, [isSearchOpen, isCommandPaletteOpen, isHelpOpen, closeSearch, closeCommandPalette, closeHelp]);

  const shortcuts = useGlobalShortcuts({
    onSearchOpen: openSearch,
    onCommandPaletteOpen: openCommandPalette,
    onSidebarToggle: toggleSidebar,
    onHelpOpen: openHelp,
    onModalClose: handleModalClose,
  });

  const value: ProductivityContextType = {
    openSearch,
    closeSearch,
    openCommandPalette,
    closeCommandPalette,
    openHelp,
    closeHelp,
    toggleSidebar,
  };

  return (
    <ProductivityContext.Provider value={value}>
      {children}
      <CommandPalette isOpen={isCommandPaletteOpen} onClose={closeCommandPalette} />
      <GlobalSearch isOpen={isSearchOpen} onClose={closeSearch} />
      <HelpOverlay isOpen={isHelpOpen} onClose={closeHelp} shortcuts={shortcuts} />
    </ProductivityContext.Provider>
  );
}
