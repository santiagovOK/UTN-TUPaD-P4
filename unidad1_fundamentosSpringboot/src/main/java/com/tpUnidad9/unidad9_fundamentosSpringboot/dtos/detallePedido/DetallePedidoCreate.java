package com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.detallePedido;

public record DetallePedidoCreate(
        int cantidad,
        Long idProducto
) {
    // Al igual que con Producto, la entidad DetallePedido requiere una Entidad (Producto) real.
    // Por eso, en este DTO solo pasamos el idProducto y delegaremos la búsqueda del producto a la capa Service.
}
