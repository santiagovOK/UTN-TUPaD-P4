// [Consigna TP7 - Catálogo Paginado y Detalle de Productos (HU-05, RN-02)]:
//   - Capa de servicios HTTP para la consulta del catálogo de productos y su detalle.
//   - Verificación obligatoria de respuestas HTTP con if (!res.ok) para asegurar el rechazo
//     de promesas ante respuestas fallidas y la activación de isError en TanStack Query.
//   - Parámetros de consulta estructurados con offset, limit, búsqueda por nombre, filtro de
//     disponibilidad y filtro por identificador de categoría asociada.
// [Diagrama UML - Entidad PRODUCTO y relación N:N con CATEGORIA (docs/UML_FOOD_STORE.svg)]:
//   - Consulta de productos con categorías anidadas mediante relación asociativa normalizada.

import { API_BASE_URL, handleResponse } from "./api";
import type { PaginatedResponse } from "../types/categoria";
import type { Producto } from "../types/producto";

export const PRODUCTOS_ENDPOINT = `${API_BASE_URL}/productos`;

/**
 * Obtiene el catálogo paginado de productos aplicando filtros opcionales de nombre, disponibilidad y categoría.
 * [Consigna TP7 - HU-05 & RN-02]: Paginación con límite por defecto de 6 ítems para la grilla del catálogo.
 */
export async function getProductos(
  offset = 0,
  limit = 6,
  nombre?: string,
  disponible?: boolean,
  categoria_id?: number
): Promise<PaginatedResponse<Producto>> {
  const params = new URLSearchParams({
    offset: String(offset),
    limit: String(limit),
  });

  if (nombre && nombre.trim() !== "") {
    params.append("nombre", nombre.trim());
  }

  if (disponible !== undefined) {
    params.append("disponible", String(disponible));
  }

  if (categoria_id !== undefined && categoria_id > 0) {
    params.append("categoria_id", String(categoria_id));
  }

  const res = await fetch(`${PRODUCTOS_ENDPOINT}/?${params.toString()}`);
  if (!res.ok) {
    return handleResponse<PaginatedResponse<Producto>>(
      res,
      "Error al cargar el catálogo de productos"
    );
  }
  return res.json() as Promise<PaginatedResponse<Producto>>;
}

/**
 * Obtiene el detalle de un producto específico por su identificador primario.
 * [Diagrama UML - Detalle de PRODUCTO]: Incluye arreglo de categorías asociadas.
 */
export async function getProductoById(id: number): Promise<Producto> {
  const res = await fetch(`${PRODUCTOS_ENDPOINT}/${id}`);
  if (!res.ok) {
    return handleResponse<Producto>(res, `Producto #${id} no encontrado`);
  }
  return res.json() as Promise<Producto>;
}

/**
 * Objeto agrupador para consumidores que prefieren importar el servicio completo como `productoService`.
 */
export const productoService = {
  getProductos,
  getProductoById,
};
