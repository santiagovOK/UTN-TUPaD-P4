package com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.pedido;

import com.tpUnidad1.unidad1_fundamentosSpringboot.entities.Pedido;
import com.tpUnidad1.unidad1_fundamentosSpringboot.enums.Estado;
import com.tpUnidad1.unidad1_fundamentosSpringboot.enums.FormaPago;

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
