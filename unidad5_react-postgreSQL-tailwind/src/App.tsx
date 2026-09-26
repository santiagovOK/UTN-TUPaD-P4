import type { Producto } from './types/producto';
import { Navbar } from './components/Navbar';
import { ProductoForm } from './components/ProductoForm';
import { ProductoList } from './components/ProductoList';
import { Footer } from './components/Footer';

const PRODUCTOS_MOCK: Producto[] = [
  {
    id: 1,
    nombre: 'Notebook Lenovo ThinkPad E14',
    descripcion: 'Procesador Intel Core i5, 16GB RAM, 512GB SSD NVMe, pantalla 14" FHD IPS antireflejo.',
    precio: 1250000,
    categoria: 'Computación',
    stock: 8,
    stock_minimo: 3,
    activo: true,
  },
  {
    id: 2,
    nombre: 'Monitor Gamer Samsung Odyssey G3 24"',
    descripcion: 'Panel VA FHD, tasa de refresco 144Hz, tiempo de respuesta 1ms y soporte AMD FreeSync Premium.',
    precio: 340000,
    categoria: 'Monitores',
    stock: 15,
    stock_minimo: 5,
    activo: true,
  },
  {
    id: 3,
    nombre: 'Teclado Mecánico Wireless',
    descripcion: 'Layout 75%, switches Gateron Brown, retroiluminación RGB y conectividad Bluetooth/USB-C.',
    precio: 185000,
    categoria: 'Periféricos',
    stock: 4,
    stock_minimo: 5,
    activo: true,
  },
  {
    id: 4,
    nombre: 'Mouse Inalámbrico Logitech MX Master 3S',
    descripcion: 'Sensor de 8000 DPI sobre cualquier superficie, scroll MagSpeed y botones programables.',
    precio: 145000,
    categoria: 'Periféricos',
    stock: 0,
    stock_minimo: 2,
    activo: false,
  },
];

export function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 flex flex-col">
      {/* Skip Link para accesibilidad de teclado (WCAG 2.4.1) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-3 focus:left-3 focus:px-4 focus:py-2 focus:bg-indigo-600 focus:text-white focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 font-medium text-sm transition-all"
      >
        Saltar al contenido principal
      </a>

      <Navbar />

      <main
        id="main-content"
        className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8"
      >
        <h1 className="sr-only">Gestor de Productos - Panel Principal</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 items-start">
          <div className="lg:col-span-1">
            <ProductoForm />
          </div>
          <div className="lg:col-span-2">
            <ProductoList productos={PRODUCTOS_MOCK} />
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
