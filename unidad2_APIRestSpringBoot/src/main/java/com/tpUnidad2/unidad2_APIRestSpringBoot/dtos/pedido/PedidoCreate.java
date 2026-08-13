package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido;

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.detallePedido.DetallePedidoCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Pedido;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.Estado;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.FormaPago;

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
