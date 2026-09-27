import { describe, it, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { ProductoList } from '../components/ProductoList';
import type { Producto } from '../types/producto';

describe('ProductoList', () => {
  const mockProductos: Producto[] = [
    {
      id: 1,
      nombre: 'Monitor Gamer 27"',
      descripcion: 'Monitor IPS 144Hz 1ms',
      precio: 180000,
      categoria: 'Monitores',
      stock: 5,
      activo: true,
    },
    {
      id: 2,
      nombre: 'Mouse Óptico Inalámbrico',
      descripcion: 'Sensor de alta precisión 16000 DPI',
      precio: 25000,
      categoria: 'Periféricos',
      stock: 20,
      activo: true,
    },
    {
      id: 3,
      nombre: 'Auriculares con Cancelación de Ruido',
      descripcion: 'Conexión Bluetooth y jack 3.5mm',
      precio: 65000,
      categoria: 'Audio',
      stock: 0,
      activo: false,
    },
  ];

  it('muestra el mensaje de estado vacío cuando la lista de productos está vacía', () => {
    render(<ProductoList productos={[]} />);

    // Verificar presencia del mensaje con role="status"
    const statusMsg = screen.getByRole('status');
    expect(statusMsg).toBeInTheDocument();
    expect(statusMsg).toHaveTextContent(/no hay productos disponibles para mostrar/i);

    // Verificar que no se renderice ninguna tarjeta de producto
    expect(screen.queryAllByRole('article')).toHaveLength(0);
  });

  it('renderiza exactamente la cantidad N de tarjetas correspondiente al array de productos proporcionado', () => {
    render(<ProductoList productos={mockProductos} />);

    // Verificar que existan exactamente N artículos
    const cards = screen.getAllByRole('article');
    expect(cards).toHaveLength(mockProductos.length);

    // Verificar que los nombres de todos los productos figuren en el documento
    mockProductos.forEach((producto) => {
      expect(
        screen.getByRole('heading', { level: 3, name: producto.nombre })
      ).toBeInTheDocument();
    });

    // Verificar que no aparezca el mensaje de estado vacío
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('organiza los productos dentro de una lista no ordenada semántica (ul / li)', () => {
    render(<ProductoList productos={mockProductos} />);

    const list = screen.getByRole('list');
    expect(list).toBeInTheDocument();

    const listItems = within(list).getAllByRole('listitem');
    expect(listItems).toHaveLength(mockProductos.length);
  });

  it('incluye el contenedor semántico de sección con accesibilidad apropiada', () => {
    render(<ProductoList productos={mockProductos} />);

    const section = screen.getByRole('region', { name: /catálogo de productos/i });
    expect(section).toBeInTheDocument();
  });
});
