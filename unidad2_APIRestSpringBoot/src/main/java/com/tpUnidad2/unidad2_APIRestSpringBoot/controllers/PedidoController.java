package com.tpUnidad2.unidad2_APIRestSpringBoot.controllers;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.pedido.PedidoEdit;
import com.tpUnidad2.unidad2_APIRestSpringBoot.service.PedidoService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/pedidos")
public class PedidoController {

    private final PedidoService pedidoService;

    // TP2 - Inclusión de los endpoints básicos

    public PedidoController(PedidoService pedidoService) {
        this.pedidoService = pedidoService;
    }

    @GetMapping
    public ResponseEntity<List<PedidoDto>> findAll() {
        return ResponseEntity.ok(pedidoService.findAll());
    }

    @PostMapping
    public ResponseEntity<PedidoDto> save(@Valid @RequestBody PedidoCreate pedidoCreate) {
        return ResponseEntity.status(HttpStatus.CREATED).body(pedidoService.save(pedidoCreate));
    }

    @PutMapping("/{id}")
    public ResponseEntity<PedidoDto> update(@Valid @RequestBody PedidoEdit pedidoEdit, @PathVariable Long id) {
        return ResponseEntity.ok(pedidoService.update(pedidoEdit, id));
    }


    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteById(@PathVariable Long id) {
        pedidoService.deleteById(id);
        return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
    }
}