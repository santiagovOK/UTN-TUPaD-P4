package com.tpUnidad2.unidad2_APIRestSpringBoot.service;

// Santiago Octavio Varela / @santiagovOK (GitHub) <santiago.varela@tupad.utn.edu.ar>

import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.categoria.CategoriaCreate;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.categoria.CategoriaDto;
import com.tpUnidad2.unidad2_APIRestSpringBoot.dtos.categoria.CategoriaEdit;
import com.tpUnidad2.unidad2_APIRestSpringBoot.entities.Categoria;
import com.tpUnidad2.unidad2_APIRestSpringBoot.repository.CategoriaRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class CategoriaServiceImpl implements CategoriaService {
    private final CategoriaRepository categoriaRepository;

    public CategoriaServiceImpl(CategoriaRepository categoriaRepository) {
        this.categoriaRepository = categoriaRepository;
    }

    @Override
    public CategoriaDto save(CategoriaCreate categoriaCreate) {
        Categoria categoria = categoriaCreate.toEntity();
        categoria = categoriaRepository.save(categoria);
        return CategoriaDto.toDto(categoria);
    }

    @Override
    public CategoriaDto findById(Long id) {
        Categoria categoria = categoriaRepository.findById(id)
                .orElseThrow(() -> new NullPointerException("No se encontró categoría con el id: " + id));
        return CategoriaDto.toDto(categoria);
    }

    @Override
    public List<CategoriaDto> findAll() {
        return categoriaRepository.findAll().stream()
                .map(CategoriaDto::toDto).toList();
    }

    @Override
    public CategoriaDto update(CategoriaEdit categoriaEdit, Long idCategoria) {
        Categoria categoria = categoriaRepository.findById(idCategoria)
                .orElseThrow(() -> new NullPointerException("No se encontró categoría con el id: " + idCategoria));
        categoriaEdit.applyTo(categoria);
        categoria = categoriaRepository.save(categoria);
        return CategoriaDto.toDto(categoria);
    }

    @Override
    public void deleteById(Long id) {
        Categoria categoria = categoriaRepository.findById(id)
                .orElseThrow(() -> new NullPointerException("No se encontró categoría con el id: " + id));
        
        // Baja lógica: marcamos la entidad como eliminada en lugar de borrarla de la BD (ya estaba implementado en mis entidades desde Base).
        categoria.setEliminado(true);
        categoriaRepository.save(categoria);
    }
}