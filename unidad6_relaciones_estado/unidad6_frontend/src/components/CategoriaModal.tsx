import type { Categoria } from '../types/categoria';

export interface CategoriaModalProps {
  isOpen?: boolean;
  categoriaAEditar?: Categoria | null;
  onClose?: () => void;
  onSubmit?: (e: React.FormEvent) => void;
}

export function CategoriaModal({
  isOpen = true,
  categoriaAEditar = null,
  onClose,
  onSubmit,
}: CategoriaModalProps) {
  if (!isOpen) return null;

  const isEditing = Boolean(categoriaAEditar);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-6 mb-8"
    >
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 id="modal-title" className="text-xl font-bold text-gray-900">
            {isEditing ? 'Editar Categoría' : 'Registrar Nueva Categoría'}
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Formulario de alta y edición de categorías con maquetado reciclado.
          </p>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-1.5 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
            aria-label="Cerrar modal"
          >
            ✕
          </button>
        )}
      </div>

      <form onSubmit={onSubmit ?? ((e) => e.preventDefault())}>
        <fieldset className="space-y-4">
          <legend className="sr-only">Información de la Categoría</legend>

          <div>
            <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-1">
              Nombre de la Categoría <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="nombre"
              name="nombre"
              required
              defaultValue={categoriaAEditar?.nombre ?? ''}
              placeholder="Ej: Muebles de Oficina, Electrónica..."
              className="w-full px-3.5 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm transition-colors"
            />
          </div>

          <div>
            <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              id="descripcion"
              name="descripcion"
              rows={3}
              defaultValue={categoriaAEditar?.descripcion ?? ''}
              placeholder="Descripción detallada de la categoría..."
              className="w-full px-3.5 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm resize-none transition-colors"
            />
          </div>
        </fieldset>

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-100 mt-6">
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors cursor-pointer"
            >
              Cancelar
            </button>
          )}
          <button
            type="submit"
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
          >
            {isEditing ? 'Guardar Cambios' : 'Guardar Categoría'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default CategoriaModal;
