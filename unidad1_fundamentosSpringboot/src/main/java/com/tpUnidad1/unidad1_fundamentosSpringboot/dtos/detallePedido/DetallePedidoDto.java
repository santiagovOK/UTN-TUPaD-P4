package com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.detallePedido;

import com.tpUnidad1.unidad1_fundamentosSpringboot.entities.DetallePedido;

public record DetallePedidoDto(
        Long id,
        int cantidad,
        Double subtotal,
        String nombreProducto
) {
    public static DetallePedidoDto toDto(DetallePedido detalle) {
        return new DetallePedidoDto(
                detalle.getId(),
                detalle.getCantidad(),
                detalle.getSubtotal(),
                detalle.getProducto() != null ? detalle.getProducto().getNombre() : null
        );
    }
}
