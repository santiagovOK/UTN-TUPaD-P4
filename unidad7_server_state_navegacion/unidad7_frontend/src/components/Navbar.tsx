// [Consigna TP7 - Navegación React Router & Navbar (HU-04, RN-01)]:
//   - Barra de navegación principal que provee navegación declarativa mediante NavLink de React Router.
//   - Discriminación visual dinámica entre la ruta activa e inactiva.
//   - Desacoplamiento total de la lógica de negocio y estado del servidor (RN-01).
// [Diagrama UML - Clúster Catálogo de Productos (docs/UML_FOOD_STORE.svg)]:
//   - Acceso centralizado a los módulos de gestión para CATEGORIA y PRODUCTO.

import { NavLink, Link } from 'react-router-dom';

const getLinkClasses = ({ isActive }: { isActive: boolean }): string =>
  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
    isActive
      ? 'bg-indigo-600 text-white shadow-sm'
      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
  }`;

export function Navbar() {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <nav
        aria-label="Navegación principal"
        className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between"
      >
        {/* Bloque de Marca / Identidad */}
        <Link
          to="/categorias"
          className="flex items-center gap-2 sm:gap-3 hover:opacity-90 transition-opacity"
          aria-label="Food Store Admin - Ir al catálogo de categorías"
        >
          <span className="text-xl font-bold tracking-tight text-indigo-600">
            🍔 Food Store Admin
          </span>
          <span className="bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs px-2.5 py-0.5 rounded-full font-semibold">
            TP7
          </span>
        </Link>

        {/* Bloque de Enlaces Principales */}
        <ul className="flex items-center gap-1 sm:gap-2 list-none m-0 p-0">
          <li>
            <NavLink to="/categorias" className={getLinkClasses}>
              Categorías
            </NavLink>
          </li>
          <li>
            <NavLink to="/productos" className={getLinkClasses}>
              Productos
            </NavLink>
          </li>
        </ul>
      </nav>
    </header>
  );
}

export default Navbar;
