import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProductoCard } from '../components/ProductoCard';
import type { Producto } from '../types/producto';

describe('ProductoCard', () => {
  const mockProductoCompleto: Producto = {
    id: 1,
    nombre: 'Teclado Mecánico RGB',
    descripcion: 'Teclado para gaming con switches mecánicos táctiles',
    precio: 45000.5,
    categoria: 'Periféricos',
    stock: 12,
    stock_minimo: 5,
    activo: true,
  };

  it('renderiza correctamente la información completa de un producto', () => {
    render(<ProductoCard producto={mockProductoCompleto} />);

    // Título y rol semántico
    expect(
      screen.getByRole('heading', { level: 3, name: mockProductoCompleto.nombre })
    ).toBeInTheDocument();

    // Descripción
    expect(screen.getByText(mockProductoCompleto.descripcion!)).toBeInTheDocument();

    // Categoría
    expect(screen.getByText('Periféricos')).toBeInTheDocument();

    // Estado activo
    expect(screen.getByText('Activo')).toBeInTheDocument();
    // Precio formateado (moneda ARS, tolera espacio no separable de Intl)
    expect(screen.getByText(/\$\s*45\.000,50/)).toBeInTheDocument();

    // Stock
    expect(screen.getByText('12 u.')).toBeInTheDocument();
  });

  it('muestra el badge "Inactivo" cuando activo es false', () => {
    const productoInactivo: Producto = {
      ...mockProductoCompleto,
      activo: false,
    };

    render(<ProductoCard producto={productoInactivo} />);

    expect(screen.getByText('Inactivo')).toBeInTheDocument();
    expect(screen.queryByText('Activo')).not.toBeInTheDocument();
  });

  it('muestra "General" como categoría fallback si no se especifica categoría', () => {
    const productoSinCategoria: Producto = {
      ...mockProductoCompleto,
      categoria: undefined,
    };

    render(<ProductoCard producto={productoSinCategoria} />);

    expect(screen.getByText('General')).toBeInTheDocument();
  });

  it('no renderiza el elemento de descripción si es omitida', () => {
    const productoSinDescripcion: Producto = {
      ...mockProductoCompleto,
      descripcion: undefined,
    };

    render(<ProductoCard producto={productoSinDescripcion} />);

    expect(screen.queryByText(mockProductoCompleto.descripcion!)).not.toBeInTheDocument();
  });

  it('resalta visualmente en rojo cuando el stock es 0', () => {
    const productoSinStock: Producto = {
      ...mockProductoCompleto,
      stock: 0,
    };

    render(<ProductoCard producto={productoSinStock} />);

    const stockElement = screen.getByText('0 u.');
    expect(stockElement).toBeInTheDocument();
    expect(stockElement).toHaveClass('text-red-500');
  });
});
