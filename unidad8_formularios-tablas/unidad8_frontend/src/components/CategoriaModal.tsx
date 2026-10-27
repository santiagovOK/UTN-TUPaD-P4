// Base heredada del TP7; identidad y documentación adaptadas al TP8.
import type { Categoria, CategoriaFormApi } from '../types/categoria';

// [CRUD de Categorías & Tipado TypeScript]:
// Modal presentacional puro controlado por props y conectado a TanStack Form v1.
// No contiene useState ni useEffect propios; la orquestación reside en CategoriasPage.
export interface CategoriaModalProps {
  isOpen: boolean;
  isEditing: boolean;
  initialData?: Categoria | null;
  form: CategoriaFormApi;
  isSubmitting?: boolean;
  errorMessage?: string | null;
  onClose: () => void;
}

/**
 * Función pura de validación para el nombre de categoría conforme a RN-01.
 * Longitud mínima de 1 caracter tras trim y máxima de 100 caracteres.
 */
export function validateCategoriaNombre(value: string): string | undefined {
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return 'El nombre de la categoría es obligatorio.';
  }
  if (trimmed.length > 100) {
    return 'El nombre no puede superar los 100 caracteres.';
  }
  return undefined;
}

export function CategoriaModal({
  isOpen,
  isEditing,
  form,
  isSubmitting = false,
  errorMessage = null,
  onClose,
}: CategoriaModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isSubmitting) {
          onClose();
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="categoria-modal-title"
        onKeyDown={(e) => {
          if (e.key === 'Escape' && !isSubmitting) {
            e.stopPropagation();
            onClose();
          }
        }}
        className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8"
      >
        <div className="mb-5">
          <h2
            id="categoria-modal-title"
            className="text-xl font-bold text-slate-900"
          >
            {isEditing ? 'Editar Categoría' : 'Nueva Categoría'}
          </h2>
        </div>

        {errorMessage && (
          <div
            role="alert"
            className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-sm"
          >
            {errorMessage}
          </div>
        )}

        <form
          noValidate
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            void form.handleSubmit();
          }}
        >
          <fieldset className="space-y-4">
            <legend className="sr-only">Información de la Categoría</legend>

            <form.Field
              name="nombre"
              validators={{
                onBlur: ({ value }) => validateCategoriaNombre(value),
                onSubmit: ({ value }) => validateCategoriaNombre(value),
                onChange: ({ value, fieldApi }) => {
                  const err = validateCategoriaNombre(value);
                  if (!err && fieldApi.state.meta.errorMap.onBlur) {
                    fieldApi.setErrorMap({ onBlur: undefined });
                  }
                  if (
                    fieldApi.state.meta.isBlurred ||
                    form.state.submissionAttempts > 0 ||
                    value.trim().length > 100
                  ) {
                    return err;
                  }
                  return undefined;
                },
              }}
            >
              {(field) => {
                const uniqueErrors = Array.from(
                  new Set(
                    field.state.meta.errors.filter(
                      (err): err is string =>
                        typeof err === 'string' && err.length > 0
                    )
                  )
                );
                const hasError = uniqueErrors.length > 0;

                return (
                  <div>
                    <label
                      htmlFor="categoria-nombre"
                      className="block text-sm font-medium text-slate-700 mb-1.5"
                    >
                      Nombre de la categoría <span aria-hidden="true" className="text-rose-500">*</span>
                    </label>
                    <input
                      id="categoria-nombre"
                      name={field.name}
                      type="text"
                      required
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      disabled={isSubmitting}
                      placeholder="Ej: Pizzas, Empanadas, Bebidas..."
                      aria-invalid={hasError}
                      aria-describedby={
                        hasError ? 'categoria-nombre-errors' : undefined
                      }
                      className={`w-full px-3 py-2 border rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 disabled:bg-slate-100 disabled:text-slate-500 transition-colors ${
                        hasError
                          ? 'border-rose-400 focus:ring-rose-500 focus:border-rose-500'
                          : 'border-slate-300 focus:ring-blue-500 focus:border-blue-500'
                      }`}
                    />
                    {hasError && (
                      <div
                        id="categoria-nombre-errors"
                        role="alert"
                        className="mt-1.5 space-y-1"
                      >
                        {uniqueErrors.map((msg) => (
                          <p
                            key={msg}
                            className="text-xs text-rose-600 font-medium"
                          >
                            {msg}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                );
              }}
            </form.Field>

            <form.Field name="descripcion">
              {(field) => (
                <div>
                  <label
                    htmlFor="categoria-descripcion"
                    className="block text-sm font-medium text-slate-700 mb-1.5"
                  >
                    Descripción
                  </label>
                  <textarea
                    id="categoria-descripcion"
                    name={field.name}
                    rows={3}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    disabled={isSubmitting}
                    placeholder="Descripción opcional de la categoría..."
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:text-slate-500 transition-colors"
                  />
                </div>
              )}
            </form.Field>
          </fieldset>

          <form.Subscribe
            selector={(state) =>
              [state.canSubmit, state.isSubmitting] as const
            }
          >
            {([canSubmit, formIsSubmitting]) => {
              const busy = Boolean(isSubmitting || formIsSubmitting);

              return (
                <div className="flex justify-end gap-3 pt-6">
                  <button
                    type="button"
                    onClick={onClose}
                    disabled={busy}
                    className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors cursor-pointer"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={!canSubmit || busy}
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white font-medium text-sm rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer"
                  >
                    {busy
                      ? 'Guardando...'
                      : isEditing
                        ? 'Guardar cambios'
                        : 'Guardar'}
                  </button>
                </div>
              );
            }}
          </form.Subscribe>
        </form>
      </div>
    </div>
  );
}

export default CategoriaModal;
