/**
 * Interface que representa la entidad Producto en el frontend.
 *
 * Mapea el contrato de datos expuesto por el backend (FastAPI / SQLModel).
 * Requisito estricto de tipado estático según consignas y rúbrica de evaluación.
 */
export interface Producto {
  id: number;
  nombre: string;
  descripcion?: string;
  precio: number;
  categoria?: string;
  stock?: number;
  stock_minimo?: number;
  activo?: boolean;
}
