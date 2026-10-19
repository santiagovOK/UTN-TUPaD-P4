// [Consigna TP7 - Catálogo Paginado y Detalle de Productos (HU-05, RN-02)]:
//   - Capa de servicios HTTP para la consulta del catálogo de productos y su detalle.
//   - Verificación obligatoria de respuestas HTTP con if (!res.ok) para asegurar el rechazo
//     de promesas ante respuestas fallidas y la activación de isError en TanStack Query.
//   - Parámetros de consulta estructurados con offset, limit, búsqueda por nombre, filtro de
//     disponibilidad y filtro por identificador de categoría asociada.
// [Diagrama UML - Entidad PRODUCTO y relación N:N con CATEGORIA (docs/UML_FOOD_STORE.svg)]:
//   - Consulta de productos con categorías anidadas mediante relación asociativa normalizada.

import { API_BASE_URL, handleResponse, handleVoidResponse } from "./api";
import type { Categoria, PaginatedResponse } from "../types/categoria";
import type { Ingrediente } from "../types/ingrediente";
import type {
  Producto,
  ProductoCreate,
  ProductoUpdate,
} from "../types/producto";

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
  categoria_id?: number,
  incluir_inactivos = false
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

  if (incluir_inactivos) {
    params.append("incluir_inactivos", "true");
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
 * Crea un nuevo producto con categorías asociadas y opcionalmente ingredientes.
 * [Consigna TP7 - RN-19, RN-20]: Requiere al menos una categoría válida.
 */
export async function createProducto(
  payload: ProductoCreate
): Promise<Producto> {
  const res = await fetch(`${PRODUCTOS_ENDPOINT}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    return handleResponse<Producto>(res, "No se pudo crear el producto");
  }
  return res.json() as Promise<Producto>;
}

/**
 * Actualiza un producto existente mediante PUT.
 * [Consigna TP7 - RN-12, RN-20, RN-21]: Reemplazo total de asociaciones en el backend.
 */
export async function updateProducto({
  id,
  data,
}: {
  id: number;
  data: ProductoUpdate;
}): Promise<Producto> {
  const res = await fetch(`${PRODUCTOS_ENDPOINT}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    return handleResponse<Producto>(res, "No se pudo actualizar el producto");
  }
  return res.json() as Promise<Producto>;
}

/**
 * Elimina un producto mediante baja lógica en el backend.
 * [Consigna TP7 - RN-10]: Responde HTTP 204 No Content.
 */
export async function deleteProducto(id: number): Promise<void> {
  const res = await fetch(`${PRODUCTOS_ENDPOINT}/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    return handleVoidResponse(res, "No se pudo eliminar el producto");
  }
}

/**
 * Obtiene las categorías asociadas a un producto específico.
 * [Consigna TP7]: Endpoint relacional inverso GET /productos/{id}/categorias.
 */
export async function getCategoriasByProducto(
  id: number
): Promise<Categoria[]> {
  const res = await fetch(`${PRODUCTOS_ENDPOINT}/${id}/categorias`);
  if (!res.ok) {
    return handleResponse<Categoria[]>(
      res,
      `Error al obtener las categorías del producto #${id}`
    );
  }
  return res.json() as Promise<Categoria[]>;
}

/**
 * Obtiene los ingredientes asociados a un producto específico.
 * [Consigna TP7]: Endpoint relacional inverso GET /productos/{id}/ingredientes.
 */
export async function getIngredientesByProducto(
  id: number
): Promise<Ingrediente[]> {
  const res = await fetch(`${PRODUCTOS_ENDPOINT}/${id}/ingredientes`);
  if (!res.ok) {
    return handleResponse<Ingrediente[]>(
      res,
      `Error al obtener los ingredientes del producto #${id}`
    );
  }
  return res.json() as Promise<Ingrediente[]>;
}

/**
 * Objeto agrupador para consumidores que prefieren importar el servicio completo como `productoService`.
 */
export const productoService = {
  getProductos,
  getProductoById,
  createProducto,
  updateProducto,
  deleteProducto,
  getCategoriasByProducto,
  getIngredientesByProducto,
};
