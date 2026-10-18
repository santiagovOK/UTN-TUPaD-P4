// [Consigna TP7 - CRUD de Categorías y Server State (HU-01, HU-02, HU-03, RN-02)]:
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

export const CATEGORIAS_ENDPOINT = `${API_BASE_URL}/categorias`;

/**
 * Obtiene la lista paginada de categorías con filtro dinámico por nombre.
 * [Consigna TP7 - HU-01 & RN-02]: Soporta paginación (offset/limit) y búsqueda incremental.
 */
export async function getCategorias(
  offset = 0,
  limit = 50,
  search?: string
): Promise<PaginatedResponse<Categoria>> {
  const params = new URLSearchParams({
    offset: String(offset),
    limit: String(limit),
  });

  if (search && search.trim() !== "") {
    params.append("search", search.trim());
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
 * [Consigna TP7 - HU-02]: Si el nombre ya existe, el backend emite HTTP 409 y se captura el detalle.
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
 * Actualiza parcialmente los datos de una categoría existente mediante PATCH.
 * [Consigna TP7 - HU-03]: Modificación segura mediante exclude_unset en backend.
 */
export async function updateCategoria({
  id,
  data,
}: {
  id: number;
  data: CategoriaUpdate;
}): Promise<Categoria> {
  const res = await fetch(`${CATEGORIAS_ENDPOINT}/${id}`, {
    method: "PATCH",
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
 * [Consigna TP7 - HU-03]: Responde con HTTP 204 No Content en caso exitoso.
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
 * Objeto agrupador para consumidores que prefieren importar el servicio completo como `categoriaService`.
 */
export const categoriaService = {
  getCategorias,
  getCategoriaById,
  createCategoria,
  updateCategoria,
  deleteCategoria,
};
