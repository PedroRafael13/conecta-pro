import { AlertCircle, RefreshCw } from 'lucide-react';
import { clsx } from 'clsx';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({
  title = 'Erro',
  message,
  onRetry,
  className,
}: ErrorMessageProps) {
  return (
    <div
      className={clsx(
        'flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg',
        className
      )}
    >
      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="font-medium text-red-800">{title}</p>
        <p className="text-sm text-red-700 mt-1">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 mt-3 text-sm font-medium text-red-700 hover:text-red-800"
          >
            <RefreshCw className="w-4 h-4" />
            Tentar novamente
          </button>
        )}
      </div>
    </div>
  );
}

export default ErrorMessage;
