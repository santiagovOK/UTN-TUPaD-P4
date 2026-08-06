package com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.categoria;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad1.unidad1_fundamentosSpringboot.entities.Categoria;

public record CategoriaEdit(
        String nombre,
        String descripcion
) {
    public void applyTo(Categoria categoria) {
        if (this.nombre != null) {
            categoria.setNombre(this.nombre);
        }
        if (this.descripcion != null) {
            categoria.setDescripcion(this.descripcion);
        }
    }
}