import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useUIStore } from '@stores/uiStore';
import { SkipLink } from '@core/components/ui/SkipLink';

/**
 * Layout principal da aplicacao com melhorias de acessibilidade.
 * Inclui:
 * - SkipLink para navegacao por teclado
 * - Landmark roles semanticos (nav, header, main)
 * - aria-labels descritivos
 */
export function MainLayout() {
  const { sidebarCollapsed } = useUIStore();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Skip Link para acessibilidade - visivel apenas com foco */}
      <SkipLink targetId="main-content" />

      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-h-screen transition-all duration-200 ${
          sidebarCollapsed ? 'lg:ml-0' : 'lg:ml-0'
        }`}
      >
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main
          id="main-content"
          role="main"
          aria-label="Conteudo principal"
          className="flex-1 p-4 lg:p-6 overflow-auto"
          tabIndex={-1}
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default MainLayout;
