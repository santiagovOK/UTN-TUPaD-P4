import type { Categoria } from './types/categoria';
import { Navbar } from './components/Navbar';
import { CategoriaModal } from './components/CategoriaModal';
import { CategoriaList } from './components/CategoriaList';
import { Footer } from './components/Footer';

const CATEGORIAS_MOCK: Categoria[] = [
  {
    id: 1,
    nombre: 'Muebles de Oficina',
    descripcion: 'Escritorios ergonómicos, sillas gerenciales, estanterías y muebles de guardado para espacios de trabajo.',
    activo: true,
  },
  {
    id: 2,
    nombre: 'Electrónica e Informática',
    descripcion: 'Dispositivos portátiles, pantallas de alta definición, periféricos wireless y accesorios informáticos.',
    activo: true,
  },
  {
    id: 3,
    nombre: 'Iluminación y Deco',
    descripcion: 'Lámparas LED regulables, apliques modernos y accesorios de iluminación ambiental.',
    activo: true,
  },
  {
    id: 4,
    nombre: 'Insumos y Papelería',
    descripcion: 'Artículos de librería comercial, resmas, consumibles y organizadores de escritorio.',
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
        <h1 className="sr-only">Gestor de Categorías - Panel Principal</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 items-start">
          <div className="lg:col-span-1">
            <CategoriaModal />
          </div>
          <div className="lg:col-span-2">
            <CategoriaList categorias={CATEGORIAS_MOCK} />
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
