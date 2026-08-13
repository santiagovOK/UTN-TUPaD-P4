package com.tpUnidad2.unidad2_APIRestSpringBoot.entities;

/*
 *
 * @author Santiago Octavio Varela / @santiagovOK (GitHub)
 * <santiago.varela@tupad.utn.edu.ar>
 */

import jakarta.persistence.Entity;
import jakarta.persistence.OneToMany;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;
import lombok.EqualsAndHashCode; // no es incluido en el video, pero si queremos mantener lo que hicimos en la unidad 5, tendría que ir.
import lombok.experimental.SuperBuilder; // si no uso experimental, me lanza error.
import lombok.Builder;

import java.util.HashSet;
import java.util.Set;

@Getter
@Setter
@ToString(exclude = "productos") // antes era excluido en el ToString para evitar problemas de recursividad infinita. Ahora se excluye desde Lombok.
@EqualsAndHashCode(callSuper = false)
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor
@Entity
public class Categoria extends Base {
    private String nombre;
    private String descripcion;

    @OneToMany(mappedBy = "categoria")
    @Builder.Default // Evita que el campo productos quede null
    private Set<Producto> productos = new HashSet<>(); // Relación de uno a muchos con Producto. No está en el video, pero dado el UML y lo aplicado en el TP Nº5 debería ir. Dado que antes se inicializaba en el constructor explícitamente, HashSet para en esta misma línea (la del atributo) para que se inicialice
}
