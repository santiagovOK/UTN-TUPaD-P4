// [Consigna TP7 - Desacoplamiento de App.tsx & Navegación React Router]:
//   - "App.tsx no contiene lógica de negocio ni llamadas a APIs; su única responsabilidad es definir las rutas."
//   - Implementación inicial bajo estrategia combinada Bottom-Up + Walking Skeleton:
//     provee un esqueleto mínimo compilable conectado a BrowserRouter y QueryClientProvider desde la Fase 1,
//     que será evolucionado en la Tarea 3.6 con <Navbar /> y las vistas definitivas
//     (CategoriasPage, ProductsPage y ProductDetailPage).
// [Diagrama UML - Clúster Catálogo de Productos (docs/UML_FOOD_STORE.svg)]:
//   - Contenedor raíz de enrutamiento para las vistas de las entidades CATEGORIA y PRODUCTO.
import { Routes, Route } from "react-router-dom";

export function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route
            path="*"
            element={
              <section
                aria-label="Estado inicial de la aplicación"
                className="bg-white rounded-xl border border-slate-200 p-8 text-center shadow-xs"
              >
                <h1 className="text-xl font-semibold text-slate-900">
                  Food Store Admin — TP7
                </h1>
                <p className="mt-2 text-sm text-slate-600">
                  Walking Skeleton inicializado (TanStack Query + React Router).
                </p>
              </section>
            }
          />
        </Routes>
      </main>
    </div>
  );
}
