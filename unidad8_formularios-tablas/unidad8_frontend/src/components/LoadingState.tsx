// Componente presentacional reutilizable de estado de carga inicial con Skeleton accesible.
export interface LoadingStateProps {
  message?: string;
  rows?: number;
}

export function LoadingState({
  message = 'Cargando datos...',
  rows = 5,
}: LoadingStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 animate-pulse motion-reduce:animate-none"
    >
      <div aria-hidden="true" className="space-y-4">
        <div className="flex justify-between items-center pb-4 border-b border-slate-100">
          <div className="h-4 bg-slate-200 rounded w-1/4" />
          <div className="h-4 bg-slate-200 rounded w-1/6" />
        </div>
        <div className="space-y-3">
          {Array.from({ length: rows }, (_, i) => i + 1).map((id) => (
            <div key={id} className="h-8 bg-slate-100 rounded" />
          ))}
        </div>
      </div>
      <span className="sr-only">{message}</span>
    </div>
  );
}

export default LoadingState;
