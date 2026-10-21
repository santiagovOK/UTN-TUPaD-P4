// Base heredada del TP7; identidad y documentación adaptadas al TP8.
import type { Categoria } from '../types/categoria';
import { CategoriaCard } from './CategoriaCard';

// [CRUD de Categorías & Tipado TypeScript]: Tabla presentacional que recibe Categoria[] por props tipados.
// [Diagrama UML - Entidad CATEGORIA]: Lista los registros activos del catálogo (excluyendo bajas lógicas deleted_at != NULL en el backend).
export interface CategoriaListProps {
  categorias: Categoria[];
  onEdit?: (categoria: Categoria) => void;
  onDelete?: (id: number) => void;
}

export function CategoriaList({ categorias, onEdit, onDelete }: CategoriaListProps) {
  if (categorias.length === 0) {
    return (
      <section
        aria-label="Catálogo de categorías"
        className="text-center py-12 bg-white rounded-xl border border-dashed border-slate-300"
      >
        <p role="status" aria-live="polite" className="text-slate-500 text-base">
          No hay categorías disponibles para mostrar.
        </p>
      </section>
    );
  }

  return (
    <section aria-label="Catálogo de categorías">
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                NÚMERO
              </th>
              <th
                scope="col"
                className="px-6 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                NOMBRE
              </th>
              <th
                scope="col"
                className="px-6 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                DESCRIPCIÓN
              </th>
              <th
                scope="col"
                className="px-6 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500 text-right"
              >
                ACCIONES
              </th>
            </tr>
          </thead>
          <tbody>
            {categorias.map((categoria) => (
              <CategoriaCard
                key={categoria.id}
                categoria={categoria}
                onEdit={onEdit}
                onDelete={onDelete}
              />
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default CategoriaList;
