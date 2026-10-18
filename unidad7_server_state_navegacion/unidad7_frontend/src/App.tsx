// [Consigna TP7 - Desacoplamiento de App.tsx & Navegación React Router]:
//   - "App.tsx no contiene lógica de negocio ni llamadas a APIs; su única responsabilidad es definir las rutas."
//   - Estrategia combinada Bottom-Up + Walking Skeleton con Montaje Progresivo:
//     expone inmediatamente las vistas construidas (CategoriasPage en Tarea 3.3) para garantizar
//     feedback visual continuo en el navegador con HMR, manteniendo un fallback para las rutas en construcción.
// [Diagrama UML - Clúster Catálogo de Productos (docs/UML_FOOD_STORE.svg)]:
//   - Contenedor raíz de enrutamiento para las vistas de las entidades CATEGORIA y PRODUCTO.
import { Routes, Route } from "react-router-dom";
import { CategoriasPage } from "./pages/CategoriasPage";

export function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<CategoriasPage />} />
          <Route path="/categorias" element={<CategoriasPage />} />
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
