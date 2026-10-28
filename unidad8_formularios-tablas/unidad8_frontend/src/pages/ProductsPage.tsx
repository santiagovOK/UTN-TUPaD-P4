// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [Catálogo Paginado de Productos con TanStack Query, TanStack Table v8 y TanStack Form v1]:
//   - ProductsPage actúa como orquestadora central y propietaria exclusiva de los hooks
//     (useQuery, useMutation, useForm, useReactTable, useState).
//   - Carga inicial completa (offset=0, limit=100) para ordenamiento, filtrado y paginación en memoria.
//   - ProductoModal es un componente presentacional puro conectado a ProductoFormApi.
//   - Preservación de la navegación hacia el detalle individual (/productos/:id).

import { useState, useMemo, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type PaginationState,
  type SortingState,
} from '@tanstack/react-table';
import { useForm } from '@tanstack/react-form';
import {
  getProductos,
  createProducto,
  updateProducto,
  deleteProducto,
} from '../services/productos.service';
import { getCategorias } from '../services/categorias.service';
import { ProductoModal } from '../components/ProductoModal';
import { LoadingState } from '../components/LoadingState';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import type {
  Producto,
  ProductoCreate,
  ProductoUpdate,
  ProductoFormValues,
} from '../types/producto';
import type { Categoria } from '../types/categoria';

const EMPTY_PRODUCTOS: Producto[] = [];
const EMPTY_CATEGORIAS: Categoria[] = [];

const DEFAULT_PRODUCTO_FORM_VALUES: ProductoFormValues = {
  nombre: '',
  descripcion: '',
  precio_base: '',
  disponible: true,
  categoria_ids: [],
};

const columnHelper = createColumnHelper<Producto>();

export function ProductsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Estado local UI y tabla
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingProducto, setEditingProducto] = useState<Producto | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [globalFilter, setGlobalFilter] = useState<string>('');

  // Lectura declarativa con TanStack Query (carga catálogo completo hasta limit=100)
  const { data, isLoading, isFetching, isError, error, refetch } = useQuery({
    queryKey: ['productos'],
    queryFn: () => getProductos(0, 100),
  });

  const productos = data?.items ?? EMPTY_PRODUCTOS;

  // Consulta de categorías disponibles para el modal
  const categoriasQuery = useQuery({
    queryKey: ['categorias'],
    queryFn: () => getCategorias(0, 100),
  });

  const categoriasDisponibles =
    categoriasQuery.data?.items ?? EMPTY_CATEGORIAS;

  // Mutación de Alta
  const createMutation = useMutation({
    mutationFn: (values: ProductoCreate) => createProducto(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      handleCloseModal();
    },
  });

  // Mutación de Modificación (PUT /productos/{id})
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductoUpdate }) =>
      updateProducto({ id, data }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['productos'] });
      queryClient.invalidateQueries({ queryKey: ['producto', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      handleCloseModal();
    },
  });

  // Mutación de Baja (DELETE /productos/{id})
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteProducto(id),
    onSuccess: () => {
      setDeleteError(null);
      queryClient.invalidateQueries({ queryKey: ['productos'] });
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
    },
    onError: (err: Error) => {
      setDeleteError(
        err.message || 'No se pudo eliminar el producto del catálogo.'
      );
    },
  });

  // Instancia de formulario con TanStack Form v1
  const form = useForm({
    defaultValues: {
      nombre: editingProducto?.nombre ?? '',
      descripcion: editingProducto?.descripcion ?? '',
      precio_base: editingProducto ? String(editingProducto.precio_base) : '',
      disponible: editingProducto?.disponible ?? true,
      categoria_ids: editingProducto?.categorias?.map((c) => c.id) ?? [],
    },
    onSubmit: async ({ value }) => {
      const trimmedNombre = value.nombre.trim();
      const trimmedDescripcion = value.descripcion.trim();
      const parsedPrecio = Number(value.precio_base.trim());

      createMutation.reset();
      updateMutation.reset();

      try {
        if (editingProducto !== null) {
          await updateMutation.mutateAsync({
            id: editingProducto.id,
            data: {
              nombre: trimmedNombre,
              descripcion: trimmedDescripcion || null,
              precio_base: parsedPrecio,
              disponible: value.disponible,
              categoria_ids: value.categoria_ids,
            },
          });
        } else {
          await createMutation.mutateAsync({
            nombre: trimmedNombre,
            descripcion: trimmedDescripcion || null,
            precio_base: parsedPrecio,
            disponible: value.disponible,
            categoria_ids: value.categoria_ids,
          });
        }
      } catch {
        // Error de backend preservado en mutation.error, el modal permanece abierto con datos intactos
      }
    },
  });

  // Controladores del ciclo de vida del modal
  const handleOpenCreate = useCallback(() => {
    setEditingProducto(null);
    createMutation.reset();
    updateMutation.reset();
    form.reset(DEFAULT_PRODUCTO_FORM_VALUES);
    setIsModalOpen(true);
  }, [createMutation, updateMutation, form]);

  const handleOpenEdit = useCallback(
    (producto: Producto) => {
      setEditingProducto(producto);
      createMutation.reset();
      updateMutation.reset();
      form.reset({
        nombre: producto.nombre,
        descripcion: producto.descripcion ?? '',
        precio_base: String(producto.precio_base),
        disponible: producto.disponible,
        categoria_ids: producto.categorias?.map((c) => c.id) ?? [],
      });
      setIsModalOpen(true);
    },
    [createMutation, updateMutation, form]
  );

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    setEditingProducto(null);
    createMutation.reset();
    updateMutation.reset();
    form.reset(DEFAULT_PRODUCTO_FORM_VALUES);
  }, [createMutation, updateMutation, form]);

  const handleDelete = useCallback(
    (producto: Producto) => {
      if (
        window.confirm(
          `¿Está seguro de que desea eliminar el producto "${producto.nombre}"?`
        )
      ) {
        setDeleteError(null);
        deleteMutation.mutate(producto.id);
      }
    },
    [deleteMutation]
  );

  const handleClearFilter = useCallback(() => {
    setGlobalFilter('');
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));
  }, []);

  // Bloqueo de scroll de fondo y atajo Escape accesible
  useEffect(() => {
    if (!isModalOpen) return;

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === 'Escape' &&
        !createMutation.isPending &&
        !updateMutation.isPending
      ) {
        handleCloseModal();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [
    isModalOpen,
    createMutation.isPending,
    updateMutation.isPending,
    handleCloseModal,
  ]);

  // Definición de columnas para TanStack Table
  const columns = useMemo(
    () => [
      columnHelper.accessor('id', {
        header: 'NÚMERO',
        cell: (info) => `#${info.getValue()}`,
      }),
      columnHelper.accessor('nombre', {
        header: 'NOMBRE',
        cell: (info) => (
          <span className="font-medium text-slate-900">{info.getValue()}</span>
        ),
      }),
      columnHelper.accessor('descripcion', {
        header: 'DESCRIPCIÓN',
        cell: (info) => {
          const desc = info.getValue();
          return desc ? (
            <span className="line-clamp-2">{desc}</span>
          ) : (
            <span className="text-slate-400 italic">Sin descripción</span>
          );
        },
      }),
      columnHelper.accessor('precio_base', {
        header: 'PRECIO BASE',
        cell: (info) => {
          const val = Number(info.getValue());
          const formatted = val.toFixed(2);
          return (
            <span
              className="font-semibold text-emerald-600"
              aria-label={`Precio base: $${formatted}`}
            >
              ${formatted}
            </span>
          );
        },
      }),
      columnHelper.accessor('disponible', {
        header: 'ESTADO',
        cell: (info) => {
          const disp = info.getValue();
          return disp ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              Disponible
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
              No disponible
            </span>
          );
        },
      }),
      columnHelper.accessor('categorias', {
        header: 'CATEGORÍAS',
        enableSorting: false,
        cell: ({ row }) => {
          const cats = row.original.categorias;
          if (!cats || cats.length === 0) {
            return (
              <span className="text-slate-400 italic">Sin categorías</span>
            );
          }
          return (
            <ul
              aria-label={`Categorías de ${row.original.nombre}`}
              className="flex flex-wrap gap-1.5"
            >
              {cats.map((cat) => (
                <li
                  key={cat.id}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700"
                >
                  {cat.nombre}
                </li>
              ))}
            </ul>
          );
        },
      }),
      columnHelper.display({
        id: 'acciones',
        header: 'ACCIONES',
        enableSorting: false,
        cell: ({ row }) => (
          <div className="inline-flex items-center justify-center gap-3">
            <button
              type="button"
              onClick={() => navigate(`/productos/${row.original.id}`)}
              aria-label={`Ver detalle del producto "${row.original.nombre}"`}
              className="text-slate-600 hover:text-slate-900 font-medium transition-colors focus-visible:outline-none focus-visible:underline cursor-pointer"
            >
              Ver detalle
            </button>
            <button
              type="button"
              onClick={() => handleOpenEdit(row.original)}
              aria-label={`Editar producto "${row.original.nombre}"`}
              className="text-blue-600 hover:text-blue-800 font-medium transition-colors focus-visible:outline-none focus-visible:underline cursor-pointer"
            >
              Editar
            </button>
            <button
              type="button"
              onClick={() => handleDelete(row.original)}
              aria-label={`Eliminar producto "${row.original.nombre}"`}
              className="text-rose-600 hover:text-rose-800 font-medium transition-colors focus-visible:outline-none focus-visible:underline cursor-pointer"
            >
              Eliminar
            </button>
          </div>
        ),
      }),
    ],
    [navigate, handleOpenEdit, handleDelete]
  );

  // Instancia de tabla TanStack Table v8
  const table = useReactTable({
    data: productos,
    columns,
    getRowId: (row) => String(row.id),
    state: {
      sorting,
      pagination,
      globalFilter,
    },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  const activeModalError =
    createMutation.error?.message || updateMutation.error?.message || null;

  const { pageIndex, pageSize } = table.getState().pagination;
  const pageCount = table.getPageCount();
  const rows = table.getRowModel().rows;
  const filteredCount = table.getFilteredRowModel().rows.length;

  return (
    <div className="space-y-6">
      {/* Encabezado y resumen */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Catálogo de Productos
            </h1>
            {isFetching && !isLoading && (
              <span
                role="status"
                aria-live="polite"
                className="inline-flex items-center gap-1.5 text-xs text-blue-600 font-medium"
              >
                <span
                  className="inline-block w-2 h-2 rounded-full bg-blue-600 animate-ping"
                  aria-hidden="true"
                />
                Actualizando catálogo...
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Total registrados: {data?.total ?? productos.length}
          </p>
        </div>

        <button
          type="button"
          onClick={handleOpenCreate}
          className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-xs transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          + Nuevo Producto
        </button>
      </div>

      {/* Barra de herramientas / Búsqueda en memoria */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
        <div className="flex-1 max-w-md">
          <label htmlFor="search-producto" className="sr-only">
            Buscar producto por nombre o descripción
          </label>
          <div className="relative">
            <input
              type="search"
              id="search-producto"
              value={globalFilter}
              onChange={(e) => {
                setGlobalFilter(e.target.value);
                setPagination((prev) => ({ ...prev, pageIndex: 0 }));
              }}
              placeholder="Buscar producto por nombre o descripción..."
              className="w-full pl-3.5 pr-10 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
            {globalFilter && (
              <button
                type="button"
                onClick={handleClearFilter}
                aria-label="Limpiar búsqueda de productos"
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-600 font-medium px-1.5 py-0.5 rounded cursor-pointer"
                title="Limpiar búsqueda"
              >
                Limpiar
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Feedback de error en eliminación */}
      {deleteError && (
        <div
          role="alert"
          className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center justify-between"
        >
          <span>{deleteError}</span>
          <button
            type="button"
            onClick={() => setDeleteError(null)}
            aria-label="Descartar mensaje de error"
            className="text-rose-600 hover:text-rose-800 font-medium text-xs ml-4 cursor-pointer"
          >
            Descartar
          </button>
        </div>
      )}

      {/* Aviso no destructivo si falla un refetch en segundo plano con datos previos */}
      {isError && data !== undefined && (
        <ErrorState
          variant="background"
          title="No se pudo sincronizar el catálogo en segundo plano"
          message={(error as Error)?.message || 'Error de conexión.'}
          onRetry={() => void refetch()}
          isRetrying={isFetching}
        />
      )}

      {/* Estado de carga inicial con Skeleton accesible */}
      {isLoading && <LoadingState message="Cargando productos..." />}

      {/* Estado de error inicial sin datos previos */}
      {isError && !data && (
        <ErrorState
          title="Error al cargar los productos"
          message={
            (error as Error)?.message ||
            'Ocurrió un error inesperado al consultar el catálogo.'
          }
          onRetry={() => void refetch()}
          isRetrying={isFetching}
        />
      )}

      {/* Catálogo vacío */}
      {!isLoading &&
        (!isError || data !== undefined) &&
        productos.length === 0 && (
          <EmptyState
            ariaLabel="Catálogo de productos"
            message="No hay productos disponibles para mostrar."
            actionLabel="+ Crear primer producto"
            onAction={handleOpenCreate}
          />
        )}

      {/* Tabla presentacional conectada a TanStack Table v8 */}
      {!isLoading && (!isError || data !== undefined) && productos.length > 0 && (
        <section aria-label="Catálogo de productos" className="space-y-4">
          <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
              <caption className="sr-only">
                Listado de productos del catálogo con ordenamiento y paginación
                local
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
                          className={`py-3 text-xs font-semibold uppercase tracking-wider text-slate-500 ${
                            isAcciones
                              ? 'text-center pl-2 pr-6 min-w-[210px]'
                              : 'text-left px-3'
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
                                {isSorted === 'asc'
                                  ? '▲'
                                  : isSorted === 'desc'
                                    ? '▼'
                                    : '↕'}
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
                      <p>
                        No se encontraron productos que coincidan con la
                        búsqueda.
                      </p>
                      <button
                        type="button"
                        onClick={handleClearFilter}
                        className="text-blue-600 hover:text-blue-800 font-medium underline text-sm transition-colors cursor-pointer"
                      >
                        Limpiar búsqueda
                      </button>
                    </td>
                  </tr>
                ) : (
                  rows.map((row) => (
                    <tr
                      key={row.id}
                      className="border-t border-slate-100 hover:bg-slate-50 transition-colors"
                    >
                      {row.getVisibleCells().map((cell) => {
                        const colId = cell.column.id;
                        const cellClassName =
                          colId === 'acciones'
                            ? 'pl-2 pr-6 py-3 text-sm text-center whitespace-nowrap min-w-[210px]'
                            : colId === 'descripcion'
                              ? 'px-3 py-3 text-sm text-slate-600 max-w-[180px]'
                              : colId === 'nombre'
                                ? 'px-3 py-3 text-sm font-medium text-slate-900 whitespace-nowrap'
                                : colId === 'precio_base'
                                  ? 'px-3 py-3 text-sm font-medium text-slate-900 whitespace-nowrap'
                                  : colId === 'disponible'
                                    ? 'px-3 py-3 text-sm whitespace-nowrap'
                                    : colId === 'categorias'
                                      ? 'px-3 py-3 text-sm max-w-[160px]'
                                      : colId === 'id'
                                        ? 'px-3 py-3 text-sm text-slate-700 whitespace-nowrap w-16'
                                        : 'px-3 py-3 text-sm text-slate-700 whitespace-nowrap';

                        return (
                          <td key={cell.id} className={cellClassName}>
                            {flexRender(
                              cell.column.columnDef.cell,
                              cell.getContext()
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))
                )}
              </tbody>
              </table>
            </div>
          </div>

          <nav
            aria-label="Paginación de productos"
            className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white px-6 py-3.5 rounded-xl border border-slate-200 shadow-xs text-sm text-slate-600"
          >
            <div
              role="status"
              aria-live="polite"
              className="flex items-center gap-4"
            >
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
                {filteredCount === 1 ? 'producto' : 'productos'}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <label
                  htmlFor="productos-page-size"
                  className="text-xs text-slate-500"
                >
                  Filas por página:
                </label>
                <select
                  id="productos-page-size"
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
      )}

      {/* Modal controlado de Creación / Edición con TanStack Form v1 */}
      <ProductoModal
        isOpen={isModalOpen}
        isEditing={editingProducto !== null}
        initialData={editingProducto}
        form={form}
        categoriasDisponibles={categoriasDisponibles}
        isLoadingCategorias={categoriasQuery.isLoading}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
        errorMessage={activeModalError}
        onClose={handleCloseModal}
      />
    </div>
  );
}

export default ProductsPage;
