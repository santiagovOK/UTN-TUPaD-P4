import type { Categoria } from '../types/categoria';

// [Consigna TP6 - Parte B, inciso d]: CategoriaModal.tsx — formulario de alta/edición dentro de un modal accesible.
export interface CategoriaModalProps {
  isOpen?: boolean;
  categoriaAEditar?: Categoria | null;
  onClose?: () => void;
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void;
  isSubmitting?: boolean;
}

export function CategoriaModal({
  isOpen = true,
  categoriaAEditar = null,
  onClose,
  onSubmit,
  isSubmitting = false,
}: CategoriaModalProps) {
  if (!isOpen) return null;

  const isEditing = Boolean(categoriaAEditar);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8"
      >
        <div className="mb-5">
          <h2 id="modal-title" className="text-xl font-bold text-slate-900">
            {isEditing ? 'Editar Categoría' : 'Nueva Categoría'}
          </h2>
        </div>

        <form onSubmit={onSubmit ?? ((e) => e.preventDefault())}>
          <fieldset className="space-y-4">
            <legend className="sr-only">Información de la Categoría</legend>

            <div>
              <label
                htmlFor="nombre"
                className="block text-sm font-medium text-slate-700 mb-1.5"
              >
                Nombre de la categoría
              </label>
              <input
                type="text"
                id="nombre"
                name="nombre"
                required
                defaultValue={categoriaAEditar?.nombre ?? ''}
                placeholder="Ej: Pizzas, Hamburguesas..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>

            <div>
              <label
                htmlFor="descripcion"
                className="block text-sm font-medium text-slate-700 mb-1.5"
              >
                Descripción
              </label>
              <input
                type="text"
                id="descripcion"
                name="descripcion"
                defaultValue={categoriaAEditar?.descripcion ?? ''}
                placeholder="Descripción de la categoría..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
          </fieldset>

          <div className="flex justify-end gap-3 pt-6">
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
              >
                Cancelar
              </button>
            )}
            {/* [Consigna TP6 - Parte B, inciso e]: Prevención de doble envío mediante isSubmitting y estado disabled. */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white font-medium text-sm rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer"
            >
              {isSubmitting ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CategoriaModal;
