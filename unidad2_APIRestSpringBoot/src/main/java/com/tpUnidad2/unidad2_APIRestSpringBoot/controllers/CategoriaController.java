package com.tpUnidad2.unidad2_APIRestSpringBoot.controllers;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.categoria.CategoriaCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.categoria.CategoriaDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.categoria.CategoriaEdit;
import com.tpUnidad2.unidad2_APIRestSpringBoot.service.CategoriaService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/categorias")
public class CategoriaController {

    private final CategoriaService categoriaService;

    // TP2 - Inclusión de los endpoints básicos

    public CategoriaController(CategoriaService categoriaService) {
        this.categoriaService = categoriaService;
    }

    @GetMapping
    public ResponseEntity<List<CategoriaDto>> findAll() {
        return ResponseEntity.ok(categoriaService.findAll());
    }

    // TP2 - Se usa `HttpStatus.` + retorno por legibilidad y porque es autoexplicativo del código que se está devolviendo.

    @PostMapping
    public ResponseEntity<CategoriaDto> save(@RequestBody CategoriaCreate categoriaCreate) {
        return ResponseEntity.status(HttpStatus.CREATED).body(categoriaService.save(categoriaCreate));
    }

    @PutMapping("/{id}")
    public ResponseEntity<CategoriaDto> update(@RequestBody CategoriaEdit categoriaEdit, @PathVariable Long id) {
        return ResponseEntity.ok(categoriaService.update(categoriaEdit, id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteById(@PathVariable Long id) {
        categoriaService.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}