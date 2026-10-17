// [Consigna TP7 - Integración Full Stack & Requerimientos Clave]:
//   - "El frontend React consume la API FastAPI mediante TanStack Query (useQuery / useMutation),
//      con invalidación de la caché luego de cada operación."
//   - "Organización en páginas separadas (CategoriasPage y ProductsPage) utilizando React Router."
// [Diagrama UML - docs/UML_FOOD_STORE.svg]:
//   - Provee el almacén de Server State (QueryClientProvider) y el contexto de navegación SPA
//     (BrowserRouter) para gestionar las vistas del clúster "Catálogo de Productos":
//     entidades CATEGORIA, PRODUCTO y tabla intermedia PRODUCTO_CATEGORIA.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";
import { App } from "./App";

// [Consigna TP7 - Manejo del estado del servidor con useQuery y useMutation]:
// Instancia global de QueryClient (a nivel de módulo, fuera del árbol de renderizado)
// con políticas explícitas de frescura (staleTime) y recolección de basura (gcTime) en caché.
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos de datos considerados "frescos" (FRESH)
      gcTime: 1000 * 60 * 10,   // 10 minutos en memoria antes de recolección de basura (INACTIVE)
      retry: 1,                 // 1 reintento automático ante fallos transitorios
      refetchOnWindowFocus: false, // evita refetches accidentales al cambiar de ventana
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {/* [Consigna TP7 - Integración Full Stack]: Proveedor de caché de TanStack Query v5 */}
    <QueryClientProvider client={queryClient}>
      {/* [Consigna TP7 - Navegación React Router]: Proveedor de History API para rutas SPA */}
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
