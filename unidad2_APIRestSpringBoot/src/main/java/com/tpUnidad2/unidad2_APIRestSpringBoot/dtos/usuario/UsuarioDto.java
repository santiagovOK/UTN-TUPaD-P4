package com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.usuario;

import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Usuario;

public record UsuarioDto(
        Long id,
        String nombre,
        String apellido,
        String mail,
        String celular
) {
    // Aquí se agrega el método toDto() usando los getters provistos por Lombok en la entidad Usuario.
    // Además, se le sumó el campo "id" que va a ser importante para identificar el recurso en el frontend (si es que esto se reutiliza así posteriormente).
    public static UsuarioDto toDto(Usuario usuario) {
        return new UsuarioDto(
                usuario.getId(),
                usuario.getNombre(),
                usuario.getApellido(),
                usuario.getMail(),
                usuario.getCelular()
        );
    }
}