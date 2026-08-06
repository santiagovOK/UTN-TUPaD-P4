package com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.usuario;

import com.tpUnidad1.unidad1_fundamentosSpringboot.entities.Usuario;
import com.tpUnidad1.unidad1_fundamentosSpringboot.enums.Rol;

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
