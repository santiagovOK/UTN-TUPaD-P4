// [Consigna TP7 - Catálogo Paginado de Productos (HU-04, HU-05, RN-01, RN-02, RN-07)]:
//   - Client State con useState para paginación reactiva (page base 1) y búsqueda incremental por nombre.
//   - Server State con TanStack Query (useQuery) con clave compuesta ['productos', { offset, limit, nombre }].
//   - Garantía RN-02: Cero duplicación de data?.items en useState locales; renderizado directo y declarativo.
//   - Navegación programática hacia el detalle individual con useNavigate (/productos/:id).
//   - Accesibilidad: Landmark <nav> para paginador, regiones vivas (role status/alert), <article> por tarjeta,
//     listas semánticas (<ul>/<li>) y estilos de foco por teclado (focus-visible).
// [Diagrama UML - Clúster Catálogo de Productos (docs/UML_FOOD_STORE.svg)]:
//   - Visualización de atributos: nombre, descripción, precio_base formateado, disponibilidad y badges N:N de categorías.

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getProductos } from '../services/productos.service';
import type { Producto } from '../types/producto';

export const PAGE_SIZE = 6;

export function ProductsPage() {
  const navigate = useNavigate();

  // Client State
  const [page, setPage] = useState<number>(1);
  const [nombre, setNombre] = useState<string>('');

  // Cálculo de desplazamiento
  const offset = (page - 1) * PAGE_SIZE;

  // Server State con TanStack Query (RN-02: Sin useState intermedio para datos del servidor)
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['productos', { offset, limit: PAGE_SIZE, nombre }],
    queryFn: () => getProductos(offset, PAGE_SIZE, nombre),
  });

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const items: Producto[] = data?.items ?? [];

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNombre(e.target.value);
    setPage(1);
  };

  const handleClearSearch = () => {
    setNombre('');
    setPage(1);
  };

  const handlePrevPage = () => {
    setPage((prev) => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setPage((prev) => Math.min(totalPages, prev + 1));
  };

  return (
    <div className="space-y-6">
      {/* Encabezado y resumen del catálogo */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Catálogo de Productos
          </h1>
          <p
            className="text-sm text-slate-500 mt-1"
            role="status"
            aria-live="polite"
          >
            Mostrando {items.length} de {total} productos
          </p>
        </div>
      </div>

      {/* Barra de herramientas / Búsqueda */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <label htmlFor="search-producto" className="sr-only">
          Filtrar productos por nombre
        </label>
        <div className="relative flex items-center">
          <input
            type="search"
            id="search-producto"
            value={nombre}
            onChange={handleSearchChange}
            placeholder="Filtrar productos por nombre..."
            className="w-full sm:max-w-md px-3.5 py-2 border border-slate-300 rounded-lg text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          />
          {nombre && (
            <button
              type="button"
              onClick={handleClearSearch}
              aria-label="Limpiar filtro de búsqueda"
              className="ml-2 text-xs font-medium text-slate-500 hover:text-slate-800 underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded cursor-pointer"
            >
              Limpiar filtro
            </button>
          )}
        </div>
      </div>

      {/* Estado de carga */}
      {isLoading && (
        <div
          role="status"
          aria-live="polite"
          className="flex justify-center items-center py-16 text-slate-500 text-sm bg-white rounded-xl border border-slate-100"
        >
          <span>Cargando productos...</span>
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
            <p className="font-semibold text-base">Error al cargar los productos</p>
            <p className="text-sm text-rose-600 mt-1">
              {(error as Error)?.message || 'Ocurrió un error inesperado al consultar el catálogo.'}
            </p>
          </div>
          <button
            type="button"
            onClick={() => refetch()}
            className="inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500 cursor-pointer"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Estado vacío */}
      {!isLoading && !isError && items.length === 0 && (
        <div
          role="status"
          aria-live="polite"
          className="p-12 text-center bg-white rounded-xl border border-slate-200 space-y-3"
        >
          <p className="text-base font-medium text-slate-700">
            No se encontraron productos coincidentes.
          </p>
          {nombre && (
            <button
              type="button"
              onClick={handleClearSearch}
              aria-label="Limpiar filtro de búsqueda"
              className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-indigo-600 hover:text-indigo-800 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 rounded cursor-pointer"
            >
              Limpiar filtro de búsqueda
            </button>
          )}
        </div>
      )}

      {/* Grilla de tarjetas */}
      {!isLoading && !isError && items.length > 0 && (
        <section aria-label="Catálogo de productos disponibles">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((prod) => (
              <article
                key={prod.id}
                aria-labelledby={`producto-titulo-${prod.id}`}
                className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-colors"
              >
                <div className="space-y-3">
                  {/* Cabecera de la tarjeta: Título y Precio */}
                  <div className="flex items-start justify-between gap-2">
                    <h2
                      id={`producto-titulo-${prod.id}`}
                      className="text-base font-semibold text-slate-900 leading-snug"
                    >
                      {prod.nombre}
                    </h2>
                    <span
                      className="text-base font-bold text-emerald-600 shrink-0"
                      aria-label={`Precio: $${Number(prod.precio_base).toFixed(2)}`}
                    >
                      ${Number(prod.precio_base).toFixed(2)}
                    </span>
                  </div>

                  {/* Badge de Disponibilidad */}
                  <div>
                    {prod.disponible ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Disponible
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
                        No disponible
                      </span>
                    )}
                  </div>

                  {/* Descripción */}
                  <p className="text-sm text-slate-600 line-clamp-3">
                    {prod.descripcion ? (
                      prod.descripcion
                    ) : (
                      <span className="text-slate-400 italic">Sin descripción</span>
                    )}
                  </p>

                  {/* Badges de Categorías */}
                  <div className="pt-2">
                    <span
                      id={`categorias-label-${prod.id}`}
                      className="text-xs font-medium text-slate-500 mb-1.5 block"
                    >
                      Categorías:
                    </span>
                    {prod.categorias && prod.categorias.length > 0 ? (
                      <ul
                        aria-labelledby={`categorias-label-${prod.id}`}
                        className="flex flex-wrap gap-1.5 list-none p-0 m-0"
                      >
                        {prod.categorias.map((cat) => (
                          <li key={cat.id}>
                            <span className="inline-block bg-indigo-50 text-indigo-700 text-xs px-2.5 py-0.5 rounded-full font-medium">
                              {cat.nombre}
                            </span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-xs text-slate-400 italic">
                        Sin categorías asignadas
                      </span>
                    )}
                  </div>
                </div>

                {/* Botón de Navegación Programática */}
                <button
                  type="button"
                  onClick={() => navigate(`/productos/${prod.id}`)}
                  aria-label={`Ver detalle de ${prod.nombre}`}
                  className="mt-4 text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 rounded self-end cursor-pointer"
                >
                  Ver detalle →
                </button>
              </article>
            ))}
          </div>
        </section>
      )}

      {/* Barra de navegación de páginas (Paginador) */}
      {!isLoading && !isError && total > 0 && (
        <nav
          aria-label="Paginación de productos"
          className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4"
        >
          <p className="text-sm text-slate-600" aria-live="polite">
            Página <span className="font-semibold text-slate-900">{page}</span> de{' '}
            <span className="font-semibold text-slate-900">{totalPages}</span>
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={page <= 1 || isLoading}
              onClick={handlePrevPage}
              aria-label="Ir a la página anterior"
              className="px-3.5 py-1.5 text-xs font-medium rounded-lg border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 cursor-pointer"
            >
              ← Anterior
            </button>
            <button
              type="button"
              disabled={page >= totalPages || isLoading}
              onClick={handleNextPage}
              aria-label="Ir a la página siguiente"
              className="px-3.5 py-1.5 text-xs font-medium rounded-lg border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 cursor-pointer"
            >
              Siguiente →
            </button>
          </div>
        </nav>
      )}
    </div>
  );
}

export default ProductsPage;
