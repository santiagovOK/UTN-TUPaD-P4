package com.tpUnidad9.unidad9_fundamentosSpringboot.entities;


/*
 *
 * @author Santiago Octavio Varela / @santiagovOK (GitHub)
 * <santiago.varela@tupad.utn.edu.ar>
 */

import jakarta.persistence.Entity;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;
import lombok.experimental.SuperBuilder;

@Getter
@Setter
// Excluimos categoría del ToString, como ya estaba en el TP Nº5
@ToString(exclude = "categoria")
// callSuper = false ignora el 'id' y el 'createdAt', enfocándose sólo en los atributos propios del producto (esto ya estaba así en el TP Nº5)
@EqualsAndHashCode(callSuper = false, exclude = "categoria")
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor

@Entity
public class Producto extends Base {

    private String nombre;
    private Double precio;
    private String descripcion;
    private int stock;
    private String imagen;
    private boolean disponible;

    @ManyToOne
    @JoinColumn(name = "categoria_id")
    private Categoria categoria; // Atributo faltante en el UML, pero que marca la relación de agregación 1 a muchos con Categoria

}
