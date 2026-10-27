// Base heredada del TP7; identidad y documentación adaptadas al TP8.
import type { Categoria } from '../types/categoria';
import type { Producto, ProductoFormApi } from '../types/producto';

// [Modal Controlado & TanStack Form v1]:
//   - Componente presentacional puro controlado por props y conectado a ProductoFormApi.
//   - Sin useState ni useEffect internos; la orquestación reside en ProductsPage.

export interface ProductoModalProps {
  isOpen: boolean;
  isEditing: boolean;
  initialData?: Producto | null;
  form: ProductoFormApi;
  categoriasDisponibles: Categoria[];
  isLoadingCategorias?: boolean;
  isSubmitting?: boolean;
  errorMessage?: string | null;
  onClose: () => void;
}

/**
 * Función pura de validación para el nombre del producto conforme a RN-06.
 * Longitud mínima de 1 caracter tras trim y máxima de 150 caracteres.
 */
export function validateProductoNombre(value: string): string | undefined {
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return 'El nombre del producto es obligatorio.';
  }
  if (trimmed.length > 150) {
    return 'El nombre no puede superar los 150 caracteres.';
  }
  return undefined;
}

/**
 * Función pura de validación para el precio base conforme a RN-07.
 * Requiere valor numérico finito mayor o igual a 0 (admite 0 para ítems promocionales/gratuitos).
 */
export function validateProductoPrecioBase(value: string): string | undefined {
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return 'El precio base es obligatorio.';
  }
  const parsed = Number(trimmed);
  if (!Number.isFinite(parsed) || parsed < 0) {
    return 'El precio base debe ser un número mayor o igual a 0.';
  }
  return undefined;
}

/**
 * Función pura de validación para las categorías asociadas conforme a RN-08 (RN-11).
 * Exige seleccionar al menos una categoría válida.
 */
export function validateProductoCategorias(value: number[]): string | undefined {
  if (!Array.isArray(value) || value.length === 0) {
    return 'Debe seleccionar al menos una categoría para el producto.';
  }
  return undefined;
}

export function ProductoModal({
  isOpen,
  isEditing,
  form,
  categoriasDisponibles,
  isLoadingCategorias = false,
  isSubmitting = false,
  errorMessage = null,
  onClose,
}: ProductoModalProps) {
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
        aria-labelledby="producto-modal-title"
        onKeyDown={(e) => {
          if (e.key === 'Escape' && !isSubmitting) {
            e.stopPropagation();
            onClose();
          }
        }}
        className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 sm:p-8 max-h-[90vh] overflow-y-auto"
      >
        <div className="mb-5">
          <h2
            id="producto-modal-title"
            className="text-xl font-bold text-slate-900"
          >
            {isEditing ? 'Editar Producto' : 'Nuevo Producto'}
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
            <legend className="sr-only">Información del Producto</legend>

            <form.Field
              name="nombre"
              validators={{
                onBlur: ({ value }) => validateProductoNombre(value),
                onSubmit: ({ value }) => validateProductoNombre(value),
                onChange: ({ value, fieldApi }) => {
                  const err = validateProductoNombre(value);
                  if (!err && fieldApi.state.meta.errorMap.onBlur) {
                    fieldApi.setErrorMap({ onBlur: undefined });
                  }
                  if (
                    fieldApi.state.meta.isBlurred ||
                    form.state.submissionAttempts > 0 ||
                    value.trim().length > 150
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
                      htmlFor="prod-nombre"
                      className="block text-sm font-medium text-slate-700 mb-1.5"
                    >
                      Nombre del producto{' '}
                      <span aria-hidden="true" className="text-rose-500">
                        *
                      </span>
                    </label>
                    <input
                      id="prod-nombre"
                      name={field.name}
                      type="text"
                      required
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      disabled={isSubmitting}
                      placeholder="Ej: Pizza Napolitana, Hamburguesa Clásica..."
                      aria-invalid={hasError}
                      aria-describedby={
                        hasError ? 'prod-nombre-errors' : undefined
                      }
                      className={`w-full px-3 py-2 border rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 disabled:bg-slate-100 disabled:text-slate-500 transition-colors ${
                        hasError
                          ? 'border-rose-400 focus:ring-rose-500 focus:border-rose-500'
                          : 'border-slate-300 focus:ring-blue-500 focus:border-blue-500'
                      }`}
                    />
                    {hasError && (
                      <div
                        id="prod-nombre-errors"
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

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <form.Field
                name="precio_base"
                validators={{
                  onBlur: ({ value }) => validateProductoPrecioBase(value),
                  onSubmit: ({ value }) => validateProductoPrecioBase(value),
                  onChange: ({ value, fieldApi }) => {
                    const err = validateProductoPrecioBase(value);
                    if (!err && fieldApi.state.meta.errorMap.onBlur) {
                      fieldApi.setErrorMap({ onBlur: undefined });
                    }
                    const parsed = Number(value.trim());
                    if (
                      (value.trim() !== '' &&
                        (!Number.isFinite(parsed) || parsed < 0)) ||
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
                        htmlFor="prod-precio"
                        className="block text-sm font-medium text-slate-700 mb-1.5"
                      >
                        Precio base ($){' '}
                        <span aria-hidden="true" className="text-rose-500">
                          *
                        </span>
                      </label>
                      <input
                        id="prod-precio"
                        name={field.name}
                        type="number"
                        min="0"
                        step="0.01"
                        required
                        value={field.state.value}
                        onBlur={field.handleBlur}
                        onChange={(e) => field.handleChange(e.target.value)}
                        disabled={isSubmitting}
                        placeholder="0.00"
                        aria-invalid={hasError}
                        aria-describedby={
                          hasError ? 'prod-precio-errors' : undefined
                        }
                        className={`w-full px-3 py-2 border rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 disabled:bg-slate-100 disabled:text-slate-500 transition-colors ${
                          hasError
                            ? 'border-rose-400 focus:ring-rose-500 focus:border-rose-500'
                            : 'border-slate-300 focus:ring-blue-500 focus:border-blue-500'
                        }`}
                      />
                      {hasError && (
                        <div
                          id="prod-precio-errors"
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

              <form.Field name="disponible">
                {(field) => (
                  <div className="flex items-center sm:pt-6">
                    <label
                      htmlFor="prod-disponible"
                      className="flex items-center gap-2 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        id="prod-disponible"
                        name={field.name}
                        checked={field.state.value}
                        onBlur={field.handleBlur}
                        onChange={(e) => field.handleChange(e.target.checked)}
                        disabled={isSubmitting}
                        className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500 cursor-pointer"
                      />
                      <span className="text-sm font-medium text-slate-700 select-none">
                        Disponible para venta
                      </span>
                    </label>
                  </div>
                )}
              </form.Field>
            </div>

            <form.Field name="descripcion">
              {(field) => (
                <div>
                  <label
                    htmlFor="prod-descripcion"
                    className="block text-sm font-medium text-slate-700 mb-1.5"
                  >
                    Descripción (opcional)
                  </label>
                  <textarea
                    id="prod-descripcion"
                    name={field.name}
                    rows={3}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    disabled={isSubmitting}
                    placeholder="Descripción detallada del producto..."
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:text-slate-500 transition-colors"
                  />
                </div>
              )}
            </form.Field>

            <form.Field
              name="categoria_ids"
              validators={{
                onBlur: ({ value }) => validateProductoCategorias(value),
                onSubmit: ({ value }) => validateProductoCategorias(value),
                onChange: ({ value, fieldApi }) => {
                  const err = validateProductoCategorias(value);
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
                    <span
                      id="prod-categorias-label"
                      className="block text-sm font-medium text-slate-700 mb-1.5"
                    >
                      Categorías asociadas (mínimo 1){' '}
                      <span aria-hidden="true" className="text-rose-500">
                        *
                      </span>
                    </span>
                    <div
                      role="group"
                      aria-labelledby="prod-categorias-label"
                      aria-invalid={hasError}
                      aria-describedby={
                        hasError ? 'prod-categorias-errors' : undefined
                      }
                      className={`border rounded-lg p-3 max-h-44 overflow-y-auto space-y-2 bg-slate-50 ${
                        hasError ? 'border-rose-400' : 'border-slate-200'
                      }`}
                    >
                      {isLoadingCategorias ? (
                        <div
                          role="status"
                          aria-live="polite"
                          className="text-xs text-slate-500 italic py-2"
                        >
                          Cargando categorías disponibles...
                        </div>
                      ) : categoriasDisponibles.length === 0 ? (
                        <div
                          role="status"
                          className="text-xs text-amber-600 font-medium py-2"
                        >
                          No hay categorías disponibles. Debe crear al menos una
                          categoría en la sección Categorías antes de guardar
                          productos.
                        </div>
                      ) : (
                        categoriasDisponibles.map((cat) => (
                          <label
                            key={cat.id}
                            htmlFor={`prod-cat-${cat.id}`}
                            className="flex items-center gap-2.5 p-1.5 rounded hover:bg-white transition-colors cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              id={`prod-cat-${cat.id}`}
                              checked={field.state.value.includes(cat.id)}
                              onChange={() => {
                                const current = field.state.value;
                                const next = current.includes(cat.id)
                                  ? current.filter((id) => id !== cat.id)
                                  : [...current, cat.id];
                                field.handleChange(next);
                                field.handleBlur();
                              }}
                              disabled={isSubmitting}
                              className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500 cursor-pointer"
                            />
                            <span className="text-sm text-slate-800 font-medium">
                              {cat.nombre}
                            </span>
                            {cat.descripcion && (
                              <span className="text-xs text-slate-400 truncate max-w-xs">
                                — {cat.descripcion}
                              </span>
                            )}
                          </label>
                        ))
                      )}
                    </div>
                    {hasError && (
                      <div
                        id="prod-categorias-errors"
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
          </fieldset>

          <form.Subscribe
            selector={(state) =>
              [state.canSubmit, state.isSubmitting] as const
            }
          >
            {([canSubmit, formIsSubmitting]) => {
              const busy = Boolean(isSubmitting || formIsSubmitting);

              return (
                <div className="flex justify-end gap-3 pt-6 border-t border-slate-100 mt-6">
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
                    disabled={
                      !canSubmit || busy || categoriasDisponibles.length === 0
                    }
                    aria-busy={busy}
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

export default ProductoModal;
