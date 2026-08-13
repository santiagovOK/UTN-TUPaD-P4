package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.detallePedido;

import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.DetallePedido;

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
