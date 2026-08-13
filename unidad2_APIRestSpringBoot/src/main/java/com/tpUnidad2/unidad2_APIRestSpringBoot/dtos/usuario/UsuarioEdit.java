package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario;

import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Usuario;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.Rol;

public record UsuarioEdit(
        String nombre,
        String apellido,
        String celular,
        String password,
        Rol rol
) {
    public void applyTo(Usuario usuario) {
        if (this.nombre != null)
            usuario.setNombre(this.nombre);
        if (this.apellido != null)
            usuario.setApellido(this.apellido);
        if (this.celular != null)
            usuario.setCelular(this.celular);
        if (this.password != null)
            usuario.setPassword(this.password);
        if (this.rol != null)
            usuario.setRol(this.rol);
    }
}
