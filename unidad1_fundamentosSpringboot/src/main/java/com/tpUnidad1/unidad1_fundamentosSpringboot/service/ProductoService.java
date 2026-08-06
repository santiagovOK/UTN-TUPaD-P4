package com.tpUnidad1.unidad1_fundamentosSpringboot.service;

/*
 *
 * @author Santiago Octavio Varela / @santiagovOK (GitHub)
 * <santiago.varela@tupad.utn.edu.ar>
 */

import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.producto.ProductoCreate;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.producto.ProductoDto;
import com.tpUnidad1.unidad1_fundamentosSpringboot.dtos.producto.ProductoEdit;

import java.util.List;

public interface ProductoService {
    public ProductoDto save(ProductoCreate productoCreate);
    public ProductoDto findById(Long id);
    public List<ProductoDto> findAll();
    public ProductoDto update(ProductoEdit productoEdit, Long idProducto);
    public void deleteById(Long id);
}
