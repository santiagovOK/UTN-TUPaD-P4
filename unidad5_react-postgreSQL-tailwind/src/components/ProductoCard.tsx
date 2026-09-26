import type { Producto } from '../types/producto';

export interface ProductoCardProps {
  producto: Producto;
}

export function ProductoCard({ producto }: ProductoCardProps) {
  const { nombre, descripcion, precio, categoria, stock, activo } = producto;

  const precioFormateado = new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2,
  }).format(precio);

  return (
    <article className="w-full bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-5 hover:shadow-md transition-shadow flex flex-col justify-between">
      <div>
        <header className="flex justify-between items-start mb-2">
          {categoria ? (
            <span className="inline-block bg-blue-50 text-blue-700 text-xs px-2.5 py-1 rounded-full font-semibold uppercase tracking-wide">
              {categoria}
            </span>
          ) : (
            <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2.5 py-1 rounded-full font-semibold uppercase tracking-wide">
              General
            </span>
          )}
          {activo !== undefined && (
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                activo ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
              }`}
            >
              {activo ? 'Activo' : 'Inactivo'}
            </span>
          )}
        </header>

        <h3 className="text-lg font-bold text-gray-900 mb-1 leading-snug">{nombre}</h3>

        {descripcion && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">{descripcion}</p>
        )}
      </div>

      <footer className="pt-4 border-t border-gray-100 flex items-center justify-between mt-auto">
        <div>
          <span className="text-xs text-gray-600 block font-medium">Precio</span>
          <data value={precio} className="text-xl font-extrabold text-indigo-600">
            {precioFormateado}
          </data>
        </div>
        {stock !== undefined && (
          <div className="text-right">
            <span className="text-xs text-gray-600 block font-medium">Stock</span>
            <span
              className={`text-sm font-semibold ${
                stock > 0 ? 'text-gray-700' : 'text-red-500'
              }`}
            >
              {stock} u.
            </span>
          </div>
        )}
      </footer>
    </article>
  );
}

export default ProductoCard;
