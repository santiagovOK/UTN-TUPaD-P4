import type { Categoria } from '../types/categoria';
import { CategoriaCard } from './CategoriaCard';

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
        className="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300"
      >
        <p role="status" aria-live="polite" className="text-gray-500 text-base">
          No hay categorías disponibles para mostrar.
        </p>
      </section>
    );
  }

  return (
    <section aria-label="Catálogo de categorías">
      <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 list-none p-0 m-0">
        {categorias.map((categoria) => (
          <li key={categoria.id} className="flex">
            <CategoriaCard
              categoria={categoria}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          </li>
        ))}
      </ul>
    </section>
  );
}

export default CategoriaList;
