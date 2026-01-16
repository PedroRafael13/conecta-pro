import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

export function NotFoundPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-24 h-24 bg-conecta-escuro/10 rounded-full mb-6">
          <span className="text-5xl font-bold text-conecta-escuro">404</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Pagina nao encontrada
        </h1>
        <p className="text-gray-600 mb-8 max-w-md">
          A pagina que voce esta procurando nao existe ou foi movida para outro
          endereco.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link to="/dashboard" className="btn-primary">
            <Home className="w-4 h-4 mr-2" />
            Ir para Dashboard
          </Link>
          <button
            onClick={() => window.history.back()}
            className="btn-outline"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </button>
        </div>
      </div>
    </div>
  );
}

export default NotFoundPage;
