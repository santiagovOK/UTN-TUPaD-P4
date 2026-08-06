package com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.categoria;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad1.unidad1_fundamentosSpringboot.entities.Categoria;

public record CategoriaDto(
        Long id,
        String nombre,
        String descripcion
) {
    // con toDto() se está haciendo referencia a la entidad Categoria, que usa Lombok.
    public static CategoriaDto toDto(Categoria categoria) {
        return new CategoriaDto(
                categoria.getId(),
                categoria.getNombre(),
                categoria.getDescripcion()
        );
    }
}