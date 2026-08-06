package com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.producto;

import com.tpUnidad9.unidad9_fundamentosSpringboot.entities.Producto;

public record ProductoCreate(
        String nombre,
        Double precio,
        String descripcion,
        int stock,
        String imagen,
        boolean disponible,
        Long idCategoria
) {
    public Producto toEntity() {
        return Producto.builder()
                .nombre(this.nombre)
                .precio(this.precio)
                .descripcion(this.descripcion)
                .stock(this.stock)
                .imagen(this.imagen)
                .disponible(this.disponible)
                // La categoría se asignará en el servicio, ya que necesitamos cargar la entidad completa de la categoría a partir del idCategoria
                .build();
    }
}
