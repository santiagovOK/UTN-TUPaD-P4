import type { Ingrediente, IngredienteFormApi, UnidadMedida } from '../types/ingrediente';

// [CRUD de Ingredientes & Tipado TypeScript]:
// Modal presentacional puro controlado por props y conectado a TanStack Form v1.
// No contiene useState ni useEffect propios; la orquestación reside en IngredientesPage.
export interface IngredienteModalProps {
  isOpen: boolean;
  isEditing: boolean;
  initialData?: Ingrediente | null;
  form: IngredienteFormApi;
  unidadesMedida: UnidadMedida[];
  isLoadingUnidades?: boolean;
  isSubmitting?: boolean;
  errorMessage?: string | null;
  onClose: () => void;
}

/**
 * Función pura de validación para el nombre de ingrediente conforme a RN-10.
 * Longitud mínima de 1 carácter tras trim y máxima de 100 caracteres.
 */
export function validateIngredienteNombre(value: string): string | undefined {
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return 'El nombre del ingrediente es obligatorio.';
  }
  if (trimmed.length > 100) {
    return 'El nombre no puede superar los 100 caracteres.';
  }
  return undefined;
}

/**
 * Función pura de validación para la unidad de medida de ingrediente conforme a RN-11.
 * Exige la selección de una unidad válida con identificador numérico entero positivo.
 */
export function validateIngredienteUnidad(value: string): string | undefined {
  const parsed = Number(value.trim());
  if (!value || !Number.isInteger(parsed) || parsed <= 0) {
    return 'Debe seleccionar una unidad de medida válida.';
  }
  return undefined;
}

export function IngredienteModal({
  isOpen,
  isEditing,
  form,
  unidadesMedida,
  isLoadingUnidades = false,
  isSubmitting = false,
  errorMessage = null,
  onClose,
}: IngredienteModalProps) {
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
        aria-labelledby="ingrediente-modal-title"
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
            id="ingrediente-modal-title"
            className="text-xl font-bold text-slate-900"
          >
            {isEditing ? 'Editar Ingrediente' : 'Nuevo Ingrediente'}
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
            <legend className="sr-only">Información del Ingrediente</legend>

            <form.Field
              name="nombre"
              validators={{
                onBlur: ({ value }) => validateIngredienteNombre(value),
                onSubmit: ({ value }) => validateIngredienteNombre(value),
                onChange: ({ value, fieldApi }) => {
                  const err = validateIngredienteNombre(value);
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
                      htmlFor="ingrediente-nombre"
                      className="block text-sm font-medium text-slate-700 mb-1.5"
                    >
                      Nombre del ingrediente{' '}
                      <span aria-hidden="true" className="text-rose-500">
                        *
                      </span>
                    </label>
                    <input
                      id="ingrediente-nombre"
                      name={field.name}
                      type="text"
                      required
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      disabled={isSubmitting}
                      placeholder="Ej: Queso Mozzarella, Harina de Trigo, Salsa de Tomate..."
                      aria-invalid={hasError}
                      aria-describedby={
                        hasError ? 'ingrediente-nombre-errors' : undefined
                      }
                      className={`w-full px-3 py-2 border rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 disabled:bg-slate-100 disabled:text-slate-500 transition-colors ${
                        hasError
                          ? 'border-rose-400 focus:ring-rose-500 focus:border-rose-500'
                          : 'border-slate-300 focus:ring-blue-500 focus:border-blue-500'
                      }`}
                    />
                    {hasError && (
                      <div
                        id="ingrediente-nombre-errors"
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

            <form.Field
              name="unidad_medida_id"
              validators={{
                onBlur: ({ value }) => validateIngredienteUnidad(value),
                onSubmit: ({ value }) => validateIngredienteUnidad(value),
                onChange: ({ value, fieldApi }) => {
                  const err = validateIngredienteUnidad(value);
                  if (!err && fieldApi.state.meta.errorMap.onBlur) {
                    fieldApi.setErrorMap({ onBlur: undefined });
                  }
                  if (
                    fieldApi.state.meta.isBlurred ||
                    form.state.submissionAttempts > 0
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
                      htmlFor="ingrediente-unidad"
                      className="block text-sm font-medium text-slate-700 mb-1.5"
                    >
                      Unidad de medida{' '}
                      <span aria-hidden="true" className="text-rose-500">
                        *
                      </span>
                    </label>
                    <select
                      id="ingrediente-unidad"
                      name={field.name}
                      required
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      disabled={isSubmitting || isLoadingUnidades}
                      aria-invalid={hasError}
                      aria-describedby={
                        hasError ? 'ingrediente-unidad-errors' : undefined
                      }
                      className={`w-full px-3 py-2 border rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 disabled:bg-slate-100 disabled:text-slate-500 transition-colors ${
                        hasError
                          ? 'border-rose-400 focus:ring-rose-500 focus:border-rose-500'
                          : 'border-slate-300 focus:ring-blue-500 focus:border-blue-500'
                      }`}
                    >
                      <option value="">Seleccione una unidad de medida...</option>
                      {unidadesMedida.map((u) => (
                        <option key={u.id} value={String(u.id)}>
                          {u.nombre} ({u.simbolo}) — {u.tipo}
                        </option>
                      ))}
                    </select>
                    {hasError && (
                      <div
                        id="ingrediente-unidad-errors"
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

            <form.Field name="activo">
              {(field) => (
                <div className="flex items-center pt-1">
                  <label
                    htmlFor="ingrediente-activo"
                    className="flex items-center gap-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      id="ingrediente-activo"
                      name={field.name}
                      checked={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.checked)}
                      disabled={isSubmitting}
                      className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500 cursor-pointer"
                    />
                    <span className="text-sm font-medium text-slate-700 select-none">
                      Ingrediente activo en catálogo
                    </span>
                  </label>
                </div>
              )}
            </form.Field>

            <form.Field name="descripcion">
              {(field) => (
                <div>
                  <label
                    htmlFor="ingrediente-descripcion"
                    className="block text-sm font-medium text-slate-700 mb-1.5"
                  >
                    Descripción{' '}
                    <span className="text-xs text-slate-400 font-normal">
                      (opcional)
                    </span>
                  </label>
                  <textarea
                    id="ingrediente-descripcion"
                    name={field.name}
                    rows={3}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    disabled={isSubmitting}
                    placeholder="Descripción o notas del ingrediente..."
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
                    disabled={!canSubmit || busy || unidadesMedida.length === 0}
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

export default IngredienteModal;
