package com.tpUnidad1.unidad1_fundamentosSpringboot.config;

import org.springframework.stereotype.Component;
import jakarta.annotation.PostConstruct;

import com.tpUnidad1.unidad1_fundamentosSpringboot.service.UsuarioService;
import com.tpUnidad1.unidad1_fundamentosSpringboot.service.CategoriaService;
import com.tpUnidad1.unidad1_fundamentosSpringboot.service.ProductoService;
import com.tpUnidad1.unidad1_fundamentosSpringboot.service.PedidoService;

import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.usuario.UsuarioCreate;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.categoria.CategoriaCreate;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.categoria.CategoriaDto;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.producto.ProductoCreate;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.producto.ProductoDto;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.pedido.PedidoCreate;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.detallePedido.DetallePedidoCreate;

import com.tpUnidad1.unidad1_fundamentosSpringboot.enums.Rol;
import com.tpUnidad1.unidad1_fundamentosSpringboot.enums.Estado;
import com.tpUnidad1.unidad1_fundamentosSpringboot.enums.FormaPago;

import java.util.List;

// Prioricé la creación de DataInitializer para la instanciación en general porque es más adecuado respecto al uso de @PostConstruct y @Component. Así, se prioriza la correcta distinción del ciclo de vida de los componentes y la delegación de configuraciones, dejando Main (SpringbootApplication) limpio.

@Component
public class DataInitializer {

    private final UsuarioService usuarioService;
    private final CategoriaService categoriaService;
    private final ProductoService productoService;
    private final PedidoService pedidoService;

    // Aplicamos inyección de dependencias por constructor como exigen las consignas
    public DataInitializer(
            UsuarioService usuarioService,
            CategoriaService categoriaService,
            ProductoService productoService,
            PedidoService pedidoService) {
        this.usuarioService = usuarioService;
        this.categoriaService = categoriaService;
        this.productoService = productoService;
        this.pedidoService = pedidoService;
    }

    // Usamos @PostConstruct tal cual indica el material teórico para ejecutar lógica inicial
    @PostConstruct
    public void initData() {
        System.out.println("------ INICIALIZANDO BASE DE DATOS ------");

        // 1. Instanciar 2 Usuarios
        usuarioService.save(new UsuarioCreate("Juan", "Pérez", "juan@mail.com", "123456789", "pass123", Rol.USUARIO));
        usuarioService.save(new UsuarioCreate("María", "Gómez", "maria@mail.com", "987654321", "pass456", Rol.ADMIN));

        // 2. Instanciar 3 Categorias
        CategoriaDto c1 = categoriaService.save(new CategoriaCreate("Electrónica", "Aparatos electrónicos"));
        CategoriaDto c2 = categoriaService.save(new CategoriaCreate("Hogar", "Elementos para el hogar"));
        CategoriaDto c3 = categoriaService.save(new CategoriaCreate("Deportes", "Artículos deportivos"));

        // 3. Instanciar 10 Productos
        ProductoDto p1 = productoService.save(new ProductoCreate("TV 50'", 500000.0, "Televisor 50 pulgadas", 10, "url", true, c1.id()));
        ProductoDto p2 = productoService.save(new ProductoCreate("Radio", 30000.0, "Radio AM/FM", 20, "url", true, c1.id()));
        ProductoDto p3 = productoService.save(new ProductoCreate("Notebook", 800000.0, "Notebook Ryzen 5 16GB RAM", 5, "url", true, c1.id()));
        ProductoDto p4 = productoService.save(new ProductoCreate("Mouse", 20000.0, "Mouse inalambrico", 50, "url", true, c1.id()));
        ProductoDto p5 = productoService.save(new ProductoCreate("Mesa", 120000.0, "Mesa de comedor", 5, "url", true, c2.id()));
        ProductoDto p6 = productoService.save(new ProductoCreate("Silla", 30000.0, "Silla de madera", 20, "url", true, c2.id()));
        ProductoDto p7 = productoService.save(new ProductoCreate("Lampara", 30000.0, "Lampara de pie", 15, "url", true, c2.id()));
        ProductoDto p8 = productoService.save(new ProductoCreate("Pelota", 25000.0, "Pelota de futbol", 30, "url", true, c3.id()));
        ProductoDto p9 = productoService.save(new ProductoCreate("Raqueta", 80000.0, "Raqueta de tenis", 10, "url", true, c3.id()));
        ProductoDto p10 = productoService.save(new ProductoCreate("Bicicleta", 300000.0, "Bicicleta mountain bike", 5, "url", true, c3.id()));

        // 4. Instanciar 3 Pedidos, con al menos 2 detalles por cada uno, a través de pedidoService
        pedidoService.save(new PedidoCreate(Estado.PENDIENTE, FormaPago.EFECTIVO, List.of(
                new DetallePedidoCreate(1, p1.id()),
                new DetallePedidoCreate(2, p4.id())
        )));

        pedidoService.save(new PedidoCreate(Estado.CONFIRMADO, FormaPago.TARJETA, List.of(
                new DetallePedidoCreate(4, p6.id()),
                new DetallePedidoCreate(1, p5.id()),
                new DetallePedidoCreate(2, p7.id())
        )));

        pedidoService.save(new PedidoCreate(Estado.TERMINADO, FormaPago.TRANSFERENCIA, List.of(
                new DetallePedidoCreate(1, p10.id()),
                new DetallePedidoCreate(1, p8.id())
        )));

        System.out.println("------ BASE DE DATOS INICIALIZADA CON EXITO ------");
    }
}
