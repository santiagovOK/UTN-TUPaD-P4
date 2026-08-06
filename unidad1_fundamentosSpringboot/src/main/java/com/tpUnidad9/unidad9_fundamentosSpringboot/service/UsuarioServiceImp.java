package com.tpUnidad9.unidad9_fundamentosSpringboot.service;

import com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.usuario.UsuarioCreate;
import com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.usuario.UsuarioDto;
import com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.usuario.UsuarioEdit;
import com.tpUnidad9.unidad9_fundamentosSpringboot.entities.Usuario;
import com.tpUnidad9.unidad9_fundamentosSpringboot.repository.UsuarioRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UsuarioServiceImp implements UsuarioService {

    private final UsuarioRepository usuarioRepository;

    public UsuarioServiceImp(UsuarioRepository usuarioRepository) {
        this.usuarioRepository = usuarioRepository;
    }

    @Override
    public UsuarioDto save(UsuarioCreate usuarioCreate) {
        Usuario usuario = usuarioCreate.toEntity();
        usuario = usuarioRepository.save(usuario);
        return UsuarioDto.toDto(usuario);
    }

    @Override
    public UsuarioDto findById(Long id) {
        Usuario usuario = usuarioRepository.findById(id).orElseThrow(() -> new NullPointerException("No se encontró el usuario con id: " + id));
        return UsuarioDto.toDto(usuario);
    }

    @Override
    public List<UsuarioDto> findAll() {
        List<Usuario> usuarios = usuarioRepository.findAll();
        return usuarios.stream().map(UsuarioDto::toDto).toList();
    }

    @Override
    public UsuarioDto update(UsuarioEdit usuarioEdit, Long idUsuario) {
        Usuario usuario = usuarioRepository.findById(idUsuario).orElseThrow(() -> new NullPointerException("No se encontró el usuario con id: " + idUsuario));
        usuarioEdit.applyTo(usuario);
        usuario = usuarioRepository.save(usuario);
        return UsuarioDto.toDto(usuario);
    }

    @Override
    public void deleteById(Long id) {
        Usuario usuario = usuarioRepository.findById(id).orElseThrow(() -> new NullPointerException("No se encontró el usuario con id: " + id));
        usuario.setEliminado(true);
        usuarioRepository.save(usuario);
    }
}