// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [Tipado con TypeScript & Catálogo de Categorías]:
//   - Definición de interfaces para datos del dominio, props de componentes y respuestas de la API.
//   - Contrato consumido por modales, tablas, servicios HTTP y páginas del catálogo.
// [Diagrama UML - Entidad CATEGORIA (docs/UML_FOOD_STORE.svg)]:
//   - id          : INTEGER {PK, NN, AI}        -> number
//   - nombre      : VARCHAR(100) {UNIQUE, NN}   -> string
//   - descripcion : TEXT (opcional / Decisión A)-> string | undefined
//   - Campos de auditoría (created_at, updated_at, deleted_at) gestionados internamente por el backend.

export interface Categoria {
  id: number;
  nombre: string;
  descripcion?: string;
}

export interface CategoriaCreate {
  nombre: string;
  descripcion?: string;
}

export interface CategoriaUpdate {
  nombre?: string;
  descripcion?: string;
}

// [Paginación y Respuestas Estructuradas]:
// Contrato genérico para endpoints de colección que retornan { total, items }.
export interface PaginatedResponse<T> {
  total: number;
  items: T[];
}
