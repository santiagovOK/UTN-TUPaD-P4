package com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.pedido;

import com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.detallePedido.DetallePedidoCreate;
import com.tpUnidad9.unidad9_fundamentosSpringboot.entities.Pedido;
import com.tpUnidad9.unidad9_fundamentosSpringboot.enums.Estado;
import com.tpUnidad9.unidad9_fundamentosSpringboot.enums.FormaPago;

import java.time.LocalDate;
import java.util.List;

public record PedidoCreate(
        Estado estado,
        FormaPago formaPago,
        List<DetallePedidoCreate> detalles
) {
    public Pedido toEntity() {
        return Pedido.builder()
                .fecha(LocalDate.now())
                .estado(this.estado != null ? this.estado : Estado.PENDIENTE)
                .formaPago(this.formaPago)
                .build();
    }
}
