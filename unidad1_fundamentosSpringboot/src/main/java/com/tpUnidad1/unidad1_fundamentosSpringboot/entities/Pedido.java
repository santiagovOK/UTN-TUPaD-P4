package com.tpUnidad1.unidad1_fundamentosSpringboot.entities;

/*
 *
 * @author Santiago Octavio Varela / @santiagovOK (GitHub)
 * <santiago.varela@tupad.utn.edu.ar>
 */

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.OneToMany;
import jakarta.persistence.CascadeType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;
import lombok.experimental.SuperBuilder;

import com.tpUnidad1.unidad1_fundamentosSpringboot.enums.Estado;
import com.tpUnidad1.unidad1_fundamentosSpringboot.enums.FormaPago;
import com.tpUnidad1.unidad1_fundamentosSpringboot.interfaces.Calculable;

import java.time.LocalDate;
import java.util.HashSet;
import java.util.Set;

@Getter
@Setter
// Evitamos que al hacer un print del Pedido, intente imprimir todos los detalles (y que el detalle imprima al pedido infinitamente). Esto ya estaba implementado antes.
@ToString(exclude = "detalles")
// Excluimos "detalles" del equals y hashCode para evitar problemas de recursividad infinita. Esto ya estaba implementado antes.
@EqualsAndHashCode(callSuper = true, exclude = "detalles")
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor

// en el ejemplo del video, Calculable no está implementado, pero lo agrego para que se pueda calcular el total del pedido y es lo correcto hacerlo aquí en cuanto al UML (Acerca de cómo venía el tp - unidad 5)
@Entity
public class Pedido extends Base implements Calculable {

    private LocalDate fecha;
    @Enumerated(EnumType.STRING)
    private Estado estado;
    private Double total;
    @Enumerated(EnumType.STRING)
    private FormaPago formaPago;

    // Inicializamos el Set para que no lance NullPointerException
    @Builder.Default
    @OneToMany(mappedBy = "pedido", cascade = CascadeType.ALL, orphanRemoval = true) // Esto asegura que al eliminar un pedido, se eliminen sus detalles asociados y que al agregar un detalle, se asocie correctamente al pedido.
    private Set<DetallePedido> detalles = new HashSet<>();

    // Mantenemos la lógica el método, pero instanciando con Lombok
    public void addDetallePedido(int cantidad, Producto producto) {

        // Creamos el detalle usando el builder (dado el cambio en DetallePedido, ya no se usa un constructor manual)
        DetallePedido nuevoDetalle = DetallePedido.builder()
                .cantidad(cantidad)
                .producto(producto)
                .pedido(this)
                .build();

        this.detalles.add(nuevoDetalle);

        // Siempre que agregamos uno, recalculamos
        calcularTotal();
    }
    @Override
    public void calcularTotal() {
        this.total = java.util.Optional.ofNullable(this.detalles)
                .map(det -> det.stream()
                        .mapToDouble(DetallePedido::getSubtotal)
                        .sum())
                .orElse(0.0);
    }

}
