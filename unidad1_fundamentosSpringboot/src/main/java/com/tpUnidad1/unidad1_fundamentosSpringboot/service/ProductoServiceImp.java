package com.tpUnidad1.unidad1_fundamentosSpringboot.service;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.producto.ProductoCreate;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.producto.ProductoDto;
import com.tpUnidad1.unidad1_fundamentosSpringboot.entities.Categoria;
import com.tpUnidad1.unidad1_fundamentosSpringboot.entities.Producto;
import com.tpUnidad1.unidad1_fundamentosSpringboot.repository.CategoriaRepository;
import com.tpUnidad1.unidad1_fundamentosSpringboot.repository.ProductoRepository;

import java.util.List;

import org.springframework.stereotype.Service;

@Service
public class ProductoServiceImp implements ProductoService {

    private final ProductoRepository productoRepository;
    private final CategoriaRepository categoriaRepository;

    public ProductoServiceImp(ProductoRepository productoRepository,  CategoriaRepository categoriaRepository) {
        this.productoRepository = productoRepository;
        this.categoriaRepository = categoriaRepository;
    }

    @Override
        public ProductoDto save(ProductoCreate productoCreate) {
            Categoria categoria = categoriaRepository.findById(productoCreate.idCategoria()).orElseThrow(() -> new NullPointerException("No se encontró la categoria con id: " + productoCreate.idCategoria()));
            Producto producto = productoCreate.toEntity();
            producto.setCategoria(categoria);
            producto = productoRepository.save(producto);
            return ProductoDto.toDto(producto);
        }

        @Override
        public ProductoDto findById(Long id) {
            Producto producto = productoRepository.findById(id).orElseThrow(() -> new NullPointerException("No se encontró el producto con id: " + id));
            return ProductoDto.toDto(producto);
        }

        @Override
        public List<ProductoDto> findAll() {
            List<Producto> productos = productoRepository.findAll();
            return productos.stream().map(ProductoDto::toDto).toList();
        }

        @Override
        public ProductoDto update(com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.producto.ProductoEdit productoEdit, Long idProducto) {
            Producto producto = productoRepository.findById(idProducto).orElseThrow(() -> new NullPointerException("No se encontró el producto con id: " + idProducto));
            Categoria categoria = null;
            if (productoEdit.idCategoria() != null) {
                categoria = categoriaRepository.findById(productoEdit.idCategoria()).orElseThrow(() -> new RuntimeException("No se encontró la categoria con id: " + productoEdit.idCategoria()));
            }
            productoEdit.applyTo(producto, categoria);
            producto = productoRepository.save(producto);
            return ProductoDto.toDto(producto);
        }

        @Override
        public void deleteById(Long id) {
            Producto producto = productoRepository.findById(id).orElseThrow(() -> new NullPointerException("No se encontró el producto con id: " + id));
            producto.setEliminado(true);
            productoRepository.save(producto);
        }
}