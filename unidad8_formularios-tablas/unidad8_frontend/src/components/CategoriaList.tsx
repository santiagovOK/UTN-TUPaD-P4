// Base heredada del TP7; identidad y documentación adaptadas al TP8.
import { flexRender, type Table } from '@tanstack/react-table';
import type { Categoria } from '../types/categoria';
import { CategoriaCard } from './CategoriaCard';

// [CRUD de Categorías & Tipado TypeScript]:
// Tabla presentacional pura conectada a TanStack Table v8, con ordenamiento por columnas y paginación accesible.
export interface CategoriaListProps {
  table: Table<Categoria>;
  totalCount: number;
  globalFilter?: string;
  onClearFilter?: () => void;
  onCreateFirst?: () => void;
}

export function CategoriaList({
  table,
  totalCount,
  onClearFilter,
  onCreateFirst,
}: CategoriaListProps) {
  if (totalCount === 0) {
    return (
      <section
        aria-label="Catálogo de categorías"
        className="text-center py-12 px-4 bg-white rounded-xl border border-dashed border-slate-300 space-y-3"
      >
        <p role="status" aria-live="polite" className="text-slate-500 text-base">
          No hay categorías disponibles para mostrar.
        </p>
        {onCreateFirst && (
          <button
            type="button"
            onClick={onCreateFirst}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors cursor-pointer"
          >
            + Crear primera categoría
          </button>
        )}
      </section>
    );
  }

  const { pageIndex, pageSize } = table.getState().pagination;
  const pageCount = table.getPageCount();
  const rows = table.getRowModel().rows;
  const filteredCount = table.getFilteredRowModel().rows.length;

  return (
    <section aria-label="Catálogo de categorías" className="space-y-4">
      <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <caption className="sr-only">
            Listado de categorías del catálogo con ordenamiento y paginación local
          </caption>
          <thead className="bg-slate-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  const canSort = header.column.getCanSort();
                  const isSorted = header.column.getIsSorted();
                  const ariaSort = canSort
                    ? isSorted === 'asc'
                      ? 'ascending'
                      : isSorted === 'desc'
                        ? 'descending'
                        : 'none'
                    : undefined;

                  const isAcciones = header.column.id === 'acciones';

                  return (
                    <th
                      key={header.id}
                      colSpan={header.colSpan}
                      scope="col"
                      aria-sort={ariaSort}
                      className={`px-6 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500 ${
                        isAcciones ? 'text-right' : 'text-left'
                      }`}
                    >
                      {header.isPlaceholder ? null : canSort ? (
                        <button
                          type="button"
                          onClick={header.column.getToggleSortingHandler()}
                          className={`inline-flex items-center gap-1.5 font-semibold text-xs uppercase tracking-wider text-slate-500 hover:text-slate-800 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded px-1 -mx-1 cursor-pointer ${
                            isAcciones ? 'justify-end' : ''
                          }`}
                        >
                          <span>
                            {flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                          </span>
                          <span
                            aria-hidden="true"
                            className="text-slate-400 select-none"
                          >
                            {isSorted === 'asc' ? '▲' : isSorted === 'desc' ? '▼' : '↕'}
                          </span>
                          <span className="sr-only">
                            {isSorted === 'asc'
                              ? '(orden ascendente, activar para descendente)'
                              : isSorted === 'desc'
                                ? '(orden descendente, activar para limpiar)'
                                : '(sin ordenar, activar para ascendente)'}
                          </span>
                        </button>
                      ) : (
                        <span>
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                        </span>
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr className="border-t border-slate-100">
                <td
                  colSpan={table.getVisibleLeafColumns().length}
                  role="status"
                  aria-live="polite"
                  className="px-6 py-10 text-center text-sm text-slate-500 space-y-2"
                >
                  <p>No se encontraron categorías que coincidan con la búsqueda.</p>
                  {onClearFilter && (
                    <button
                      type="button"
                      onClick={onClearFilter}
                      className="text-blue-600 hover:text-blue-800 font-medium underline text-sm transition-colors cursor-pointer"
                    >
                      Limpiar búsqueda
                    </button>
                  )}
                </td>
              </tr>
            ) : (
              rows.map((row) => <CategoriaCard key={row.id} row={row} />)
            )}
          </tbody>
        </table>
      </div>

      <nav
        aria-label="Paginación de categorías"
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white px-6 py-3.5 rounded-xl border border-slate-200 shadow-xs text-sm text-slate-600"
      >
        <div role="status" aria-live="polite" className="flex items-center gap-4">
          <span>
            Página{' '}
            <strong>
              {pageCount === 0 ? 0 : pageIndex + 1} de {pageCount}
            </strong>
          </span>
          <span className="text-slate-300" aria-hidden="true">
            |
          </span>
          <span>
            Total: <strong>{filteredCount}</strong>{' '}
            {filteredCount === 1 ? 'categoría' : 'categorías'}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label htmlFor="categorias-page-size" className="text-xs text-slate-500">
              Filas por página:
            </label>
            <select
              id="categorias-page-size"
              value={pageSize}
              onChange={(e) => table.setPageSize(Number(e.target.value))}
              className="px-2 py-1 border border-slate-300 rounded-md text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              {[5, 10, 20, 50].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              aria-label="Página anterior"
              className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors cursor-pointer"
            >
              Anterior
            </button>
            <button
              type="button"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              aria-label="Página siguiente"
              className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors cursor-pointer"
            >
              Siguiente
            </button>
          </div>
        </div>
      </nav>
    </section>
  );
}

export default CategoriaList;
