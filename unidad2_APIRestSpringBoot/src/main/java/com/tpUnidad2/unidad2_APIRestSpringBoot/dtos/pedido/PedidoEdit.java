package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido;

import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Pedido;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.Estado;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.FormaPago;

public record PedidoEdit(
        Estado estado,
        FormaPago formaPago
) {
    public void applyTo(Pedido pedido) {
        if (this.estado != null) {
            pedido.setEstado(this.estado);
        }
        if (this.formaPago != null) {
            pedido.setFormaPago(this.formaPago);
        }
    }
}
