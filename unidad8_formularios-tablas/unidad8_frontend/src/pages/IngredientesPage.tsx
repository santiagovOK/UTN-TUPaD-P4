// [CRUD de Ingredientes con TanStack Query, TanStack Table v8 y TanStack Form v1]:
//   - IngredientesPage actúa como orquestadora central y propietaria exclusiva de los hooks
//     (useQuery, useMutation, useForm, useReactTable, useState).
//   - IngredienteList e IngredienteModal son estrictamente presentacionales sin estado propio.
//   - Carga inicial completa (offset=0, limit=100) para ordenamiento, filtrado y paginación en memoria.
//   - Carga del catálogo de unidades de medida (/unidades-medida/) para resolución de nombres y selección en modal.
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
  getIngredientes,
  createIngrediente,
  updateIngrediente,
  deleteIngrediente,
  getUnidadesMedida,
} from '../services/ingredientes.service';
import { IngredienteList } from '../components/IngredienteList';
import { IngredienteModal } from '../components/IngredienteModal';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import type {
  Ingrediente,
  IngredienteCreate,
  IngredienteUpdate,
  IngredienteFormValues,
  UnidadMedida,
} from '../types/ingrediente';

const EMPTY_INGREDIENTES: Ingrediente[] = [];
const EMPTY_UNIDADES: UnidadMedida[] = [];

const DEFAULT_INGREDIENTE_FORM_VALUES: IngredienteFormValues = {
  nombre: '',
  descripcion: '',
  unidad_medida_id: '',
  activo: true,
};

const columnHelper = createColumnHelper<Ingrediente>();

export function IngredientesPage() {
  // Estado local UI y tabla
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingIngrediente, setEditingIngrediente] = useState<Ingrediente | null>(null);
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
    queryKey: ['ingredientes'],
    queryFn: () => getIngredientes(0, 100),
  });

  const ingredientes = data?.items ?? EMPTY_INGREDIENTES;

  // Consulta de catálogo de unidades de medida
  const unidadesQuery = useQuery({
    queryKey: ['unidades-medida'],
    queryFn: getUnidadesMedida,
  });

  const unidadesMedida = unidadesQuery.data?.items ?? EMPTY_UNIDADES;

  const unidadesMap = useMemo(
    () => new Map(unidadesMedida.map((u) => [u.id, u])),
    [unidadesMedida]
  );

  // Mutación de Alta
  const createMutation = useMutation({
    mutationFn: (values: IngredienteCreate) => createIngrediente(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingredientes'] });
      queryClient.invalidateQueries({ queryKey: ['productos'] });
      handleCloseModal();
    },
  });

  // Mutación de Modificación (PUT /ingredientes/{id})
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: IngredienteUpdate }) =>
      updateIngrediente({ id, data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ingredientes'] });
      queryClient.invalidateQueries({ queryKey: ['productos'] });
      handleCloseModal();
    },
  });

  // Mutación de Baja (DELETE /ingredientes/{id})
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteIngrediente(id),
    onSuccess: () => {
      setDeleteError(null);
      queryClient.invalidateQueries({ queryKey: ['ingredientes'] });
      queryClient.invalidateQueries({ queryKey: ['productos'] });
    },
    onError: (err: Error) => {
      setDeleteError(
        err.message || 'No se pudo eliminar el ingrediente del catálogo.'
      );
    },
  });

  // Instancia de formulario con TanStack Form v1
  const form = useForm({
    defaultValues: {
      nombre: editingIngrediente?.nombre ?? '',
      descripcion: editingIngrediente?.descripcion ?? '',
      unidad_medida_id: editingIngrediente
        ? String(editingIngrediente.unidad_medida_id)
        : '',
      activo: editingIngrediente?.activo ?? true,
    },
    onSubmit: async ({ value }) => {
      const trimmedNombre = value.nombre.trim();
      const trimmedDescripcion = value.descripcion.trim();
      const parsedUnidadId = Number(value.unidad_medida_id);

      createMutation.reset();
      updateMutation.reset();

      try {
        if (editingIngrediente !== null) {
          await updateMutation.mutateAsync({
            id: editingIngrediente.id,
            data: {
              nombre: trimmedNombre,
              descripcion: trimmedDescripcion,
              unidad_medida_id: parsedUnidadId,
              activo: value.activo,
            },
          });
        } else {
          await createMutation.mutateAsync({
            nombre: trimmedNombre,
            descripcion: trimmedDescripcion,
            unidad_medida_id: parsedUnidadId,
            activo: value.activo,
          });
        }
      } catch {
        // Error de backend (p. ej. HTTP 409 conflicto por duplicado RN-02/RN-10).
        // Se preserva en createMutation.error / updateMutation.error,
        // el modal permanece abierto y los valores ingresados no se pierden (HU-05).
      }
    },
  });

  // Controladores del ciclo de vida del modal
  const handleOpenCreate = useCallback(() => {
    setEditingIngrediente(null);
    createMutation.reset();
    updateMutation.reset();
    form.reset({
      nombre: '',
      descripcion: '',
      unidad_medida_id:
        unidadesMedida.length > 0 ? String(unidadesMedida[0].id) : '',
      activo: true,
    });
    setIsModalOpen(true);
  }, [createMutation, updateMutation, form, unidadesMedida]);

  const handleOpenEdit = useCallback(
    (ingrediente: Ingrediente) => {
      setEditingIngrediente(ingrediente);
      createMutation.reset();
      updateMutation.reset();
      form.reset({
        nombre: ingrediente.nombre,
        descripcion: ingrediente.descripcion ?? '',
        unidad_medida_id: String(ingrediente.unidad_medida_id),
        activo: ingrediente.activo,
      });
      setIsModalOpen(true);
    },
    [createMutation, updateMutation, form]
  );

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    setEditingIngrediente(null);
    createMutation.reset();
    updateMutation.reset();
    form.reset(DEFAULT_INGREDIENTE_FORM_VALUES);
  }, [createMutation, updateMutation, form]);

  const handleDelete = useCallback(
    (ingrediente: Ingrediente) => {
      if (
        window.confirm(
          `¿Está seguro de que desea eliminar el ingrediente "${ingrediente.nombre}"?`
        )
      ) {
        setDeleteError(null);
        deleteMutation.mutate(ingrediente.id);
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
      columnHelper.accessor('unidad_medida_id', {
        header: 'UNIDAD DE MEDIDA',
        cell: (info) => {
          const unidadId = Number(info.getValue());
          const unidad = unidadesMap.get(unidadId);
          return unidad ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
              {unidad.nombre} ({unidad.simbolo})
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
              Unidad #{unidadId}
            </span>
          );
        },
      }),
      columnHelper.accessor('activo', {
        header: 'ESTADO',
        cell: (info) => {
          const activo = info.getValue();
          return activo ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              Activo
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
              Inactivo
            </span>
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
              aria-label={`Editar ingrediente "${row.original.nombre}"`}
              className="text-blue-600 hover:text-blue-800 font-medium transition-colors focus-visible:outline-none focus-visible:underline cursor-pointer"
            >
              Editar
            </button>
            <button
              type="button"
              onClick={() => handleDelete(row.original)}
              aria-label={`Eliminar ingrediente "${row.original.nombre}"`}
              className="text-rose-600 hover:text-rose-800 font-medium transition-colors focus-visible:outline-none focus-visible:underline cursor-pointer"
            >
              Eliminar
            </button>
          </div>
        ),
      }),
    ],
    [unidadesMap, handleOpenEdit, handleDelete]
  );

  // Instancia de tabla con TanStack Table v8
  const table = useReactTable({
    data: ingredientes,
    columns,
    state: {
      sorting,
      pagination,
      globalFilter,
    },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  const activeModalError =
    (createMutation.error as Error | null)?.message ??
    (updateMutation.error as Error | null)?.message ??
    null;

  return (
    <div className="space-y-6">
      {/* Encabezado y acción principal */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Gestión de Ingredientes
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Administre el catálogo de materias primas e insumos de la pizzería.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full border border-slate-200">
            Total registrados: {ingredientes.length}
          </span>
          <button
            type="button"
            onClick={handleOpenCreate}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg shadow-xs transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer"
          >
            + Nuevo Ingrediente
          </button>
        </div>
      </div>

      {/* Barra de herramientas / Búsqueda en memoria */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
        <div className="flex-1 max-w-md">
          <label htmlFor="search-ingrediente" className="sr-only">
            Buscar ingrediente por nombre o descripción
          </label>
          <div className="relative">
            <input
              type="search"
              id="search-ingrediente"
              value={globalFilter}
              onChange={(e) => {
                setGlobalFilter(e.target.value);
                setPagination((prev) => ({ ...prev, pageIndex: 0 }));
              }}
              placeholder="Buscar ingrediente por nombre o descripción..."
              className="w-full pl-3.5 pr-10 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
            {globalFilter && (
              <button
                type="button"
                onClick={handleClearFilter}
                aria-label="Limpiar búsqueda de ingredientes"
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
        <ErrorState
          variant="background"
          title="No se pudo sincronizar el catálogo en segundo plano"
          message={(error as Error)?.message || 'Error de conexión.'}
          onRetry={() => void refetch()}
          isRetrying={isFetching}
        />
      )}

      {/* Estado de carga inicial con Skeleton accesible */}
      {isLoading && <LoadingState message="Cargando ingredientes..." />}

      {/* Estado de error inicial sin datos previos */}
      {isError && !data && (
        <ErrorState
          title="Error al cargar los ingredientes"
          message={
            (error as Error)?.message ||
            'Ocurrió un error inesperado al consultar el catálogo.'
          }
          onRetry={() => void refetch()}
          isRetrying={isFetching}
        />
      )}

      {/* Tabla presentacional conectada a TanStack Table v8 */}
      {!isLoading && (!isError || data !== undefined) && (
        <IngredienteList
          table={table}
          totalCount={ingredientes.length}
          globalFilter={globalFilter}
          onClearFilter={handleClearFilter}
          onCreateFirst={handleOpenCreate}
        />
      )}

      {/* Modal controlado de Creación / Edición con TanStack Form v1 */}
      <IngredienteModal
        isOpen={isModalOpen}
        isEditing={editingIngrediente !== null}
        initialData={editingIngrediente}
        form={form}
        unidadesMedida={unidadesMedida}
        isLoadingUnidades={unidadesQuery.isLoading}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
        errorMessage={activeModalError}
        onClose={handleCloseModal}
      />
    </div>
  );
}

export default IngredientesPage;
