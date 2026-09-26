/**
 * Interface que representa la entidad Producto en el frontend.
 *
 * Mapea literalmente el contrato de datos expuesto por el backend en el schema ProductoResponse (FastAPI / SQLModel).
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
