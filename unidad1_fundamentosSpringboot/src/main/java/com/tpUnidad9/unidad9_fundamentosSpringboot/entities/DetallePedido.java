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
// Exclusión de "pedido" y "producto" para evitar problemas (ya estaba así antes de aplicar Lombok)
@ToString(exclude = {"pedido", "producto"})
// Llamamos al equals de Base y excluimos "pedido" (ya estaba así antes de aplicar Lombok)
@EqualsAndHashCode(callSuper = true, exclude = "pedido")
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor

@Entity
public class DetallePedido extends Base {
    private int cantidad;
    @ManyToOne
    @JoinColumn(name = "pedido_id")
    private Pedido pedido;

    @ManyToOne
    @JoinColumn(name = "producto_id")
    private Producto producto;

    // Reescribimos el Getter que haría Lombok para calcular subtotal.
    // Dado que en este caso el subtotal pasa a ser un valor calculado, no tiene sentido colocarlo como atributo. Conceptualmente está ahí, pero en vez de ser un valor estático, se calcula cada vez que se llama al método getSubtotal() a partir de la cantidad y el precio del producto.
    public Double getSubtotal() {
        if (producto != null && producto.getPrecio() != null) {
            return cantidad * producto.getPrecio();
        }
        return 0.0;
    }
}
