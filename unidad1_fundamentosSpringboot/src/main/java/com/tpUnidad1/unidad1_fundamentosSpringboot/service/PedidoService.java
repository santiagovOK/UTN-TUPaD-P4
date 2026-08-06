package com.tpUnidad1.unidad1_fundamentosSpringboot.service;

import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.pedido.PedidoCreate;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.pedido.PedidoDto;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.pedido.PedidoEdit;

import java.util.List;

public interface PedidoService {
    public PedidoDto save(PedidoCreate pedidoCreate);
    public PedidoDto findById(Long id);
    public List<PedidoDto> findAll();
    public PedidoDto update(PedidoEdit pedidoEdit, Long idPedido);
    public void deleteById(Long id);
}
