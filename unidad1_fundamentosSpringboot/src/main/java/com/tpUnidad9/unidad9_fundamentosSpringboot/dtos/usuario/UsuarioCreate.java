package com.tpUnidad9.unidad9_fundamentosSpringboot.dtos.usuario;

import com.tpUnidad9.unidad9_fundamentosSpringboot.entities.Usuario;
import com.tpUnidad9.unidad9_fundamentosSpringboot.enums.Rol;

public record UsuarioCreate(
        String nombre,
        String apellido,
        String mail,
        String celular,
        String password,
        Rol rol
) {
    public Usuario toEntity() {
        return Usuario.builder()
                .nombre(this.nombre)
                .apellido(this.apellido)
                .mail(this.mail)
                .celular(this.celular)
                .password(this.password)
                .rol(this.rol)
                .build();
    }
}