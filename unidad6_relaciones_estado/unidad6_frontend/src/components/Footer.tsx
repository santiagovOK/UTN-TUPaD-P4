export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-800 text-gray-300 mt-auto py-6 border-t border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm">
        <p className="font-medium text-gray-200">
          Gestor de Categorías &copy; {currentYear} &mdash; Trabajo Práctico 6
        </p>
        <p className="text-xs text-gray-300 mt-1">
          Desarrollado con React 19, TypeScript y Tailwind CSS
        </p>
      </div>
    </footer>
  );
}

export default Footer;
