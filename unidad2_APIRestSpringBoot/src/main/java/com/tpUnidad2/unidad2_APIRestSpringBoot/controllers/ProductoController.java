package com.tpUnidad2.unidad2_APIRestSpringBoot.controllers;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.producto.ProductoCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.producto.ProductoDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.producto.ProductoEdit;
import com.tpUnidad2.unidad2_APIRestSpringBoot.service.ProductoService;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/productos")
public class ProductoController {

    private final ProductoService productoService;

    // TP2 - Inclusión de los endpoints básicos

    public ProductoController(ProductoService productoService) {
        this.productoService = productoService;
    }

    @GetMapping
    public ResponseEntity<List<ProductoDto>> findAll() {
        return ResponseEntity.ok(productoService.findAll());
    }

    @PostMapping
    public ResponseEntity<ProductoDto> save(@RequestBody ProductoCreate productoCreate) {
        return ResponseEntity.status(HttpStatus.CREATED).body(productoService.save(productoCreate));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProductoDto> update(@RequestBody ProductoEdit productoEdit, @PathVariable Long id) {
        return ResponseEntity.ok(productoService.update(productoEdit, id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteById(@PathVariable Long id) {
        productoService.deleteById(id);
        return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
    }
}