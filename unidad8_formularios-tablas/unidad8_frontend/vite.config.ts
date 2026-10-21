// Base heredada del TP7; identidad y documentación adaptadas al TP8.
// [Configuración de Vite, Tailwind CSS y servidor de desarrollo]:
//   - Plugins para React y Tailwind CSS v4.
//   - Servidor de desarrollo en puerto 5173 para integración con la API FastAPI.
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
