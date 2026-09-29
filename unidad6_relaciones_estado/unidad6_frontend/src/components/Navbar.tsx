export function Navbar() {
  return (
    <header className="bg-indigo-600 text-white shadow-md">
      <nav
        aria-label="Navegación principal"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-2 sm:gap-4"
      >
        <div className="flex items-center space-x-3">
          <span className="text-xl sm:text-2xl font-bold tracking-tight">Gestor de Categorías</span>
          <span className="bg-indigo-700 text-indigo-100 text-xs px-2.5 py-0.5 rounded-full font-medium">
            TP6
          </span>
        </div>
        <ul className="flex items-center gap-1 sm:gap-2 text-sm font-medium list-none m-0 p-0">
          <li>
            <a
              href="#"
              className="px-3 py-2 rounded-md text-indigo-100 hover:text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-white transition-colors"
            >
              Catálogo
            </a>
          </li>
          <li>
            <a
              href="#"
              className="px-3 py-2 rounded-md text-indigo-200 hover:text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-white transition-colors"
            >
              Admin
            </a>
          </li>
        </ul>
      </nav>
    </header>
  );
}

export default Navbar;
