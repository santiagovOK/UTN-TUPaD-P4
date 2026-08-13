package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario;

import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Usuario;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.Rol;

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