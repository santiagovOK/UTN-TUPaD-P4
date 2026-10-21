// Base heredada del TP7; identidad y documentación adaptadas al TP8.
import { useState, useEffect } from 'react';
import type { Categoria, CategoriaCreate } from '../types/categoria';

// [Modal Controlado y Server State]: Formulario de alta y edición dentro de un Modal controlado con estado booleano mediante useState.
// [Diagrama UML - Entidad CATEGORIA]: Captura los campos de negocio nombre (VARCHAR(100) NN UNIQUE) y descripcion (TEXT) para creación (POST) y actualización (PATCH/PUT).
export interface CategoriaModalProps {
  isOpen?: boolean;
  initialData?: Categoria | null;
  categoriaAEditar?: Categoria | null; // Retrocompatibilidad de prop
  isSubmitting?: boolean;
  errorMessage?: string | null;
  onClose?: () => void;
  onSubmit?: (values: CategoriaCreate) => void;
}

export function CategoriaModal({
  isOpen = true,
  initialData = null,
  categoriaAEditar = null,
  isSubmitting = false,
  errorMessage = null,
  onClose,
  onSubmit,
}: CategoriaModalProps) {
  const activeCategoria = initialData ?? categoriaAEditar ?? null;
  const [nombre, setNombre] = useState(activeCategoria?.nombre ?? '');
  const [descripcion, setDescripcion] = useState(activeCategoria?.descripcion ?? '');

  useEffect(() => {
    if (activeCategoria) {
      setNombre(activeCategoria.nombre);
      setDescripcion(activeCategoria.descripcion ?? '');
    } else {
      setNombre('');
      setDescripcion('');
    }
  }, [initialData, categoriaAEditar, isOpen]);

  if (!isOpen) return null;

  const isEditing = Boolean(activeCategoria);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmedNombre = nombre.trim();
    const trimmedDescripcion = descripcion.trim();
    if (trimmedNombre === '') return;

    onSubmit?.({
      nombre: trimmedNombre,
      descripcion: trimmedDescripcion || undefined,
    });
  };

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

        {errorMessage && (
          <div
            role="alert"
            aria-live="polite"
            className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-sm"
          >
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit}>
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
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                disabled={isSubmitting}
                placeholder="Ej: Pizzas, Hamburguesas..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:text-slate-500 transition-colors"
              />
            </div>

            <div>
              <label
                htmlFor="descripcion"
                className="block text-sm font-medium text-slate-700 mb-1.5"
              >
                Descripción
              </label>
              <textarea
                id="descripcion"
                name="descripcion"
                rows={3}
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                disabled={isSubmitting}
                placeholder="Descripción de la categoría..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:text-slate-500 transition-colors"
              />
            </div>
          </fieldset>

          <div className="flex justify-end gap-3 pt-6">
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors cursor-pointer"
              >
                Cancelar
              </button>
            )}
            {/* Prevención de doble envío mediante isSubmitting y estado disabled */}
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
