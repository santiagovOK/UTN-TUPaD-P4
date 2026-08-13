package com.tpUnidad2.unidad2_APIRestSpringBoot.service;

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.detallePedido.DetallePedidoCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoEdit;
import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Pedido;
import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Producto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.repository.PedidoRepository;
import com.tpUnidad2.unidad2_APIRestSpringBoot.repository.ProductoRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PedidoServiceImp implements PedidoService {

    private final PedidoRepository pedidoRepository;
    private final ProductoRepository productoRepository;

    public PedidoServiceImp(PedidoRepository pedidoRepository, ProductoRepository productoRepository) {
        this.pedidoRepository = pedidoRepository;
        this.productoRepository = productoRepository;
    }

    @Override
    public PedidoDto save(PedidoCreate pedidoCreate) {
        // Se crea la entidad Pedido desde el DTO
        Pedido pedido = pedidoCreate.toEntity();
        
        // La lógica de negocio para gestionar los detalles (DetallePedido) se maneja directamente desde aquí (PedidoService).
        // Recorremos la lista de detalles enviados, buscamos la entidad Producto real en la BD usando su ID, 
        // Utilizamos el método addDetallePedido de la entidad Pedido, el cual instancia un nuevo DetallePedido pasándole 'this' (el pedido) y manteniendo la relación bidireccional correctamente.
        if (pedidoCreate.detalles() != null) {
            for (DetallePedidoCreate detalleCreate : pedidoCreate.detalles()) {
                Producto producto = productoRepository.findById(detalleCreate.idProducto())
                        .orElseThrow(() -> new NullPointerException("No se encontró el producto con id: " + detalleCreate.idProducto()));
                pedido.addDetallePedido(detalleCreate.cantidad(), producto);
            }
        }
        
        pedido = pedidoRepository.save(pedido);
        return PedidoDto.toDto(pedido);
    }

    @Override
    public PedidoDto findById(Long id) {
        Pedido pedido = pedidoRepository.findById(id)
                .orElseThrow(() -> new NullPointerException("No se encontró el pedido con id: " + id));
        return PedidoDto.toDto(pedido);
    }

    @Override
    public List<PedidoDto> findAll() {
        List<Pedido> pedidos = pedidoRepository.findAll();
        return pedidos.stream().map(PedidoDto::toDto).toList();
    }

    @Override
    public PedidoDto update(PedidoEdit pedidoEdit, Long idPedido) {
        Pedido pedido = pedidoRepository.findById(idPedido)
                .orElseThrow(() -> new NullPointerException("No se encontró el pedido con id: " + idPedido));
        pedidoEdit.applyTo(pedido);
        pedido = pedidoRepository.save(pedido);
        return PedidoDto.toDto(pedido);
    }

    @Override
    public void deleteById(Long id) {
        Pedido pedido = pedidoRepository.findById(id)
                .orElseThrow(() -> new NullPointerException("No se encontró el pedido con id: " + id));
        pedido.setEliminado(true);
        pedidoRepository.save(pedido);
    }
}