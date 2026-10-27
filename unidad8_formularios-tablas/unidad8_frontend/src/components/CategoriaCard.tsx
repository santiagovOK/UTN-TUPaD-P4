// Base heredada del TP7; identidad y documentación adaptadas al TP8.
import { flexRender, type Row } from '@tanstack/react-table';
import type { Categoria } from '../types/categoria';

// [CRUD de Categorías & Tipado TypeScript]:
// Fila presentacional que renderiza las celdas visibles de Row<Categoria> mediante TanStack Table flexRender.
export interface CategoriaCardProps {
  row: Row<Categoria>;
}

export function CategoriaCard({ row }: CategoriaCardProps) {
  return (
    <tr className="border-t border-slate-100 hover:bg-slate-50 transition-colors">
      {row.getVisibleCells().map((cell) => {
        const colId = cell.column.id;
        const cellClassName =
          colId === 'acciones'
            ? 'px-6 py-4 text-sm text-right whitespace-nowrap'
            : colId === 'descripcion'
              ? 'px-6 py-4 text-sm text-slate-600 max-w-md'
              : colId === 'nombre'
                ? 'px-6 py-4 text-sm font-medium text-slate-900 whitespace-nowrap'
                : 'px-6 py-4 text-sm text-slate-700 whitespace-nowrap';

        return (
          <td key={cell.id} className={cellClassName}>
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        );
      })}
    </tr>
  );
}

export default CategoriaCard;
