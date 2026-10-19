import { useState, useEffect } from 'react';
import type { Categoria } from '../types/categoria';
import type { Producto, ProductoCreate } from '../types/producto';

// [Consigna TP7 - Modal Controlado y Server State (HU-06, RN-06, RN-07, RN-19)]:
//   - Formulario de alta y edición de producto dentro de un Modal controlado con estado booleano.
//   - Validación de campos requeridos: nombre no vacío (RN-06), precio base >= 0 (RN-07), y al menos una categoría asociada (RN-19).
// [Diagrama UML - Entidad PRODUCTO y relación N:N con CATEGORIA (docs/UML_FOOD_STORE.svg)]:
//   - Permite vincular múltiples categorías mediante checkboxes accesibles.
export interface ProductoModalProps {
  isOpen?: boolean;
  initialData?: Producto | null;
  productoAEditar?: Producto | null;
  categoriasDisponibles: Categoria[];
  isLoadingCategorias?: boolean;
  isSubmitting?: boolean;
  errorMessage?: string | null;
  onClose?: () => void;
  onSubmit?: (values: ProductoCreate) => void;
}

export function ProductoModal({
  isOpen = true,
  initialData = null,
  productoAEditar = null,
  categoriasDisponibles = [],
  isLoadingCategorias = false,
  isSubmitting = false,
  errorMessage = null,
  onClose,
  onSubmit,
}: ProductoModalProps) {
  const activeProducto = initialData ?? productoAEditar ?? null;
  const [nombre, setNombre] = useState(activeProducto?.nombre ?? '');
  const [descripcion, setDescripcion] = useState(activeProducto?.descripcion ?? '');
  const [precioBase, setPrecioBase] = useState(
    activeProducto ? String(activeProducto.precio_base) : ''
  );
  const [disponible, setDisponible] = useState(activeProducto?.disponible ?? true);
  const [selectedCategoriaIds, setSelectedCategoriaIds] = useState<number[]>(
    activeProducto?.categorias?.map((c) => c.id) ?? []
  );
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (activeProducto) {
      setNombre(activeProducto.nombre);
      setDescripcion(activeProducto.descripcion ?? '');
      setPrecioBase(String(activeProducto.precio_base));
      setDisponible(activeProducto.disponible);
      setSelectedCategoriaIds(activeProducto.categorias?.map((c) => c.id) ?? []);
    } else {
      setNombre('');
      setDescripcion('');
      setPrecioBase('');
      setDisponible(true);
      setSelectedCategoriaIds([]);
    }
    setValidationError(null);
  }, [initialData, productoAEditar, isOpen]);

  if (!isOpen) return null;

  const isEditing = Boolean(activeProducto);

  const handleToggleCategoria = (catId: number) => {
    setValidationError(null);
    setSelectedCategoriaIds((prev) =>
      prev.includes(catId) ? prev.filter((id) => id !== catId) : [...prev, catId]
    );
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmedNombre = nombre.trim();
    const trimmedDescripcion = descripcion.trim();

    if (trimmedNombre === '') {
      setValidationError('El nombre del producto es obligatorio.');
      return;
    }

    const parsedPrecio = Number(precioBase);
    if (precioBase.trim() === '' || Number.isNaN(parsedPrecio) || parsedPrecio < 0) {
      setValidationError('El precio base debe ser un número mayor o igual a 0.');
      return;
    }

    if (selectedCategoriaIds.length === 0) {
      setValidationError('Debe seleccionar al menos una categoría para el producto (RN-19).');
      return;
    }

    setValidationError(null);
    onSubmit?.({
      nombre: trimmedNombre,
      descripcion: trimmedDescripcion || null,
      precio_base: parsedPrecio,
      disponible,
      categoria_ids: selectedCategoriaIds,
    });
  };

  const activeError = validationError || errorMessage;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="producto-modal-title"
        className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 sm:p-8 max-h-[90vh] overflow-y-auto"
      >
        <div className="mb-5">
          <h2 id="producto-modal-title" className="text-xl font-bold text-slate-900">
            {isEditing ? 'Editar Producto' : 'Nuevo Producto'}
          </h2>
        </div>

        {activeError && (
          <div
            role="alert"
            aria-live="polite"
            className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-sm"
          >
            {activeError}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <fieldset className="space-y-4">
            <legend className="sr-only">Información del Producto</legend>

            <div>
              <label
                htmlFor="prod-nombre"
                className="block text-sm font-medium text-slate-700 mb-1.5"
              >
                Nombre del producto
              </label>
              <input
                type="text"
                id="prod-nombre"
                name="nombre"
                required
                value={nombre}
                onChange={(e) => {
                  setNombre(e.target.value);
                  if (validationError) setValidationError(null);
                }}
                disabled={isSubmitting}
                placeholder="Ej: Pizza Napolitana, Hamburguesa Clásica..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:text-slate-500 transition-colors"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="prod-precio"
                  className="block text-sm font-medium text-slate-700 mb-1.5"
                >
                  Precio base ($)
                </label>
                <input
                  type="number"
                  id="prod-precio"
                  name="precio_base"
                  required
                  min="0"
                  step="0.01"
                  value={precioBase}
                  onChange={(e) => {
                    setPrecioBase(e.target.value);
                    if (validationError) setValidationError(null);
                  }}
                  disabled={isSubmitting}
                  placeholder="0.00"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:text-slate-500 transition-colors"
                />
              </div>

              <div className="flex items-center sm:pt-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    id="prod-disponible"
                    name="disponible"
                    checked={disponible}
                    onChange={(e) => setDisponible(e.target.checked)}
                    disabled={isSubmitting}
                    className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500 cursor-pointer"
                  />
                  <span className="text-sm font-medium text-slate-700 select-none">
                    Disponible para venta
                  </span>
                </label>
              </div>
            </div>

            <div>
              <label
                htmlFor="prod-descripcion"
                className="block text-sm font-medium text-slate-700 mb-1.5"
              >
                Descripción (opcional)
              </label>
              <textarea
                id="prod-descripcion"
                name="descripcion"
                rows={3}
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                disabled={isSubmitting}
                placeholder="Descripción detallada del producto..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:text-slate-500 transition-colors"
              />
            </div>

            <div>
              <span className="block text-sm font-medium text-slate-700 mb-1.5">
                Categorías asociadas (mínimo 1)
              </span>
              <div className="border border-slate-200 rounded-lg p-3 max-h-44 overflow-y-auto space-y-2 bg-slate-50">
                {isLoadingCategorias ? (
                  <p className="text-xs text-slate-500 italic py-2">
                    Cargando categorías disponibles...
                  </p>
                ) : categoriasDisponibles.length === 0 ? (
                  <p className="text-xs text-amber-600 font-medium py-2">
                    No hay categorías disponibles. Debe crear al menos una categoría en la sección Categorías antes de guardar productos.
                  </p>
                ) : (
                  categoriasDisponibles.map((cat) => (
                    <label
                      key={cat.id}
                      className="flex items-center gap-2.5 p-1.5 rounded hover:bg-white transition-colors cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedCategoriaIds.includes(cat.id)}
                        onChange={() => handleToggleCategoria(cat.id)}
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
            </div>
          </fieldset>

          <div className="flex justify-end gap-3 pt-6 border-t border-slate-100 mt-6">
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
            <button
              type="submit"
              disabled={isSubmitting || categoriasDisponibles.length === 0}
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

export default ProductoModal;
