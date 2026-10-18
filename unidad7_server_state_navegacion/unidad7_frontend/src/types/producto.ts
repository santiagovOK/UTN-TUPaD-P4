// [Consigna TP7 - Tipado con TypeScript]:
//   - Definición de interfaces para los datos del dominio de productos, props de componentes y payloads de API.
// [Diagrama UML - Entidad PRODUCTO y relación N:N con CATEGORIA (docs/UML_FOOD_STORE.svg)]:
//   - id          : INTEGER {PK, NN, AI} -> number
//   - nombre      : VARCHAR(150) {NN}    -> string
//   - descripcion : TEXT (opcional)      -> string | null
//   - precio_base : DECIMAL(10,2) {NN}   -> number
//   - imagenes_url: JSON / ARRAY         -> string[]
//   - disponible  : BOOLEAN {NN}         -> boolean
//   - categorias  : CATEGORIA[]          -> Categoria[] (asociación N:N normalizada)
//   - Campos de auditoría (created_at, updated_at, deleted_at) gestionados internamente por el backend.

import { Categoria } from "./categoria";

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_base: number;
  imagenes_url?: string[];
  disponible: boolean;
  categorias: Categoria[];
}

export interface ProductoCreate {
  nombre: string;
  descripcion?: string | null;
  precio_base: number;
  imagenes_url?: string[];
  disponible?: boolean;
}

export interface ProductoUpdate {
  nombre?: string;
  descripcion?: string | null;
  precio_base?: number;
  imagenes_url?: string[];
  disponible?: boolean;
}

// [Consigna TP7 - Asignación de categorías en relación N:N]:
// [Diagrama UML - PRODUCTO_CATEGORIA con clave compuesta y flag es_principal]:
export interface ProductoCategoriaAssign {
  producto_id: number;
  categoria_id: number;
  es_principal?: boolean;
}
