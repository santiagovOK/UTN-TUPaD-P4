// [Consigna TP7 - Detalle de Producto con Navegación y TanStack Query (HU-04, HU-05, RN-01, RN-02, RN-07)]:
//   - Extracción de parámetro :id mediante useParams y validación numérica estricta (entero positivo).
//   - Consulta declarativa con useQuery(['producto', numericId]) con activación condicional enabled: isValidId.
//   - Navegación programática de retorno hacia /productos mediante useNavigate.
//   - Cero copia a useState local (RN-02: Server State gestionado íntegramente por TanStack Query).
//   - Accesibilidad: Landmark <article> para ficha de producto, secciones semánticas (<section>), listas (<ul>/<li>),
//     etiquetado accesible con aria-labelledby/aria-label y estilos focus-visible en botones interactivos.
// [Diagrama UML - Clúster Catálogo de Productos (docs/UML_FOOD_STORE.svg)]:
//   - Presentación de ficha de producto con id, nombre, precio_base, disponible, descripcion, imagenes_url y categorías N:N.

import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getProductoById } from '../services/productos.service';
import type { Producto } from '../types/producto';

export function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const numericId = Number(id);
  const isValidId =
    Boolean(id) && !Number.isNaN(numericId) && Number.isInteger(numericId) && numericId > 0;

  const {
    data: producto,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<Producto>({
    queryKey: ['producto', numericId],
    queryFn: () => getProductoById(numericId),
    enabled: isValidId,
  });

  return (
    <div className="space-y-6">
      {/* Botón de retorno al catálogo */}
      <div>
        <button
          type="button"
          onClick={() => navigate('/productos')}
          aria-label="Volver al listado de productos"
          className="text-sm font-medium text-indigo-600 hover:text-indigo-800 hover:underline mb-2 inline-flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 rounded cursor-pointer"
        >
          ← Volver al listado de productos
        </button>
      </div>

      {/* Caso: Identificador inválido o ausente */}
      {!isValidId && (
        <div
          role="alert"
          aria-live="assertive"
          className="p-6 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 space-y-3"
        >
          <h2 className="font-semibold text-base">Identificador de producto inválido</h2>
          <p className="text-sm text-amber-800">
            El parámetro proporcionado en la ruta (
            <code className="font-mono bg-amber-100 px-1 py-0.5 rounded">{id ?? 'vacío'}</code>) no
            corresponde a un identificador numérico de producto válido.
          </p>
          <button
            type="button"
            onClick={() => navigate('/productos')}
            aria-label="Regresar al catálogo de productos"
            className="inline-flex items-center px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 cursor-pointer"
          >
            Regresar al catálogo
          </button>
        </div>
      )}

      {/* Estado de carga */}
      {isValidId && isLoading && (
        <div
          role="status"
          aria-live="polite"
          className="flex justify-center items-center py-20 text-slate-500 text-sm bg-white rounded-2xl border border-slate-200 shadow-xs"
        >
          <span>Cargando detalle del producto #{id}...</span>
        </div>
      )}

      {/* Estado de error */}
      {isValidId && isError && (
        <div
          role="alert"
          aria-live="assertive"
          className="p-8 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-center space-y-4"
        >
          <div>
            <h2 className="font-semibold text-base">Error al cargar el producto #{id}</h2>
            <p className="text-sm text-rose-600 mt-1">
              {(error as Error)?.message ||
                'No fue posible recuperar la información del producto solicitado.'}
            </p>
          </div>
          <div className="flex items-center justify-center gap-3">
            <button
              type="button"
              onClick={() => refetch()}
              className="inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500 cursor-pointer"
            >
              Reintentar
            </button>
            <button
              type="button"
              onClick={() => navigate('/productos')}
              aria-label="Ir al catálogo de productos"
              className="inline-flex items-center px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-500 cursor-pointer"
            >
              Ir al catálogo
            </button>
          </div>
        </div>
      )}

      {/* Ficha detallada del producto */}
      {isValidId && !isLoading && !isError && producto && (
        <article
          aria-labelledby="producto-titulo-detalle"
          className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-6"
        >
          {/* Cabecera */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-100 pb-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span
                  className="text-xs font-mono font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded"
                  aria-label={`Identificador primario de producto: ${producto.id}`}
                >
                  ID: #{producto.id}
                </span>
                {producto.disponible ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                    Disponible para venta
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
                    No disponible
                  </span>
                )}
              </div>
              <h1
                id="producto-titulo-detalle"
                className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900"
              >
                {producto.nombre}
              </h1>
            </div>

            <div className="sm:text-right">
              <div className="text-xs text-slate-500 font-medium">Precio base</div>
              <div
                className="text-2xl sm:text-3xl font-extrabold text-emerald-600"
                aria-label={`Precio base: $${Number(producto.precio_base).toFixed(2)}`}
              >
                ${Number(producto.precio_base).toFixed(2)}
              </div>
            </div>
          </div>

          {/* Descripción */}
          <section aria-labelledby="descripcion-seccion-titulo" className="space-y-2">
            <h2
              id="descripcion-seccion-titulo"
              className="text-sm font-semibold uppercase tracking-wider text-slate-500"
            >
              Descripción del producto
            </h2>
            <div className="text-slate-700 text-base leading-relaxed bg-slate-50 rounded-xl p-4 border border-slate-100">
              {producto.descripcion ? (
                <p>{producto.descripcion}</p>
              ) : (
                <p className="text-slate-400 italic">
                  Este producto no cuenta con una descripción detallada.
                </p>
              )}
            </div>
          </section>

          {/* Categorías asociadas */}
          <section aria-labelledby="categorias-seccion-titulo" className="space-y-3">
            <h2
              id="categorias-seccion-titulo"
              className="text-sm font-semibold uppercase tracking-wider text-slate-500"
            >
              Categorías asociadas
            </h2>
            {producto.categorias && producto.categorias.length > 0 ? (
              <ul
                aria-labelledby="categorias-seccion-titulo"
                className="grid grid-cols-1 sm:grid-cols-2 gap-3 list-none p-0 m-0"
              >
                {producto.categorias.map((cat) => (
                  <li
                    key={cat.id}
                    className="p-3.5 rounded-xl border border-indigo-100 bg-indigo-50/50 flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-sm text-indigo-950">{cat.nombre}</span>
                        <span
                          className="text-[10px] font-mono text-indigo-500 bg-indigo-100 px-1.5 py-0.5 rounded"
                          aria-label={`Identificador de categoría: ${cat.id}`}
                        >
                          Cat #{cat.id}
                        </span>
                      </div>
                      {cat.descripcion && (
                        <p className="text-xs text-slate-600 mt-1 line-clamp-2">
                          {cat.descripcion}
                        </p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-400 italic bg-slate-50 rounded-xl p-4 border border-slate-100">
                Sin categorías asignadas en el catálogo.
              </p>
            )}
          </section>

          {/* Galería de imágenes (si existen URLs) */}
          {producto.imagenes_url && producto.imagenes_url.length > 0 && (
            <section
              aria-labelledby="galeria-seccion-titulo"
              className="space-y-3 pt-2 border-t border-slate-100"
            >
              <h2
                id="galeria-seccion-titulo"
                className="text-sm font-semibold uppercase tracking-wider text-slate-500"
              >
                Galería de imágenes
              </h2>
              <ul
                aria-labelledby="galeria-seccion-titulo"
                className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 list-none p-0 m-0"
              >
                {producto.imagenes_url.map((url, idx) => (
                  <li
                    key={`${url}-${idx}`}
                    className="aspect-square rounded-xl overflow-hidden bg-slate-100 border border-slate-200"
                  >
                    <img
                      src={url}
                      alt={`${producto.nombre} - imagen de muestra ${idx + 1}`}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  </li>
                ))}
              </ul>
            </section>
          )}
        </article>
      )}
    </div>
  );
}

export default ProductDetailPage;
