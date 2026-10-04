import type { Categoria } from '../types/categoria';

// [Consigna TP6 - Parte B, inciso d]: CategoriaCard.tsx — tarjeta que muestra una categoría (nombre + descripción). Recibe props tipados con Categoria e incluye botones Editar y Eliminar.
export interface CategoriaCardProps {
  categoria: Categoria;
  onEdit?: (categoria: Categoria) => void;
  onDelete?: (id: number) => void;
}

export function CategoriaCard({ categoria, onEdit, onDelete }: CategoriaCardProps) {
  const { id, nombre, descripcion, activo } = categoria;

  return (
    <article className="w-full bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-5 hover:shadow-md transition-shadow flex flex-col justify-between">
      <div>
        <header className="flex justify-between items-start mb-2">
          <span className="inline-block bg-indigo-50 text-indigo-700 text-xs px-2.5 py-1 rounded-full font-semibold uppercase tracking-wide">
            ID: #{id}
          </span>
          {activo !== undefined && (
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                activo ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
              }`}
            >
              {activo ? 'Activo' : 'Inactivo'}
            </span>
          )}
        </header>

        <h3 className="text-lg font-bold text-gray-900 mb-1 leading-snug">{nombre}</h3>

        {descripcion ? (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">{descripcion}</p>
        ) : (
          <p className="text-sm text-gray-400 italic mb-4">Sin descripción</p>
        )}
      </div>

      <footer className="pt-4 border-t border-gray-100 flex items-center justify-end gap-2 mt-auto">
        <button
          type="button"
          onClick={() => onEdit?.(categoria)}
          className="px-3 py-1.5 text-xs font-medium text-amber-700 bg-amber-50 hover:bg-amber-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500 cursor-pointer"
        >
          Editar
        </button>
        <button
          type="button"
          onClick={() => onDelete?.(id)}
          className="px-3 py-1.5 text-xs font-medium text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-rose-500 cursor-pointer"
        >
          Eliminar
        </button>
      </footer>
    </article>
  );
}

export default CategoriaCard;
