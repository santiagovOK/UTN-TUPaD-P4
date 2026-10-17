import type { Categoria } from '../types/categoria';

// [Consigna TP7 - CRUD de Categorías & Tipado TypeScript]: Componente presentacional de fila con props tipados (Categoria) y acciones de edición/eliminación.
// [Diagrama UML - Entidad CATEGORIA]: Visualiza los atributos id (INTEGER PK), nombre (VARCHAR(100) UNIQUE NN) y descripcion (TEXT).
export interface CategoriaCardProps {
  categoria: Categoria;
  onEdit?: (categoria: Categoria) => void;
  onDelete?: (id: number) => void;
}

export function CategoriaCard({ categoria, onEdit, onDelete }: CategoriaCardProps) {
  const { id, nombre, descripcion } = categoria;

  return (
    <tr className="border-t border-slate-100 hover:bg-slate-50 transition-colors">
      <td className="px-6 py-4 text-sm text-slate-700 whitespace-nowrap">
        {id}
      </td>
      <td className="px-6 py-4 text-sm font-medium text-slate-900 whitespace-nowrap">
        {nombre}
      </td>
      <td className="px-6 py-4 text-sm text-slate-600 max-w-md">
        {descripcion ? (
          <span className="line-clamp-2">{descripcion}</span>
        ) : (
          <span className="text-slate-400 italic">Sin descripción</span>
        )}
      </td>
      <td className="px-6 py-4 text-sm text-right whitespace-nowrap">
        <div className="inline-flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={() => onEdit?.(categoria)}
            className="text-blue-600 hover:text-blue-800 font-medium transition-colors focus:outline-none focus:underline cursor-pointer"
          >
            Editar
          </button>
          {onDelete && (
            <button
              type="button"
              onClick={() => onDelete(id)}
              className="text-rose-600 hover:text-rose-800 font-medium transition-colors focus:outline-none focus:underline cursor-pointer"
            >
              Eliminar
            </button>
          )}
        </div>
      </td>
    </tr>
  );
}

export default CategoriaCard;
