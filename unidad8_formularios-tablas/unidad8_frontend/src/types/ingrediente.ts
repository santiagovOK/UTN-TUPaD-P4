// [Extensión de catálogo heredada del TP7 - Tipado con TypeScript]:
//   - Interfaces para UnidadMedida (catálogo inmutable seed), Ingrediente y relación ProductoIngrediente.
//   - Extensión heredada del TP7: no forma parte del clúster Catálogo del SVG original.
//   - UnidadMedida: id, nombre, simbolo, tipo.
//   - Ingrediente: id, nombre, descripcion, unidad_medida_id, activo.
//   - ProductoIngredienteInput: ingrediente_id, cantidad (> 0), es_opcional.

export interface UnidadMedida {
  id: number;
  nombre: string;
  simbolo: string;
  tipo: string;
}

export interface UnidadMedidaListResponse {
  total: number;
  items: UnidadMedida[];
}

export interface Ingrediente {
  id: number;
  nombre: string;
  descripcion?: string;
  unidad_medida_id: number;
  activo: boolean;
}

export interface IngredienteCreate {
  nombre: string;
  descripcion?: string;
  unidad_medida_id: number;
  activo?: boolean;
}

export interface IngredienteUpdate {
  nombre?: string;
  descripcion?: string;
  unidad_medida_id?: number;
  activo?: boolean;
}

export interface ProductoIngredienteInput {
  ingrediente_id: number;
  cantidad?: number;
  es_opcional?: boolean;
}

export type IngredienteInput = number | ProductoIngredienteInput;
