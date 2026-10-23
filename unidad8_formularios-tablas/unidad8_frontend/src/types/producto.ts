// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [Tipado con TypeScript & Catálogo de Productos]:
//   - Definición de interfaces para datos del dominio de productos, props de componentes y payloads de API.
// [Diagrama UML - Entidad PRODUCTO y relación N:N con CATEGORIA (docs/UML_FOOD_STORE.svg)]:
//   - id          : INTEGER {PK, NN, AI} -> number
//   - nombre      : VARCHAR(150) {NN}    -> string
//   - descripcion : TEXT (opcional)      -> string | null
//   - precio_base : DECIMAL(10,2) {NN}   -> number
//   - imagenes_url: JSON / ARRAY         -> string[]
//   - disponible  : BOOLEAN {NN}         -> boolean
//   - categorias  : CATEGORIA[]          -> Categoria[] (asociación N:N normalizada)
//   - Campos de auditoría (created_at, updated_at, deleted_at) gestionados internamente por el backend.

import type { Categoria } from "./categoria";
import type { Ingrediente, IngredienteInput } from "./ingrediente";

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_base: number;
  imagenes_url: string[];
  disponible: boolean;
  categorias: Categoria[];
  ingredientes: Ingrediente[];
}

export interface ProductoCreate {
  nombre: string;
  descripcion?: string | null;
  precio_base: number;
  imagenes_url?: string[];
  disponible?: boolean;
  categoria_ids: number[];
  ingredientes?: IngredienteInput[];
}

export interface ProductoUpdate {
  nombre?: string;
  descripcion?: string | null;
  precio_base?: number;
  imagenes_url?: string[];
  disponible?: boolean;
  categoria_ids?: number[];
  ingredientes?: IngredienteInput[];
}
