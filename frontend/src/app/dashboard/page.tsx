'use client';

import { Users, Briefcase, Shield, Smartphone, DollarSign, Landmark, FolderOpen, Wrench, Plug, BarChart3, Settings, Bell, Search, LogOut, User, ChevronRight } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
;
import { ModuleCard } from '@/components/ui/module-card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';
import { moduleCategories, modules } from '@/config/modules';
import { hasPermission, UserRole } from '@/types/modules';
import { cn } from '@/lib/utils';

// Mapeamento de ícones
const iconMap: Record<string, React.ElementType> = {
  Users, Briefcase, Shield, Smartphone, DollarSign, Landmark,
  FolderOpen, Wrench, Plug, BarChart3, Settings,
};

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const [search, setSearch] = useState('');
  const greeting = (() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  })();

  // Redirecionar se não autenticado
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Filtrar módulos por busca e permissão
  const filteredCategories = moduleCategories.map(category => ({
    ...category,
    modules: category.modules.filter(module => {
      // Filtro de busca
      const matchesSearch = search === '' ||
        module.title.toLowerCase().includes(search.toLowerCase()) ||
        module.description.toLowerCase().includes(search.toLowerCase());

      // Filtro de permissão (simulado - em produção viria do user.role)
      const userRole = (user?.role || 'admin') as UserRole;
      const hasAccess = hasPermission(userRole, module.permissions);

      return matchesSearch && hasAccess && module.enabled;
    }),
  })).filter(category => category.modules.length > 0);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse-slow text-[hsl(var(--primary))]">
          <Shield className="w-12 h-12" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <Image
                src="/images/logo-icon.png"
                alt="Conecta PRO"
                width={36}
                height={36}
                className="rounded-lg"
              />
              <span className="font-semibold text-[hsl(var(--foreground))]">
                Conecta PRO
              </span>
            </div>

            {/* Search - Desktop */}
            <div className="hidden md:block w-96">
              <Input
                type="search"
                placeholder="Buscar módulos..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                icon={<Search className="w-4 h-4" />}
              />
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-[hsl(var(--destructive))] rounded-full text-[10px] flex items-center justify-center text-white">
                  3
                </span>
              </Button>

              <div className="flex items-center gap-3 ml-2 pl-4 border-l border-[hsl(var(--border))]">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                    {user?.name || 'Usuário'}
                  </p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    {user?.role || 'admin'}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--destructive))]"
                >
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome */}
        <div className="mb-8 animate-slide-up">
          <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">
            {greeting}, {user?.name?.split(' ')[0] || 'Usuário'}
          </h1>
          <p className="text-[hsl(var(--muted-foreground))] mt-1">
            Selecione um módulo para começar
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-slide-up">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                <Users className="w-5 h-5 text-cyan-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">44</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Colaboradores</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <Shield className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">9</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Postos Ativos</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Briefcase className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">4</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Clientes</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-orange-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">28</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Escalas</p>
              </div>
            </div>
          </div>
        </div>

        {/* Search - Mobile */}
        <div className="md:hidden mb-6">
          <Input
            type="search"
            placeholder="Buscar módulos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            icon={<Search className="w-4 h-4" />}
          />
        </div>

        {/* Module categories */}
        <div className="space-y-10 stagger">
          {filteredCategories.map((category) => (
            <section key={category.id} className="animate-slide-up">
              <div className="flex items-center gap-2 mb-4">
                <h2 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                  {category.title}
                </h2>
                <ChevronRight className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {category.modules.map((module) => {
                  const Icon = iconMap[module.icon] || Shield;
                  return (
                    <ModuleCard
                      key={module.id}
                      id={module.id}
                      title={module.title}
                      description={module.description}
                      icon={Icon}
                      href={module.href}
                      color={module.color}
                      badge={module.badge}
                      disabled={!module.enabled}
                    />
                  );
                })}
              </div>
            </section>
          ))}
        </div>

        {/* Empty state */}
        {filteredCategories.length === 0 && (
          <div className="text-center py-16">
            <Search className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
            <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
              Nenhum módulo encontrado
            </h3>
            <p className="text-[hsl(var(--muted-foreground))] mt-1">
              Tente buscar por outro termo
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[hsl(var(--border))] mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-[hsl(var(--muted-foreground))]">
            <span>Conecta PRO v2.0.0</span>
            <span>erp.conectamais.pro</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
