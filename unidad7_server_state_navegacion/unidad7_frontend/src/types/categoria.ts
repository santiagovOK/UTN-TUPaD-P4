// [Consigna TP7 - Tipado con TypeScript & CRUD de Categorías]:
//   - "Definición de interfaces para los datos del dominio, props de componentes y respuestas de la API."
//   - Contrato hoja (estrategia Bottom-Up) consumido por CategoriaCard, CategoriaList, CategoriaModal,
//     servicios HTTP y páginas del catálogo.
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

// [Consigna TP7 - Paginación y Respuestas Estructuradas]:
// Contrato genérico para endpoints de colección que retornan { total, items }.
export interface PaginatedResponse<T> {
  total: number;
  items: T[];
}
