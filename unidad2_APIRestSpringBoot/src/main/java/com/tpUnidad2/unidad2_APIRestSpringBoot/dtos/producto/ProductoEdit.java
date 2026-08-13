package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.producto;

import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Categoria;
import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Producto;

public record ProductoEdit(
        String nombre,
        Double precio,
        String descripcion,
        Integer stock, // cambio de int a Integer para usar null luego. No está explicado en el video
        String imagen,
        Boolean disponible, // cambio de boolean a Boolean para usar null luego.
        Long idCategoria
) {
    public void applyTo(Producto producto, Categoria categoria) {
        if  (this.nombre != null) {
            producto.setNombre(this.nombre);
        }
        if  (this.precio != null) {
            producto.setPrecio(this.precio);
        }
        if  (this.descripcion != null) {
            producto.setDescripcion(this.descripcion);
        }
        if  (this.stock != null) {
            producto.setStock(this.stock);
        }
        if  (this.imagen != null) {
            producto.setImagen(this.imagen);
        }
        if (this.disponible != null) {
            producto.setDisponible(this.disponible);
        }
        // Si el Service encontró y nos pasó una categoría válida, se la asignamos
        if (categoria != null) {
            producto.setCategoria(categoria);
        }
    }


}
