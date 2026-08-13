package com.tpUnidad2.unidad2_APIRestSpringBoot.entities;

/*
 *
 * @author Santiago Octavio Varela / @santiagovOK (GitHub)
 * <santiago.varela@tupad.utn.edu.ar>
 */

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;
import lombok.experimental.SuperBuilder;
import com.tpUnidad2.unidad2_APIRestSpringBoot.enums.Rol;

@Getter
@Setter
// Como buena práctica de seguridad, directamente evitamos que password se imprima en el ToString. Antes había usado "****", pero creo que esto es mejor para el uso de Lombok.
@ToString(exclude = "password")
@EqualsAndHashCode(callSuper = true)
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor

@Entity
public class Usuario extends Base {
    private String nombre;
    private String apellido;
    @Column(unique = true) // Esto es para que no se repitan los mails en la base de datos.
    private String mail;
    private String celular;
    private String password;
    @Enumerated(EnumType.STRING) // Uso @Enumerated para que las posiciones del enum Rol sean catalogadas como Strings.
    private Rol rol;

}

