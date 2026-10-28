// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [CRUD de Ingredientes y Catálogo de Unidades de Medida - Server State]:
//   - Capa de servicios HTTP para la gestión de ingredientes y consulta de unidades de medida
//     consumiendo la API REST de FastAPI.
//   - Verificación obligatoria de errores con if (!res.ok) para asegurar el rechazo de la promesa
//     y activar la bandera isError de TanStack Query en useQuery y useMutation.
//   - Normalización de parámetros de consulta (offset, limit, search/nombre, incluir_inactivos)
//     y payloads tipados estrictamente.
// [Extensión heredada del TP7 - Entidades INGREDIENTE y UNIDAD_MEDIDA]:
//   - Soporte para operaciones de catálogo: consulta paginada, detalle por id, creación,
//     modificación completa y baja lógica de ingredientes, junto a la lectura del catálogo
//     inmutable de unidades de medida.

import { API_BASE_URL, handleResponse, handleVoidResponse } from "./api";
import type { PaginatedResponse } from "../types/categoria";
import type {
  Ingrediente,
  IngredienteCreate,
  IngredienteUpdate,
  UnidadMedida,
  UnidadMedidaListResponse,
} from "../types/ingrediente";

export const INGREDIENTES_ENDPOINT = `${API_BASE_URL}/ingredientes`;
export const UNIDADES_MEDIDA_ENDPOINT = `${API_BASE_URL}/unidades-medida`;

/**
 * Obtiene la lista paginada de ingredientes con filtro dinámico por nombre.
 * [HU-05 & RN-01]: Soporta paginación (offset, limit) y búsqueda por nombre/search.
 */
export async function getIngredientes(
  offset = 0,
  limit = 100,
  search?: string,
  incluir_inactivos = false
): Promise<PaginatedResponse<Ingrediente>> {
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

  const res = await fetch(`${INGREDIENTES_ENDPOINT}/?${params.toString()}`);
  if (!res.ok) {
    return handleResponse<PaginatedResponse<Ingrediente>>(
      res,
      "Error al cargar el listado de ingredientes"
    );
  }
  return res.json() as Promise<PaginatedResponse<Ingrediente>>;
}

/**
 * Obtiene el detalle de un ingrediente activo por su identificador único.
 * Lanza un error amigable si el recurso no existe (HTTP 404).
 */
export async function getIngredienteById(id: number): Promise<Ingrediente> {
  const res = await fetch(`${INGREDIENTES_ENDPOINT}/${id}`);
  if (!res.ok) {
    return handleResponse<Ingrediente>(res, `Ingrediente #${id} no encontrado`);
  }
  return res.json() as Promise<Ingrediente>;
}

/**
 * Crea un nuevo ingrediente en el sistema enviando el payload en formato JSON.
 * [HU-05]: Si el nombre ya existe (409) o la unidad no existe (404), se captura el detalle emitido por FastAPI.
 */
export async function createIngrediente(
  payload: IngredienteCreate
): Promise<Ingrediente> {
  const res = await fetch(`${INGREDIENTES_ENDPOINT}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    return handleResponse<Ingrediente>(res, "No se pudo crear el ingrediente");
  }
  return res.json() as Promise<Ingrediente>;
}

/**
 * Actualiza los datos de un ingrediente existente mediante PUT.
 * [HU-05]: Al guardar se envía PUT /ingredientes/{id}, que responde 200 con el ingrediente actualizado.
 */
export async function updateIngrediente({
  id,
  data,
}: {
  id: number;
  data: IngredienteUpdate;
}): Promise<Ingrediente> {
  const res = await fetch(`${INGREDIENTES_ENDPOINT}/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    return handleResponse<Ingrediente>(
      res,
      "No se pudo actualizar el ingrediente"
    );
  }
  return res.json() as Promise<Ingrediente>;
}

/**
 * Elimina un ingrediente mediante baja lógica en el backend.
 * [HU-05]: Responde con HTTP 204 No Content en caso exitoso; HTTP 409 si tiene productos asociados.
 */
export async function deleteIngrediente(id: number): Promise<void> {
  const res = await fetch(`${INGREDIENTES_ENDPOINT}/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    return handleVoidResponse(res, "No se pudo eliminar el ingrediente");
  }
}

/**
 * Obtiene el catálogo completo de unidades de medida predefinidas en el sistema.
 * [Catálogo inmutable]: Retorna { total, items } con las unidades de medida seed.
 */
export async function getUnidadesMedida(): Promise<UnidadMedidaListResponse> {
  const res = await fetch(`${UNIDADES_MEDIDA_ENDPOINT}/`);
  if (!res.ok) {
    return handleResponse<UnidadMedidaListResponse>(
      res,
      "Error al cargar el catálogo de unidades de medida"
    );
  }
  return res.json() as Promise<UnidadMedidaListResponse>;
}

/**
 * Obtiene los detalles de una unidad de medida por su identificador único.
 * Lanza un error amigable si el recurso no existe (HTTP 404).
 */
export async function getUnidadMedidaById(id: number): Promise<UnidadMedida> {
  const res = await fetch(`${UNIDADES_MEDIDA_ENDPOINT}/${id}`);
  if (!res.ok) {
    return handleResponse<UnidadMedida>(
      res,
      `Unidad de medida #${id} no encontrada`
    );
  }
  return res.json() as Promise<UnidadMedida>;
}

/**
 * Objeto agrupador para consumidores que prefieren importar el servicio completo como `ingredienteService`.
 */
export const ingredienteService = {
  getIngredientes,
  getIngredienteById,
  createIngrediente,
  updateIngrediente,
  deleteIngrediente,
  getUnidadesMedida,
  getUnidadMedidaById,
};
