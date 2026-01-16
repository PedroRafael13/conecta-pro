'use client';

import { useState, useEffect, type ReactNode } from 'react';
import { cn } from '@/shared/utils/cn';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarMobileOpen, setSidebarMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  // Detectar tamanho da tela
  useEffect(() => {
    const checkScreenSize = () => {
      const width = window.innerWidth;
      setIsMobile(width < 768); // md breakpoint
      setIsTablet(width >= 768 && width < 1024); // lg breakpoint

      // Auto-collapse no tablet
      if (width >= 768 && width < 1024) {
        setSidebarCollapsed(true);
      }

      // Fechar sidebar mobile quando redimensionar para desktop
      if (width >= 768) {
        setSidebarMobileOpen(false);
      }
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const toggleSidebar = () => {
    if (isMobile) {
      setSidebarMobileOpen(!sidebarMobileOpen);
    } else {
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };

  const closeMobileSidebar = () => {
    setSidebarMobileOpen(false);
  };

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Overlay para mobile */}
      {isMobile && sidebarMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={closeMobileSidebar}
        />
      )}

      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        mobileOpen={sidebarMobileOpen}
        isMobile={isMobile}
        isTablet={isTablet}
        onToggle={toggleSidebar}
        onClose={closeMobileSidebar}
      />

      {/* Header */}
      <Header
        sidebarCollapsed={sidebarCollapsed}
        isMobile={isMobile}
        isTablet={isTablet}
        onMenuClick={toggleSidebar}
      />

      {/* Main Content */}
      <main
        className={cn(
          'pt-16 min-h-screen transition-all duration-300',
          // Mobile: sem padding lateral
          isMobile && 'pl-0',
          // Tablet: sidebar colapsada
          isTablet && 'pl-20',
          // Desktop: sidebar normal ou colapsada
          !isMobile && !isTablet && (sidebarCollapsed ? 'pl-20' : 'pl-64')
        )}
      >
        <div className={cn(
          'p-4 md:p-6',
          'max-w-full overflow-x-hidden'
        )}>
          {children}
        </div>
      </main>
    </div>
  );
}
