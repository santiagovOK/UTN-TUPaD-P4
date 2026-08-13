package com.tpUnidad2.unidad2_APIRestSpringBoot.service;

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoEdit;

import java.util.List;

public interface PedidoService {
    public PedidoDto save(PedidoCreate pedidoCreate);
    public PedidoDto findById(Long id);
    public List<PedidoDto> findAll();
    public PedidoDto update(PedidoEdit pedidoEdit, Long idPedido);
    public void deleteById(Long id);
}
