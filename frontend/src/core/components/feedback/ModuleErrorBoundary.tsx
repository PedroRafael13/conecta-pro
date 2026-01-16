import { Component, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';

interface ModuleErrorBoundaryProps {
  /** Nome do modulo para exibicao e logging */
  moduleName: string;
  /** Conteudo do modulo */
  children: ReactNode;
  /** Componente customizado de fallback */
  fallback?: ReactNode;
  /** Callback quando erro ocorre */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  /** Se deve mostrar detalhes tecnicos do erro (default: false em producao) */
  showErrorDetails?: boolean;
}

interface ModuleErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * Error Boundary especializado para modulos.
 * Captura erros em modulos especificos sem derrubar toda a aplicacao.
 *
 * @example
 * <ModuleErrorBoundary moduleName="Dashboard">
 *   <DashboardModule />
 * </ModuleErrorBoundary>
 */
export class ModuleErrorBoundary extends Component<
  ModuleErrorBoundaryProps,
  ModuleErrorBoundaryState
> {
  constructor(props: ModuleErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ModuleErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Armazena info do erro para exibicao
    this.setState({ errorInfo });

    // Log estruturado do erro
    console.error(`[ModuleError] ${this.props.moduleName}:`, {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
    });

    // Callback customizado se fornecido
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Aqui poderia enviar para servico de monitoramento (Sentry, LogRocket, etc)
    // reportErrorToService(error, { module: this.props.moduleName, errorInfo });
  }

  handleReload = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback, moduleName, showErrorDetails } = this.props;

    if (!hasError) {
      return children;
    }

    // Fallback customizado
    if (fallback) {
      return fallback;
    }

    // Determina se deve mostrar detalhes (em desenvolvimento)
    const isDev = import.meta.env.DEV;
    const showDetails = showErrorDetails ?? isDev;

    return (
      <div
        className="min-h-[400px] flex items-center justify-center p-8"
        role="alert"
        aria-live="assertive"
      >
        <div className="text-center max-w-lg w-full">
          {/* Icone de erro */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" aria-hidden="true" />
          </div>

          {/* Titulo */}
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Erro no modulo {moduleName}
          </h2>

          {/* Descricao */}
          <p className="text-gray-600 mb-6">
            Ocorreu um problema ao carregar este modulo.
            Voce pode tentar recarregar ou voltar para a pagina inicial.
          </p>

          {/* Detalhes do erro (apenas em dev ou se habilitado) */}
          {showDetails && error && (
            <details className="text-left mb-6">
              <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 flex items-center gap-2">
                <Bug className="w-4 h-4" aria-hidden="true" />
                Detalhes tecnicos
              </summary>
              <div className="mt-2 space-y-2">
                <pre className="text-xs bg-gray-100 p-4 rounded-lg overflow-auto max-h-32">
                  <strong>Erro:</strong> {error.message}
                </pre>
                {errorInfo?.componentStack && (
                  <pre className="text-xs bg-gray-100 p-4 rounded-lg overflow-auto max-h-48">
                    <strong>Component Stack:</strong>
                    {errorInfo.componentStack}
                  </pre>
                )}
              </div>
            </details>
          )}

          {/* Botoes de acao */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={this.handleReload}
              className="inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              <RefreshCw className="w-4 h-4 mr-2" aria-hidden="true" />
              Recarregar modulo
            </button>

            <button
              onClick={this.handleGoHome}
              className="inline-flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              <Home className="w-4 h-4 mr-2" aria-hidden="true" />
              Ir para inicio
            </button>
          </div>
        </div>
      </div>
    );
  }
}

export default ModuleErrorBoundary;
