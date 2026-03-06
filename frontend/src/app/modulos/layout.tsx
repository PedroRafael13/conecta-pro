'use client';

import { Shield, ShieldCheck, ChevronLeft, ChevronRight, Menu, X, UserPlus, Target, Building2, Contact, FileText, FileSignature, ClipboardList, Calendar, CalendarDays, MapPin, UserCheck, AlertTriangle, Route, LogIn, Monitor, Bell, TrendingDown, TrendingUp, Activity, Receipt, CheckCircle2, FileSpreadsheet, FileCode, Award, File, Folder, Package, Repeat, Settings, Camera, Fingerprint, Video, Webhook, LayoutDashboard, ClipboardCheck, PieChart, Users, Lock, Building, Eye, Database, Clock, Megaphone, ShoppingCart, Calculator, Trash2, Key, RefreshCw, ToggleRight, Landmark, DollarSign, CreditCard, Wallet, Server, Zap, Plug, Truck } from 'lucide-react';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Image from 'next/image';
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
  Clock, Megaphone, ShieldCheck, ShoppingCart, Calculator, Trash2, Key,
  RefreshCw, ToggleRight, Landmark, DollarSign, CreditCard,
  Wallet, Server, Zap, Plug, Truck
};

export default function ModulosLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuth();
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
          {sidebarOpen ? (
            <button
              onClick={() => router.push('/dashboard')}
              className="flex items-center gap-2.5 text-[hsl(var(--foreground))] hover:text-[hsl(var(--primary))] transition-colors duration-200"
            >
              <Image
                src="/images/logo-icon.png"
                alt="Conecta PRO"
                width={28}
                height={28}
                className="flex-shrink-0"
              />
              <span className="text-sm font-semibold tracking-tight">Conecta PRO</span>
            </button>
          ) : (
            <button
              onClick={() => setSidebarOpen(true)}
              className="mx-auto hover:opacity-80 transition-opacity duration-200"
              title="Expandir menu"
            >
              <Image
                src="/images/logo-icon.png"
                alt="Conecta PRO"
                width={28}
                height={28}
              />
            </button>
          )}
          {sidebarOpen && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(false)}
              className="transition-colors duration-200"
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Module title */}
        <div className={cn(
          'border-b border-[hsl(var(--border))]',
          sidebarOpen ? 'px-4 py-4 gradient-brand-subtle' : 'px-2 py-4'
        )}>
          {sidebarOpen ? (
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-brand-500/10 flex items-center justify-center flex-shrink-0">
                <Shield className="w-[18px] h-[18px] text-brand-500" />
              </div>
              <div className="min-w-0">
                <h2 className="font-semibold text-[hsl(var(--foreground))] text-sm">
                  {currentModule.title}
                </h2>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5 line-clamp-1">
                  {currentModule.description}
                </p>
              </div>
            </div>
          ) : (
            <div className="w-9 h-9 mx-auto rounded-xl bg-brand-500/10 flex items-center justify-center">
              <Shield className="w-[18px] h-[18px] text-brand-500" />
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4" data-tour="sidebar-nav">
          <div className={cn('flex flex-col gap-1 px-2', sidebarOpen ? 'gap-1' : 'gap-3')}>
            {currentModule.subModules.map((subModule) => {
              const Icon = iconMap[subModule.icon] || FileText;
              const isActive = pathname === subModule.href;

              return sidebarOpen ? (
                <button
                  key={subModule.id}
                  onClick={() => router.push(subModule.href)}
                  className={cn(
                    'relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl',
                    'text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-[hsl(var(--primary))]/5 text-[hsl(var(--primary))]'
                      : 'text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--secondary))]/80 hover:text-[hsl(var(--foreground))]'
                  )}
                >
                  {isActive && (
                    <span
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full"
                      style={{ background: 'linear-gradient(180deg, hsl(var(--primary)), #f97707)' }}
                    />
                  )}
                  <Icon className="w-[18px] h-[18px] flex-shrink-0" />
                  <span className="flex-1 text-left">{subModule.title}</span>
                  {subModule.badge !== undefined && (
                    <span className="px-1.5 py-0.5 text-xs bg-brand-500/15 text-brand-500 rounded-md font-semibold">
                      {subModule.badge}
                    </span>
                  )}
                </button>
              ) : (
                <button
                  key={subModule.id}
                  onClick={() => router.push(subModule.href)}
                  className={cn(
                    'relative w-full flex flex-col items-center justify-center py-2.5 rounded-xl',
                    'transition-all duration-200',
                    isActive
                      ? 'text-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5'
                      : 'text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--secondary))]/80 hover:text-[hsl(var(--foreground))]'
                  )}
                  title={subModule.title}
                >
                  <Icon className="w-[18px] h-[18px]" />
                  {isActive && (
                    <span className="absolute bottom-1 w-1 h-1 rounded-full bg-brand-500" />
                  )}
                </button>
              );
            })}
          </div>
        </nav>

        {/* Footer with user info + ThemeToggle */}
        <div className={cn(
          'p-3 border-t border-[hsl(var(--border))]',
          sidebarOpen ? 'flex items-center gap-3' : 'flex flex-col items-center gap-2'
        )}>
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold text-white"
            style={{ background: 'linear-gradient(135deg, hsl(var(--primary)), #f97707)' }}
            title={user?.name || ''}
          >
            {user?.name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          {sidebarOpen && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[hsl(var(--foreground))] truncate">
                {user?.name || 'Usuario'}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))] truncate">
                {user?.role || ''}
              </p>
            </div>
          )}
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
          'fixed inset-y-0 left-0 z-50 w-72 lg:hidden',
          'bg-[hsl(var(--card))] border-r border-[hsl(var(--border))]',
          'transform transition-transform duration-200 ease-out',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Subtle gradient overlay at top */}
        <div className="absolute top-0 left-0 right-0 h-32 pointer-events-none opacity-[0.05] gradient-brand rounded-none" />

        {/* Header mobile */}
        <div className="relative h-16 flex items-center justify-between px-4 border-b border-[hsl(var(--border))]">
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              router.push('/dashboard');
            }}
            className="flex items-center gap-2.5 text-[hsl(var(--foreground))] hover:text-[hsl(var(--primary))] transition-colors duration-200"
          >
            <Image
              src="/images/logo-icon.png"
              alt="Conecta PRO"
              width={24}
              height={24}
              className="flex-shrink-0"
            />
            <span className="text-sm font-semibold tracking-tight">Conecta PRO</span>
          </button>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="w-8 h-8 flex items-center justify-center rounded-lg bg-brand-500 text-white transition-colors duration-200 hover:bg-brand-500/90"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Module title mobile */}
        <div className="relative px-4 py-4 border-b border-[hsl(var(--border))] gradient-brand-subtle">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-brand-500/10 flex items-center justify-center flex-shrink-0">
              <Shield className="w-[18px] h-[18px] text-brand-500" />
            </div>
            <div className="min-w-0">
              <h2 className="font-semibold text-[hsl(var(--foreground))] text-sm">
                {currentModule.title}
              </h2>
              <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5 line-clamp-1">
                {currentModule.description}
              </p>
            </div>
          </div>
        </div>

        {/* Navigation mobile */}
        <nav className="relative flex-1 overflow-y-auto py-4">
          <div className="flex flex-col gap-1 px-2">
            {currentModule.subModules.map((subModule) => {
              const Icon = iconMap[subModule.icon] || FileText;
              const isActive = pathname === subModule.href;

              return (
                <button
                  key={subModule.id}
                  onClick={() => {
                    router.push(subModule.href);
                    setMobileMenuOpen(false);
                  }}
                  className={cn(
                    'relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl',
                    'text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-[hsl(var(--primary))]/5 text-[hsl(var(--primary))]'
                      : 'text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--secondary))]/80 hover:text-[hsl(var(--foreground))]'
                  )}
                >
                  {isActive && (
                    <span
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full"
                      style={{ background: 'linear-gradient(180deg, hsl(var(--primary)), #f97707)' }}
                    />
                  )}
                  <Icon className="w-[18px] h-[18px] flex-shrink-0" />
                  <span>{subModule.title}</span>
                </button>
              );
            })}
          </div>
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
        <header className="sticky top-0 z-30 h-14 flex items-center gap-3 px-4 bg-[hsl(var(--background))]/80 backdrop-blur-2xl shadow-sm">
          {/* Mobile menu toggle */}
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setMobileMenuOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </Button>

          {/* Logo + Title mobile */}
          <div className="flex items-center gap-2 flex-1 lg:hidden">
            <Image
              src="/images/logo-icon.png"
              alt="Conecta PRO"
              width={24}
              height={24}
              className="flex-shrink-0"
            />
            <span className="font-medium text-[hsl(var(--foreground))]">
              {currentModule.title}
            </span>
          </div>

          {/* Search trigger */}
          <div className="flex-1 max-w-md" data-tour="global-search">
            <SearchTrigger />
          </div>

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
