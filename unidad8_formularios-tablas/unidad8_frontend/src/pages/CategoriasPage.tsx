// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [CRUD de Categorías con TanStack Query, TanStack Table v8 y TanStack Form v1]:
//   - CategoriasPage actúa como orquestadora central y propietaria exclusiva de los hooks
//     (useQuery, useMutation, useForm, useReactTable, useState).
//   - CategoriaList, CategoriaCard y CategoriaModal son estrictamente presentacionales sin estado propio.
//   - Carga inicial completa (offset=0, limit=100) para ordenamiento, filtrado y paginación en memoria.
//   - Mutaciones con invalidación de queries y resiliencia ante errores de validación / conflicto (HTTP 409).

import { useState, useMemo, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createColumnHelper,
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
  getCategorias,
  createCategoria,
  updateCategoria,
  deleteCategoria,
} from '../services/categorias.service';
import { CategoriaList } from '../components/CategoriaList';
import { CategoriaModal } from '../components/CategoriaModal';
import type {
  Categoria,
  CategoriaCreate,
  CategoriaFormValues,
} from '../types/categoria';

const EMPTY_CATEGORIAS: Categoria[] = [];

const DEFAULT_CATEGORIA_FORM_VALUES: CategoriaFormValues = {
  nombre: '',
  descripcion: '',
};

const columnHelper = createColumnHelper<Categoria>();

export function CategoriasPage() {
  // Estado local UI y tabla
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingCategoria, setEditingCategoria] = useState<Categoria | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [globalFilter, setGlobalFilter] = useState<string>('');

  const queryClient = useQueryClient();

  // Lectura declarativa con TanStack Query (carga catálogo completo hasta limit=100)
  const { data, isLoading, isFetching, isError, error, refetch } = useQuery({
    queryKey: ['categorias'],
    queryFn: () => getCategorias(0, 100),
  });

  const categorias = data?.items ?? EMPTY_CATEGORIAS;

  // Mutación de Alta
  const createMutation = useMutation({
    mutationFn: (values: CategoriaCreate) => createCategoria(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      handleCloseModal();
    },
  });

  // Mutación de Modificación (PUT /categorias/{id})
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: { nombre: string; descripcion: string } }) =>
      updateCategoria({ id, data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      queryClient.invalidateQueries({ queryKey: ['productos'] });
      handleCloseModal();
    },
  });

  // Mutación de Baja (DELETE /categorias/{id})
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteCategoria(id),
    onSuccess: () => {
      setDeleteError(null);
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
    },
    onError: (err: Error) => {
      setDeleteError(
        err.message || 'No se pudo eliminar la categoría del catálogo.'
      );
    },
  });

  // Instancia de formulario con TanStack Form v1
  const form = useForm({
    defaultValues: {
      nombre: editingCategoria?.nombre ?? '',
      descripcion: editingCategoria?.descripcion ?? '',
    },
    onSubmit: async ({ value }) => {
      const trimmedNombre = value.nombre.trim();
      const trimmedDescripcion = value.descripcion.trim();

      createMutation.reset();
      updateMutation.reset();

      try {
        if (editingCategoria !== null) {
          await updateMutation.mutateAsync({
            id: editingCategoria.id,
            data: {
              nombre: trimmedNombre,
              descripcion: trimmedDescripcion,
            },
          });
        } else {
          await createMutation.mutateAsync({
            nombre: trimmedNombre,
            descripcion: trimmedDescripcion,
          });
        }
      } catch {
        // Error de backend (p. ej. HTTP 409 conflicto por duplicado RN-02).
        // Se preserva en createMutation.error / updateMutation.error,
        // el modal permanece abierto y los valores ingresados no se pierden (HU-02).
      }
    },
  });

  // Controladores del ciclo de vida del modal
  const handleOpenCreate = useCallback(() => {
    setEditingCategoria(null);
    createMutation.reset();
    updateMutation.reset();
    form.reset(DEFAULT_CATEGORIA_FORM_VALUES);
    setIsModalOpen(true);
  }, [createMutation, updateMutation, form]);

  const handleOpenEdit = useCallback(
    (categoria: Categoria) => {
      setEditingCategoria(categoria);
      createMutation.reset();
      updateMutation.reset();
      form.reset({
        nombre: categoria.nombre,
        descripcion: categoria.descripcion ?? '',
      });
      setIsModalOpen(true);
    },
    [createMutation, updateMutation, form]
  );

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    setEditingCategoria(null);
    createMutation.reset();
    updateMutation.reset();
    form.reset(DEFAULT_CATEGORIA_FORM_VALUES);
  }, [createMutation, updateMutation, form]);

  const handleDelete = useCallback(
    (categoria: Categoria) => {
      if (
        window.confirm(
          `¿Está seguro de que desea eliminar la categoría "${categoria.nombre}"?`
        )
      ) {
        setDeleteError(null);
        deleteMutation.mutate(categoria.id);
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
        cell: (info) => info.getValue(),
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
      columnHelper.display({
        id: 'acciones',
        header: 'ACCIONES',
        enableSorting: false,
        cell: ({ row }) => (
          <div className="inline-flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={() => handleOpenEdit(row.original)}
              aria-label={`Editar categoría "${row.original.nombre}"`}
              className="text-blue-600 hover:text-blue-800 font-medium transition-colors focus-visible:outline-none focus-visible:underline cursor-pointer"
            >
              Editar
            </button>
            <button
              type="button"
              onClick={() => handleDelete(row.original)}
              aria-label={`Eliminar categoría "${row.original.nombre}"`}
              className="text-rose-600 hover:text-rose-800 font-medium transition-colors focus-visible:outline-none focus-visible:underline cursor-pointer"
            >
              Eliminar
            </button>
          </div>
        ),
      }),
    ],
    [handleOpenEdit, handleDelete]
  );

  // Instancia de tabla TanStack Table v8
  const table = useReactTable({
    data: categorias,
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

  return (
    <div className="space-y-6">
      {/* Encabezado y resumen */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Gestión de Categorías
            </h1>
            {isFetching && !isLoading && (
              <span role="status" aria-live="polite" className="inline-flex items-center gap-1.5 text-xs text-blue-600 font-medium">
                <span
                  className="inline-block w-2 h-2 rounded-full bg-blue-600 animate-ping"
                  aria-hidden="true"
                />
                Actualizando catálogo...
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Total registradas: {data?.total ?? categorias.length}
          </p>
        </div>

        <button
          type="button"
          onClick={handleOpenCreate}
          className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-xs transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          + Nueva Categoría
        </button>
      </div>

      {/* Barra de herramientas / Búsqueda en memoria */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
        <div className="flex-1 max-w-md">
          <label htmlFor="search-categoria" className="sr-only">
            Buscar categoría por nombre o descripción
          </label>
          <div className="relative">
            <input
              type="search"
              id="search-categoria"
              value={globalFilter}
              onChange={(e) => {
                setGlobalFilter(e.target.value);
                setPagination((prev) => ({ ...prev, pageIndex: 0 }));
              }}
              placeholder="Buscar categoría por nombre o descripción..."
              className="w-full pl-3.5 pr-10 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
            {globalFilter && (
              <button
                type="button"
                onClick={handleClearFilter}
                aria-label="Limpiar búsqueda de categorías"
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
            className="text-rose-600 hover:text-rose-800 font-medium text-xs ml-4 cursor-pointer"
          >
            Descartar
          </button>
        </div>
      )}

      {/* Aviso no destructivo si falla un refetch en segundo plano con datos previos */}
      {isError && data !== undefined && (
        <div
          role="status"
          aria-live="polite"
          className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm flex items-center justify-between"
        >
          <span>
            No se pudo sincronizar el catálogo en segundo plano:{' '}
            {(error as Error)?.message || 'Error de conexión.'}
          </span>
          <button
            type="button"
            onClick={() => void refetch()}
            className="text-amber-900 font-medium underline text-xs ml-4 cursor-pointer hover:text-amber-950"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Estado de carga inicial con Skeleton accesible */}
      {isLoading && (
        <div
          role="status"
          aria-live="polite"
          aria-busy="true"
          className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 animate-pulse motion-reduce:animate-none"
        >
          <div className="flex justify-between items-center pb-4 border-b border-slate-100">
            <div className="h-4 bg-slate-200 rounded w-1/4" />
            <div className="h-4 bg-slate-200 rounded w-1/6" />
          </div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-8 bg-slate-100 rounded" />
            ))}
          </div>
          <span className="sr-only">Cargando categorías...</span>
        </div>
      )}

      {/* Estado de error inicial sin datos previos */}
      {isError && !data && (
        <div
          role="alert"
          aria-live="assertive"
          className="p-8 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-center space-y-4"
        >
          <div>
            <p className="font-semibold text-base">
              Error al cargar las categorías
            </p>
            <p className="text-sm text-rose-600 mt-1">
              {(error as Error)?.message ||
                'Ocurrió un error inesperado al consultar el catálogo.'}
            </p>
          </div>
          <button
            type="button"
            onClick={() => void refetch()}
            className="inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Tabla presentacional conectada a TanStack Table v8 */}
      {!isLoading && (!isError || data !== undefined) && (
        <CategoriaList
          table={table}
          totalCount={categorias.length}
          globalFilter={globalFilter}
          onClearFilter={handleClearFilter}
          onCreateFirst={handleOpenCreate}
        />
      )}

      {/* Modal controlado de Creación / Edición con TanStack Form v1 */}
      <CategoriaModal
        isOpen={isModalOpen}
        isEditing={editingCategoria !== null}
        initialData={editingCategoria}
        form={form}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
        errorMessage={activeModalError}
        onClose={handleCloseModal}
      />
    </div>
  );
}

export default CategoriasPage;
