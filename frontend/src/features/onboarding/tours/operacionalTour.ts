import Shepherd from 'shepherd.js';

export type UserRole = 'CEO' | 'GERENTE' | 'SUPERVISOR' | 'USUARIO';

interface TourStep {
  id: string;
  attachTo?: {
    element: string;
    on: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  };
  title: string;
  text: string;
  buttons: Array<{
    text: string;
    action: () => void;
    classes?: string;
  }>;
  classes?: string;
  modalOverlayOpeningPadding?: number;
  modalOverlayOpeningRadius?: number;
}

const defaultButtons = (tour: any) => ({
  back: {
    text: 'Voltar',
    action: tour.back,
    classes: 'shepherd-button-secondary',
  },
  next: {
    text: 'Próximo',
    action: tour.next,
    classes: 'shepherd-button-primary',
  },
  skip: {
    text: 'Pular Tour',
    action: tour.cancel,
    classes: 'shepherd-button-secondary',
  },
  finish: {
    text: 'Concluir',
    action: tour.complete,
    classes: 'shepherd-button-primary',
  },
});

// Tour base para todos os perfis
const getBaseSteps = (tour: any): TourStep[] => {
  const btns = defaultButtons(tour);

  return [
    {
      id: 'welcome',
      title: '👋 Bem-vindo ao Módulo Operacional!',
      text: `
        <div class="tour-welcome">
          <p>Este tour rápido vai te mostrar as principais funcionalidades do sistema.</p>
          <p>Você pode pular este tour a qualquer momento ou refazê-lo depois no menu de ajuda.</p>
          <p class="tour-duration">⏱️ Duração estimada: 2 minutos</p>
        </div>
      `,
      buttons: [btns.skip, btns.next],
      classes: 'shepherd-welcome-modal',
    },
    {
      id: 'dashboard-kpis',
      attachTo: {
        element: '[data-tour="dashboard-kpis"]',
        on: 'bottom',
      },
      title: '📊 Indicadores em Tempo Real',
      text: `
        <p>Aqui você acompanha os principais indicadores operacionais:</p>
        <ul>
          <li>Postos ativos e inativos</li>
          <li>Colaboradores em serviço</li>
          <li>Ocorrências do dia</li>
          <li>Taxa de presença</li>
        </ul>
        <p class="tour-tip">💡 Os números atualizam automaticamente a cada 30 segundos.</p>
      `,
      buttons: [btns.back, btns.skip, btns.next],
      modalOverlayOpeningPadding: 10,
      modalOverlayOpeningRadius: 8,
    },
    {
      id: 'sidebar-nav',
      attachTo: {
        element: '[data-tour="sidebar-nav"]',
        on: 'right',
      },
      title: '🧭 Navegação Principal',
      text: `
        <p>Use a barra lateral para acessar rapidamente:</p>
        <ul>
          <li><strong>Dashboard:</strong> Visão geral</li>
          <li><strong>Postos:</strong> Gestão de postos de trabalho</li>
          <li><strong>Colaboradores:</strong> Equipe e escalas</li>
          <li><strong>Ocorrências:</strong> Registros e incidentes</li>
          <li><strong>Relatórios:</strong> Análises e exportações</li>
        </ul>
      `,
      buttons: [btns.back, btns.skip, btns.next],
      modalOverlayOpeningPadding: 5,
    },
    {
      id: 'global-search',
      attachTo: {
        element: '[data-tour="global-search"]',
        on: 'bottom',
      },
      title: '🔍 Busca Global',
      text: `
        <p>Encontre rapidamente qualquer informação:</p>
        <ul>
          <li>Pesquise por nome de colaborador</li>
          <li>Busque postos específicos</li>
          <li>Encontre ocorrências por protocolo</li>
        </ul>
        <p class="tour-tip">💡 Use Ctrl/Cmd + K como atalho!</p>
      `,
      buttons: [btns.back, btns.skip, btns.next],
      modalOverlayOpeningPadding: 8,
    },
    {
      id: 'notifications',
      attachTo: {
        element: '[data-tour="notifications"]',
        on: 'bottom',
      },
      title: '🔔 Central de Notificações',
      text: `
        <p>Mantenha-se atualizado sobre:</p>
        <ul>
          <li>Novas ocorrências registradas</li>
          <li>Faltas e atrasos de colaboradores</li>
          <li>Alertas de postos sem cobertura</li>
          <li>Aprovações pendentes</li>
        </ul>
        <p class="tour-tip">💡 Você receberá notificações em tempo real.</p>
      `,
      buttons: [btns.back, btns.skip, btns.next],
      modalOverlayOpeningPadding: 8,
    },
    {
      id: 'quick-actions',
      attachTo: {
        element: '[data-tour="quick-actions"]',
        on: 'bottom',
      },
      title: '⚡ Ações Rápidas',
      text: `
        <p>Acelere suas tarefas mais comuns:</p>
        <ul>
          <li>➕ Registrar nova ocorrência</li>
          <li>👤 Adicionar colaborador</li>
          <li>📍 Criar novo posto</li>
          <li>📊 Gerar relatório rápido</li>
        </ul>
      `,
      buttons: [btns.back, btns.skip, btns.next],
      modalOverlayOpeningPadding: 8,
    },
    {
      id: 'finish',
      title: '✅ Tour Concluído!',
      text: `
        <div class="tour-finish">
          <p>Parabéns! Você conheceu as principais funcionalidades do Módulo Operacional.</p>
          <p>Agora você está pronto para começar a usar o sistema.</p>
          <div class="tour-help">
            <p><strong>Precisa de ajuda?</strong></p>
            <ul>
              <li>📖 Acesse a documentação no menu Ajuda</li>
              <li>🔄 Refaça este tour a qualquer momento</li>
              <li>💬 Entre em contato com o suporte</li>
            </ul>
          </div>
        </div>
      `,
      buttons: [btns.finish],
      classes: 'shepherd-finish-modal',
    },
  ];
};

// Steps específicos para CEO (foco em analytics)
const getCEOSteps = (tour: any): TourStep[] => {
  const btns = defaultButtons(tour);
  const baseSteps = getBaseSteps(tour);

  // Adiciona step específico de analytics após dashboard-kpis
  const analyticsStep: TourStep = {
    id: 'analytics-dashboard',
    attachTo: {
      element: '[data-tour="analytics-charts"]',
      on: 'top',
    },
    title: '📈 Analytics Avançados',
    text: `
      <p>Como CEO, você tem acesso a análises aprofundadas:</p>
      <ul>
        <li>Tendências de performance por período</li>
        <li>Comparativos entre unidades</li>
        <li>Análise de custos operacionais</li>
        <li>Previsões baseadas em IA</li>
      </ul>
      <p class="tour-tip">💡 Use os filtros para personalizar suas análises.</p>
    `,
    buttons: [btns.back, btns.skip, btns.next],
    modalOverlayOpeningPadding: 10,
  };

  // Insere após dashboard-kpis
  return [...baseSteps.slice(0, 2), analyticsStep, ...baseSteps.slice(2)];
};

// Steps específicos para Gerente (foco em gestão)
const getGerenteSteps = (tour: any): TourStep[] => {
  const btns = defaultButtons(tour);
  const baseSteps = getBaseSteps(tour);

  const managementStep: TourStep = {
    id: 'team-management',
    attachTo: {
      element: '[data-tour="team-panel"]',
      on: 'left',
    },
    title: '👥 Gestão de Equipe',
    text: `
      <p>Como Gerente, você pode:</p>
      <ul>
        <li>Aprovar e rejeitar escalas de trabalho</li>
        <li>Gerenciar férias e licenças</li>
        <li>Avaliar desempenho da equipe</li>
        <li>Distribuir colaboradores entre postos</li>
      </ul>
      <p class="tour-tip">💡 Clique em qualquer colaborador para ver detalhes completos.</p>
    `,
    buttons: [btns.back, btns.skip, btns.next],
    modalOverlayOpeningPadding: 10,
  };

  return [...baseSteps.slice(0, 2), managementStep, ...baseSteps.slice(2)];
};

// Steps específicos para Supervisor (foco em operação)
const getSupervisorSteps = (tour: any): TourStep[] => {
  const btns = defaultButtons(tour);
  const baseSteps = getBaseSteps(tour);

  const operationStep: TourStep = {
    id: 'daily-operations',
    attachTo: {
      element: '[data-tour="operations-panel"]',
      on: 'top',
    },
    title: '🎯 Operações Diárias',
    text: `
      <p>Como Supervisor, suas principais ações são:</p>
      <ul>
        <li>Registrar ponto de colaboradores</li>
        <li>Reportar ocorrências em tempo real</li>
        <li>Verificar checklist de abertura/fechamento</li>
        <li>Confirmar presença em postos</li>
      </ul>
      <p class="tour-tip">💡 Use o app mobile para registros em campo.</p>
    `,
    buttons: [btns.back, btns.skip, btns.next],
    modalOverlayOpeningPadding: 10,
  };

  return [...baseSteps.slice(0, 2), operationStep, ...baseSteps.slice(2)];
};

// Configuração do tour Shepherd
export const createOperacionalTour = (role: UserRole = 'USUARIO') => {
  const tour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      classes: 'shepherd-theme-custom',
      scrollTo: { behavior: 'smooth', block: 'center' },
      cancelIcon: {
        enabled: true,
      },
      when: {
        show() {
          // Adiciona animação ao mostrar step
          const currentStep = tour.getCurrentStep();
          const element = currentStep?.getElement();
          if (element) {
            element.classList.add('shepherd-step-fade-in');
          }
        },
      },
    },
  });

  // Seleciona steps baseado no role do usuário
  let steps: TourStep[];
  switch (role) {
    case 'CEO':
      steps = getCEOSteps(tour);
      break;
    case 'GERENTE':
      steps = getGerenteSteps(tour);
      break;
    case 'SUPERVISOR':
      steps = getSupervisorSteps(tour);
      break;
    default:
      steps = getBaseSteps(tour);
  }

  // Adiciona steps ao tour
  steps.forEach((step) => {
    tour.addStep(step);
  });

  // Event listeners
  tour.on('complete', () => {
    // Salva no localStorage que tour foi completado
    if (typeof window !== 'undefined') {
      localStorage.setItem('tour_operacional_completed', 'true');
      localStorage.setItem('tour_operacional_completed_at', new Date().toISOString());
    }
  });

  tour.on('cancel', () => {
    // Tour cancelado pelo usuário
  });

  return tour;
};

// Helper para verificar se tour já foi completado
export const isTourCompleted = (): boolean => {
  if (typeof window === 'undefined') return true;
  return localStorage.getItem('tour_operacional_completed') === 'true';
};

// Helper para resetar tour
export const resetTour = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('tour_operacional_completed');
  localStorage.removeItem('tour_operacional_completed_at');
};
