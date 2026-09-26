import type { Producto } from '../types/producto';
import { ProductoCard } from './ProductoCard';

export interface ProductoListProps {
  productos: Producto[];
}

export function ProductoList({ productos }: ProductoListProps) {
  if (productos.length === 0) {
    return (
      <section
        aria-label="Catálogo de productos"
        className="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300"
      >
        <p role="status" aria-live="polite" className="text-gray-500 text-base">
          No hay productos disponibles para mostrar.
        </p>
      </section>
    );
  }

  return (
    <section aria-label="Catálogo de productos">
      <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 list-none p-0 m-0">
        {productos.map((producto) => (
          <li key={producto.id} className="flex">
            <ProductoCard producto={producto} />
          </li>
        ))}
      </ul>
    </section>
  );
}

export default ProductoList;
