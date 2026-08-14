package com.tpUnidad2.unidad2_APIRestSpringBoot.service;

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario.UsuarioCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario.UsuarioDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario.UsuarioEdit;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface UsuarioService {
    public UsuarioDto save(UsuarioCreate usuarioCreate);
    public UsuarioDto findById(Long id);
    public UsuarioDto findByMail(String mail);
    public Page<UsuarioDto> findAll(Pageable pageable);
    public UsuarioDto update(UsuarioEdit usuarioEdit, Long idUsuario);
    public void deleteById(Long id);
}

// TP2 - Se cambió el método findALL para que devuelva páginas (`Page<UsuarioDto>`) recibiendo un objeto `Pageable`. Si bien en este ejercicio hay un listado corto de usuarios, esta es una práctica correcta en caso de querer listar usuarios masivamente pero evitando el riesgo de cargar una gran cantidad de usuarios en BD grandes.  Podría también valer para otras entidades