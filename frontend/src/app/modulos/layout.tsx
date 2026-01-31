'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import {
  Shield, ChevronLeft, ChevronRight, Menu, X,
  UserPlus, Target, Building2, Contact, FileText,
  FileSignature, ClipboardList, Calendar, CalendarDays,
  MapPin, UserCheck, AlertTriangle, Route, LogIn,
  Monitor, Bell, TrendingDown, TrendingUp, Activity,
  Receipt, CheckCircle2, FileSpreadsheet, FileCode,
  Award, File, Folder, Package, Repeat, Settings,
  Camera, Fingerprint, Video, Webhook, LayoutDashboard,
  ClipboardCheck, PieChart, Users, Lock, Building, Eye, Database,
  Clock, Megaphone
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { getModuleByPath, modules } from '@/config/modules';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/ThemeToggle';
import { SearchTrigger } from '@/components/SearchTrigger';
import { NotificationBell } from '@/features/notifications';
import { QuickActions } from '@/components/QuickActions';

// Mapeamento de ícones para submódulos
const iconMap: Record<string, React.ElementType> = {
  UserPlus, Target, Building2, Contact, FileText,
  FileSignature, ClipboardList, Calendar, CalendarDays,
  MapPin, UserCheck, AlertTriangle, Route, LogIn,
  Monitor, Bell, TrendingDown, TrendingUp, Activity,
  Receipt, CheckCircle2, FileSpreadsheet, FileCode,
  Award, File, Folder, Package, Repeat, Settings,
  Camera, Fingerprint, Video, Webhook, LayoutDashboard,
  ClipboardCheck, PieChart, Users, Lock, Building, Eye, Database,
  Clock, Megaphone
};

export default function ModulosLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Buscar módulo atual
  const currentModule = getModuleByPath(pathname);

  // Redirecionar se não autenticado
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !currentModule) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse-slow text-[hsl(var(--primary))]">
          <Shield className="w-12 h-12" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-[hsl(var(--background))]">
      {/* Sidebar - Desktop */}
      <aside
        className={cn(
          'hidden lg:flex flex-col fixed inset-y-0 left-0 z-40',
          'bg-[hsl(var(--card))] border-r border-[hsl(var(--border))]',
          'transition-all duration-300 ease-in-out',
          sidebarOpen ? 'w-64' : 'w-16'
        )}
      >
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[hsl(var(--border))]">
          {sidebarOpen && (
            <button
              onClick={() => router.push('/dashboard')}
              className="flex items-center gap-2 text-[hsl(var(--foreground))] hover:text-[hsl(var(--primary))] transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              <span className="text-sm font-medium">Dashboard</span>
            </button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={cn(!sidebarOpen && 'mx-auto')}
          >
            {sidebarOpen ? (
              <ChevronLeft className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </Button>
        </div>

        {/* Module title */}
        <div className={cn(
          'px-4 py-4 border-b border-[hsl(var(--border))]',
          !sidebarOpen && 'px-2'
        )}>
          {sidebarOpen ? (
            <>
              <h2 className="font-semibold text-[hsl(var(--foreground))]">
                {currentModule.title}
              </h2>
              <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5 line-clamp-1">
                {currentModule.description}
              </p>
            </>
          ) : (
            <div className="w-8 h-8 mx-auto rounded-lg bg-[hsl(var(--primary))]/10 flex items-center justify-center">
              <Shield className="w-4 h-4 text-[hsl(var(--primary))]" />
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4" data-tour="sidebar-nav">
          <ul className="space-y-1 px-2">
            {currentModule.subModules.map((subModule) => {
              const Icon = iconMap[subModule.icon] || FileText;
              const isActive = pathname === subModule.href;

              return (
                <li key={subModule.id}>
                  <button
                    onClick={() => router.push(subModule.href)}
                    className={cn(
                      'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg',
                      'text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'bg-[hsl(var(--primary))]/10 text-[hsl(var(--primary))] border border-[hsl(var(--primary))]/30'
                        : 'text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--secondary))] hover:text-[hsl(var(--foreground))]',
                      !sidebarOpen && 'justify-center px-0'
                    )}
                    title={!sidebarOpen ? subModule.title : undefined}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    {sidebarOpen && (
                      <>
                        <span className="flex-1 text-left">{subModule.title}</span>
                        {subModule.badge !== undefined && (
                          <span className="px-1.5 py-0.5 text-xs bg-[hsl(var(--primary))]/20 text-[hsl(var(--primary))] rounded">
                            {subModule.badge}
                          </span>
                        )}
                      </>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer com ThemeToggle */}
        <div className={cn(
          'p-4 border-t border-[hsl(var(--border))]',
          !sidebarOpen && 'flex justify-center'
        )}>
          <ThemeToggle />
        </div>
      </aside>

      {/* Mobile menu overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar - Mobile */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 lg:hidden',
          'bg-[hsl(var(--card))] border-r border-[hsl(var(--border))]',
          'transform transition-transform duration-300 ease-in-out',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header mobile */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[hsl(var(--border))]">
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              router.push('/dashboard');
            }}
            className="flex items-center gap-2 text-[hsl(var(--foreground))]"
          >
            <ChevronLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Dashboard</span>
          </button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setMobileMenuOpen(false)}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Module title mobile */}
        <div className="px-4 py-4 border-b border-[hsl(var(--border))]">
          <h2 className="font-semibold text-[hsl(var(--foreground))]">
            {currentModule.title}
          </h2>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
            {currentModule.description}
          </p>
        </div>

        {/* Navigation mobile */}
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-2">
            {currentModule.subModules.map((subModule) => {
              const Icon = iconMap[subModule.icon] || FileText;
              const isActive = pathname === subModule.href;

              return (
                <li key={subModule.id}>
                  <button
                    onClick={() => {
                      router.push(subModule.href);
                      setMobileMenuOpen(false);
                    }}
                    className={cn(
                      'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg',
                      'text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'bg-[hsl(var(--primary))]/10 text-[hsl(var(--primary))]'
                        : 'text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--secondary))]'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{subModule.title}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <div
        className={cn(
          'flex-1 flex flex-col min-h-screen transition-all duration-300',
          sidebarOpen ? 'lg:ml-64' : 'lg:ml-16'
        )}
      >
        {/* Header - Desktop e Mobile */}
        <header className="sticky top-0 z-30 h-14 flex items-center gap-3 px-4 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
          {/* Mobile menu toggle */}
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setMobileMenuOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </Button>

          {/* Title mobile */}
          <span className="font-medium text-[hsl(var(--foreground))] flex-1 lg:hidden">
            {currentModule.title}
          </span>

          {/* Search trigger - sempre visível */}
          <div className="hidden sm:block flex-1 max-w-md" data-tour="global-search">
            <SearchTrigger />
          </div>

          {/* Spacer para desktop */}
          <div className="hidden lg:block flex-1" />

          {/* Actions */}
          <div className="flex items-center gap-2">
            <QuickActions />
            <NotificationBell />
            <ThemeToggle />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
