// [Consigna TP7 - Inicialización con Vite, Tailwind CSS y CORS]:
//   - Configuración de Vite con plugins para React y Tailwind CSS v4.
//   - Servidor de desarrollo en puerto 5173 para integración y consumo de la API FastAPI.
// [Diagrama UML - docs/UML_FOOD_STORE.svg]:
//   - Servidor frontend del cliente SPA consumidor del clúster "Catálogo de Productos".
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    host: true,
  },
})
