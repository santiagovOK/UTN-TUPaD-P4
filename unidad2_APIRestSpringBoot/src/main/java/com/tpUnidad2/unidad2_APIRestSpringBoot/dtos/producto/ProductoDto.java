package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.producto;

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.categoria.CategoriaDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Producto;

public record ProductoDto(
        Long id,
        String nombre,
        Double precio,
        String descripcion,
        int stock,
        String imagen,
        boolean disponible,
        CategoriaDto categoriaDto
) {

    public static ProductoDto toDto(Producto producto) {
        return new ProductoDto(
                producto.getId(),
                producto.getNombre(),
                producto.getPrecio(),
                producto.getDescripcion(),
                producto.getStock(),
                producto.getImagen(),
                producto.isDisponible(),
                producto.getCategoria() != null ? CategoriaDto.toDto(producto.getCategoria()) : null
        );
    }
}
