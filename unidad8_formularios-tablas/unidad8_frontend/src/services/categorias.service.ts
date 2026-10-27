// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [CRUD de Categorías y Server State]:
//   - Capa de servicios HTTP para la gestión de categorías consumiendo la API REST de FastAPI.
//   - Verificación obligatoria de errores con if (!res.ok) para asegurar el rechazo de la promesa y activar la bandera isError de TanStack Query en useQuery y useMutation.
//   - Normalización de parámetros de consulta (offset, limit, search) y payloads tipados estrictamente.
// [Diagrama UML - Entidad CATEGORIA (docs/UML_FOOD_STORE.svg)]:
//   - Soporte para operaciones de catálogo: consulta paginada, detalle por id, creación, modificación parcial y baja.

import { API_BASE_URL, handleResponse, handleVoidResponse } from "./api";
import type {
  Categoria,
  CategoriaCreate,
  CategoriaUpdate,
  PaginatedResponse,
} from "../types/categoria";
import type { Producto } from "../types/producto";
export const CATEGORIAS_ENDPOINT = `${API_BASE_URL}/categorias`;

/**
 * Obtiene la lista paginada de categorías con filtro dinámico por nombre.
 * [HU-01 & RN-01]: Soporta paginación y búsqueda por nombre.
 */
export async function getCategorias(
  offset = 0,
  limit = 100,
  search?: string,
  incluir_inactivos = false
): Promise<PaginatedResponse<Categoria>> {
  const params = new URLSearchParams({
    offset: String(offset),
    limit: String(limit),
  });

  if (search && search.trim() !== "") {
    params.append("nombre", search.trim());
    params.append("search", search.trim());
  }

  if (incluir_inactivos) {
    params.append("incluir_inactivos", "true");
  }

  const res = await fetch(`${CATEGORIAS_ENDPOINT}/?${params.toString()}`);
  if (!res.ok) {
    return handleResponse<PaginatedResponse<Categoria>>(
      res,
      "Error al cargar el listado de categorías"
    );
  }
  return res.json() as Promise<PaginatedResponse<Categoria>>;
}

/**
 * Obtiene el detalle de una categoría activa por su identificador único.
 * Lanza un error amigable si el recurso no existe (HTTP 404).
 */
export async function getCategoriaById(id: number): Promise<Categoria> {
  const res = await fetch(`${CATEGORIAS_ENDPOINT}/${id}`);
  if (!res.ok) {
    return handleResponse<Categoria>(res, `Categoría #${id} no encontrada`);
  }
  return res.json() as Promise<Categoria>;
}

/**
 * Crea una nueva categoría en el sistema enviando el payload en formato JSON.
 * [HU-02]: Si el nombre ya existe, el backend emite HTTP 409 y se captura el detalle.
 */
export async function createCategoria(
  payload: CategoriaCreate
): Promise<Categoria> {
  const res = await fetch(`${CATEGORIAS_ENDPOINT}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    return handleResponse<Categoria>(res, "No se pudo crear la categoría");
  }
  return res.json() as Promise<Categoria>;
}

/**
 * Actualiza los datos de una categoría existente mediante PUT (reemplazo total).
 * [HU-03]: Al guardar se envía PUT /categorias/{id}, que responde 200 con la categoría actualizada.
 */
export async function updateCategoria({
  id,
  data,
}: {
  id: number;
  data: CategoriaUpdate;
}): Promise<Categoria> {
  const res = await fetch(`${CATEGORIAS_ENDPOINT}/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    return handleResponse<Categoria>(res, "No se pudo actualizar la categoría");
  }
  return res.json() as Promise<Categoria>;
}

/**
 * Elimina una categoría mediante baja lógica en el backend.
 * [HU-04]: Responde con HTTP 204 No Content en caso exitoso.
 */
export async function deleteCategoria(id: number): Promise<void> {
  const res = await fetch(`${CATEGORIAS_ENDPOINT}/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    return handleVoidResponse(res, "No se pudo eliminar la categoría");
  }
}

/**
 * Obtiene los productos asociados a una categoría específica.
 * [Catálogo heredado del TP7]: Endpoint relacional inverso GET /categorias/{id}/productos.
 */
export async function getProductosByCategoria(id: number): Promise<Producto[]> {
  const res = await fetch(`${CATEGORIAS_ENDPOINT}/${id}/productos`);
  if (!res.ok) {
    return handleResponse<Producto[]>(
      res,
      `Error al obtener los productos de la categoría #${id}`
    );
  }
  return res.json() as Promise<Producto[]>;
}

/**
 * Objeto agrupador para consumidores que prefieren importar el servicio completo como `categoriaService`.
 */
export const categoriaService = {
  getCategorias,
  getCategoriaById,
  createCategoria,
  updateCategoria,
  deleteCategoria,
  getProductosByCategoria,
};
