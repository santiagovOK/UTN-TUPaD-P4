// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [Navegación React Router y Desacoplamiento de App.tsx]:
//   - App.tsx no contiene lógica de negocio ni llamadas a APIs; su única responsabilidad es definir las rutas.
//   - Enrutador declarativo que conecta las vistas hacia páginas dedicadas sin hooks de estado ni efectos.
// [Diagrama UML - Clúster Catálogo de Productos (docs/UML_FOOD_STORE.svg)]:
//   - Enrutamiento raíz para la gestión integral de CATEGORIA, PRODUCTO y el detalle con PRODUCTO_CATEGORIA.
import { Routes, Route } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import {
  CategoriasPage,
  ProductsPage,
  ProductDetailPage,
  IngredientesPage,
} from "./pages";

export function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <Navbar />
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<CategoriasPage />} />
          <Route path="/categorias" element={<CategoriasPage />} />
          <Route path="/productos" element={<ProductsPage />} />
          <Route path="/productos/:id" element={<ProductDetailPage />} />
          <Route path="/ingredientes" element={<IngredientesPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
