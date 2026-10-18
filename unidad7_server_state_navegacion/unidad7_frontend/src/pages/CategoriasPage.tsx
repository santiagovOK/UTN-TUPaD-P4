// [Consigna TP7 - CRUD de Categorías con TanStack Query (HU-01, HU-02, HU-03, RN-02, RN-07)]:
//   - useQuery con clave compuesta ['categorias', { search }] para lectura declarativa y búsqueda incremental.
//   - Consumo directo de data?.items sin copiar a useState local (RN-02: Server State vs Client State).
//   - useMutation para create, update y delete con invalidación de caché (queryClient.invalidateQueries).
//   - Gestión de errores de validación/conflicto y confirmación antes de eliminar.
// [Diagrama UML - Entidad CATEGORIA]: Gestión de ciclo de vida completo de categorías.

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getCategorias,
  createCategoria,
  updateCategoria,
  deleteCategoria,
} from '../services/categorias.service';
import { CategoriaList } from '../components/CategoriaList';
import { CategoriaModal } from '../components/CategoriaModal';
import type { Categoria, CategoriaCreate } from '../types/categoria';

export function CategoriasPage() {
  // Client State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingCategoria, setEditingCategoria] = useState<Categoria | null>(null);
  const [search, setSearch] = useState<string>('');
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // Server State Client
  const queryClient = useQueryClient();

  // Lectura declarativa con TanStack Query (RN-02: Sin useState intermedio para datos del servidor)
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['categorias', { search }],
    queryFn: () => getCategorias(0, 50, search),
  });

  // Mutación de Alta
  const createMutation = useMutation({
    mutationFn: (values: CategoriaCreate) => createCategoria(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      handleCloseModal();
    },
  });

  // Mutación de Modificación
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: CategoriaCreate }) =>
      updateCategoria({ id, data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      handleCloseModal();
    },
  });

  // Mutación de Baja
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteCategoria(id),
    onSuccess: () => {
      setDeleteError(null);
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
    },
    onError: (err: Error) => {
      setDeleteError(err.message || 'No se pudo eliminar la categoría');
    },
  });

  // Controladores de Interfaz
  const handleOpenCreate = () => {
    setEditingCategoria(null);
    createMutation.reset();
    updateMutation.reset();
    setIsModalOpen(true);
  };

  const handleOpenEdit = (categoria: Categoria) => {
    setEditingCategoria(categoria);
    createMutation.reset();
    updateMutation.reset();
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingCategoria(null);
    createMutation.reset();
    updateMutation.reset();
  };

  const handleModalSubmit = (values: CategoriaCreate) => {
    if (editingCategoria !== null) {
      updateMutation.mutate({ id: editingCategoria.id, data: values });
    } else {
      createMutation.mutate(values);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('¿Está seguro de que desea eliminar esta categoría?')) {
      setDeleteError(null);
      deleteMutation.mutate(id);
    }
  };

  const activeModalError =
    createMutation.error?.message || updateMutation.error?.message || null;

  return (
    <div className="space-y-6">
      {/* Encabezado y resumen */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Gestión de Categorías
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Total registradas: {data?.total ?? 0}
          </p>
        </div>

        <button
          type="button"
          onClick={handleOpenCreate}
          className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors cursor-pointer"
        >
          + Nueva Categoría
        </button>
      </div>

      {/* Barra de herramientas / Búsqueda */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <label htmlFor="search-categoria" className="sr-only">
          Buscar categoría por nombre
        </label>
        <input
          type="search"
          id="search-categoria"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar categoría por nombre..."
          className="w-full sm:max-w-md px-3.5 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
        />
      </div>

      {/* Feedback de error en eliminación */}
      {deleteError && (
        <div
          role="alert"
          aria-live="polite"
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

      {/* Estado de carga */}
      {isLoading && (
        <div
          role="status"
          aria-live="polite"
          className="flex justify-center items-center py-16 text-slate-500 text-sm bg-white rounded-xl border border-slate-100"
        >
          <span>Cargando categorías...</span>
        </div>
      )}

      {/* Estado de error */}
      {isError && (
        <div
          role="alert"
          aria-live="assertive"
          className="p-8 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-center space-y-4"
        >
          <div>
            <p className="font-semibold text-base">Error al cargar las categorías</p>
            <p className="text-sm text-rose-600 mt-1">
              {(error as Error)?.message || 'Ocurrió un error inesperado al consultar el catálogo.'}
            </p>
          </div>
          <button
            type="button"
            onClick={() => refetch()}
            className="inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Listado de Categorías */}
      {!isLoading && !isError && (
        <CategoriaList
          categorias={data?.items ?? []}
          onEdit={handleOpenEdit}
          onDelete={handleDelete}
        />
      )}

      {/* Modal controlado de Creación / Edición */}
      <CategoriaModal
        isOpen={isModalOpen}
        initialData={editingCategoria}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
        errorMessage={activeModalError}
        onClose={handleCloseModal}
        onSubmit={handleModalSubmit}
      />
    </div>
  );
}

export default CategoriasPage;
