'use client';

import { useState, type ReactNode } from 'react';
import { cn } from '@/shared/utils/cn';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Header */}
      <Header sidebarCollapsed={sidebarCollapsed} />

      {/* Main Content */}
      <main
        className={cn(
          'pt-16 min-h-screen transition-all duration-300',
          sidebarCollapsed ? 'pl-20' : 'pl-64'
        )}
      >
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
