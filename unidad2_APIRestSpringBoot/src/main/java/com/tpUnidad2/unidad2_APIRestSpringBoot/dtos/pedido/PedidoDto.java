package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido;

import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Pedido;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.Estado;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.FormaPago;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.detallePedido.DetallePedidoDto;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

public record PedidoDto(
        Long id,
        LocalDate fecha,
        Estado estado,
        Double total,
        FormaPago formaPago,
        List<DetallePedidoDto> detalles
) {
    public static PedidoDto toDto(Pedido pedido) {
        return new PedidoDto(
                pedido.getId(),
                pedido.getFecha(),
                pedido.getEstado(),
                pedido.getTotal(),
                pedido.getFormaPago(),
                pedido.getDetalles() != null
                        ? pedido.getDetalles().stream().map(DetallePedidoDto::toDto).collect(Collectors.toList())
                        : null
        );
    }
}
