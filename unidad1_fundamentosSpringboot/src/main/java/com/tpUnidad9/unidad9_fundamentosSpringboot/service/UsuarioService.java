package com.tpUnidad9.unidad9_fundamentosSpringboot.service;

import com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.usuario.UsuarioCreate;
import com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.usuario.UsuarioDto;
import com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.usuario.UsuarioEdit;

import java.util.List;

public interface UsuarioService {
    public UsuarioDto save(UsuarioCreate usuarioCreate);
    public UsuarioDto findById(Long id);
    public List<UsuarioDto> findAll();
    public UsuarioDto update(UsuarioEdit usuarioEdit, Long idUsuario);
    public void deleteById(Long id);
}
