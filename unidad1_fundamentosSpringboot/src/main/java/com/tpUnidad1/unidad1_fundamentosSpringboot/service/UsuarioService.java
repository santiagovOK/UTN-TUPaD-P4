package com.tpUnidad1.unidad1_fundamentosSpringboot.service;

import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.usuario.UsuarioCreate;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.usuario.UsuarioDto;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.usuario.UsuarioEdit;

import java.util.List;

public interface UsuarioService {
    public UsuarioDto save(UsuarioCreate usuarioCreate);
    public UsuarioDto findById(Long id);
    public List<UsuarioDto> findAll();
    public UsuarioDto update(UsuarioEdit usuarioEdit, Long idUsuario);
    public void deleteById(Long id);
}
