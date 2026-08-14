package com.tpUnidad2.unidad2_APIRestSpringBoot.controllers;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario.UsuarioCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario.UsuarioDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario.UsuarioEdit;
import com.tpUnidad2.unidad2_APIRestSpringBoot.service.UsuarioService;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/usuarios")
public class UsuarioController {

    private final UsuarioService usuarioService;

    // TP2 - Inclusión de los endpoints básicos

    public UsuarioController(UsuarioService usuarioService) {
        this.usuarioService = usuarioService;
    }

    // TP2 - Inyección directa de `@PageableDefault(size = 10) Pageable pageable` para devolver solo una cantidad determinada de usuarios cuando se busca con `findAll`.  Podría también valer para otras entidades

    @GetMapping
    public ResponseEntity<Page<UsuarioDto>> findAll(@PageableDefault(size = 15) Pageable pageable) {
        return ResponseEntity.ok(usuarioService.findAll(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<UsuarioDto> findById(@PathVariable Long id) {
        UsuarioDto usuario = usuarioService.findById(id);
        System.out.println("Usuario encontrado con id: " + id);
        return ResponseEntity.ok(usuario);
    }

    @GetMapping("/search")
    public ResponseEntity<UsuarioDto> findByMail(@RequestParam("mail") String mail) {
        UsuarioDto usuario = usuarioService.findByMail(mail);
        System.out.println("Usuario encontrado con mail: " + mail);
        return ResponseEntity.ok(usuario);
    }

    @PostMapping
    public ResponseEntity<UsuarioDto> save(@Valid @RequestBody UsuarioCreate usuarioCreate) {
        return ResponseEntity.status(HttpStatus.CREATED).body(usuarioService.save(usuarioCreate));
    }

    @PutMapping("/{id}")
    public ResponseEntity<UsuarioDto> update(@Valid @RequestBody UsuarioEdit usuarioEdit, @PathVariable Long id) {
        return ResponseEntity.ok(usuarioService.update(usuarioEdit, id));
    }


    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteById(@PathVariable Long id) {
        usuarioService.deleteById(id);
        return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
    }
}