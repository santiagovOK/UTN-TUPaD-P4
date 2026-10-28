// Componente presentacional reutilizable para errores de consulta (bloqueante inicial o aviso en segundo plano).
export interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
  isRetrying?: boolean;
  variant?: 'blocking' | 'background';
}

export function ErrorState({
  title = 'Error al cargar los datos',
  message,
  onRetry,
  retryLabel = 'Reintentar',
  isRetrying = false,
  variant = 'blocking',
}: ErrorStateProps) {
  if (variant === 'background') {
    return (
      <div
        role="status"
        aria-live="polite"
        className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm flex items-center justify-between"
      >
        <span>
          {title ? `${title}: ` : ''}
          {message}
        </span>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            disabled={isRetrying}
            className="text-amber-900 font-medium underline text-xs ml-4 cursor-pointer hover:text-amber-950 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 rounded"
          >
            {isRetrying ? 'Reintentando...' : retryLabel}
          </button>
        )}
      </div>
    );
  }

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="p-8 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-center space-y-4"
    >
      <div>
        {title && <p className="font-semibold text-base">{title}</p>}
        <p className="text-sm text-rose-600 mt-1">{message}</p>
      </div>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          disabled={isRetrying}
          className="inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500 transition-colors cursor-pointer"
        >
          {isRetrying ? 'Reintentando...' : retryLabel}
        </button>
      )}
    </div>
  );
}

export default ErrorState;
