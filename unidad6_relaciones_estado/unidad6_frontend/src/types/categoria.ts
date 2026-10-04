// [Consigna TP6 - Parte B, inciso c]: Definir la interfaz Categoria (id, nombre, descripcion, activo)
/**
 * Interface que representa la entidad Categoria en el frontend.
 *
 * Mapea el contrato de datos expuesto por el backend (FastAPI / Pydantic).
 */
export interface Categoria {
  id: number;
  nombre: string;
  descripcion?: string;
  activo?: boolean;
}
