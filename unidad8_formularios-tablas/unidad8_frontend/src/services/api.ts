// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [Capa de Servicios HTTP y Gestión de Errores]:
//   - Cliente base con configuración centralizada de URL de la API mediante import.meta.env.VITE_API_URL.
//   - Verificación estricta de respuestas HTTP (control if (!res.ok) throw new Error(...)) para
//     permitir la activación automática de isError / error en TanStack Query (useQuery / useMutation).
//   - Extracción de mensajes de error desde el cuerpo JSON de FastAPI (detail como string o
//     arreglo de validación de Pydantic), con fallback formateado ante códigos HTTP de error.
// [Diagrama UML - Comunicación REST con el Catálogo (docs/UML_FOOD_STORE.svg)]:
//   - Base URL para el acceso a las entidades CATEGORIA y PRODUCTO del backend Food Store.

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/+$/, "") ||
  "http://localhost:8000";

/**
 * Extrae de forma segura el mensaje de error emitido por FastAPI en el campo `detail`.
 * Soporta tanto strings directos de excepciones HTTP como arreglos de errores de validación de Pydantic.
 */
export async function extractErrorMessage(
  res: Response,
  fallbackMessage: string
): Promise<string> {
  try {
    const data = (await res.json()) as { detail?: unknown };
    if (typeof data?.detail === "string" && data.detail.trim() !== "") {
      return data.detail;
    }
    if (Array.isArray(data?.detail) && data.detail.length > 0) {
      const messages = (data.detail as Array<{ msg?: string }>)
        .map((err) => err.msg)
        .filter((msg): msg is string => Boolean(msg));
      if (messages.length > 0) {
        return messages.join("; ");
      }
    }
  } catch {
    // Si la respuesta no contiene un JSON válido, recurrimos al fallback con status
  }
  return `${fallbackMessage} (HTTP ${res.status})`;
}

/**
 * Procesa la respuesta HTTP asegurando la verificación obligatoria de `!res.ok`.
 * Lanza una excepción `Error` con el detalle extraído o retorna el payload deserializado.
 */
export async function handleResponse<T>(
  res: Response,
  fallbackMessage: string
): Promise<T> {
  if (!res.ok) {
    const message = await extractErrorMessage(res, fallbackMessage);
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

/**
 * Manejador especializado para endpoints que retornan `204 No Content` o sin cuerpo.
 * Lanza una excepción `Error` si `!res.ok`.
 */
export async function handleVoidResponse(
  res: Response,
  fallbackMessage: string
): Promise<void> {
  if (!res.ok) {
    const message = await extractErrorMessage(res, fallbackMessage);
    throw new Error(message);
  }
}
