package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.categoria;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Categoria;

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