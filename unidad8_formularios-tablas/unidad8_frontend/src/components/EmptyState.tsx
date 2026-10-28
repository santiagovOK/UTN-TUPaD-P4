// Componente presentacional reutilizable para representar colecciones vacías con mensaje accesible y acción opcional.
export interface EmptyStateProps {
  message: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  ariaLabel?: string;
}

export function EmptyState({
  message,
  description,
  actionLabel,
  onAction,
  ariaLabel,
}: EmptyStateProps) {
  return (
    <section
      aria-label={ariaLabel}
      className="text-center py-12 px-4 bg-white rounded-xl border border-dashed border-slate-300 space-y-3"
    >
      <p role="status" aria-live="polite" className="text-slate-500 text-base">
        {message}
      </p>
      {description && <p className="text-slate-400 text-sm">{description}</p>}
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors cursor-pointer"
        >
          {actionLabel}
        </button>
      )}
    </section>
  );
}

export default EmptyState;
