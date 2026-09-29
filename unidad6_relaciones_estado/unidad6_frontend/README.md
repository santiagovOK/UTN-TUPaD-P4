# Frontend — Gestor de Categorías (React 19 + TypeScript + Tailwind CSS v4)

Interfaz de usuario para el Trabajo Práctico de la **Unidad 6** de **Programación IV (TUPaD - UTN)**. Desarrollada con **React 19**, **TypeScript** y **Tailwind CSS v4**, empaquetada con **Vite**.

Permite la administración interactiva (CRUD) de categorías conectándose al backend de FastAPI mediante `fetch` nativo y gestión de estado con hooks (`useState`, `useEffect`).

---

## 🛠️ Tecnologías y Herramientas

- **React 19:** Biblioteca declarativa para construcción de interfaces basada en componentes funcionales.
- **TypeScript (~5.7):** Tipado estático estricto para interfaces de dominio y props de componentes.
- **Tailwind CSS v4:** Motor de estilos utilitarios integrado nativamente mediante `@tailwindcss/vite`.
- **Vite 6:** Entorno de desarrollo ultrarrápido con soporte Hot Module Replacement (HMR).
- **pnpm:** Gestor de paquetes eficiente y determinista.

---

## 📋 Requisitos Previos

- **Node.js:** Versión 18.x o 20.x+ (LTS recomendado).
- **pnpm:** Versión 9.x+ (instalable vía `corepack enable` o `npm install -g pnpm`).

---

## 🚀 Inicialización y Ejecución Individual

### 1. Instalar dependencias

Desde el directorio `unidad6_frontend/`:

```bash
pnpm install
```

### 2. Iniciar servidor de desarrollo

Para levantar únicamente la capa frontend:

```bash
pnpm dev
```

La aplicación quedará disponible en:
👉 **http://localhost:5173**

---

## 📜 Scripts Disponibles (`package.json`)

| Script | Comando | Descripción |
| :--- | :--- | :--- |
| **`pnpm dev`** | `vite` | Inicia el servidor de desarrollo local con recarga en caliente en el puerto 5173. |
| **`pnpm build`** | `tsc -b && vite build` | Realiza el chequeo de tipos con el compilador de TypeScript y compila el bundle optimizado para producción en `dist/`. |
| **`pnpm preview`** | `vite preview` | Previsualiza localmente la compilación de producción generada en `dist/`. |

---

## 📁 Estructura del Código Fuente

```text
unidad6_frontend/
├── index.html                  # Plantilla HTML principal
├── package.json                # Dependencias y scripts de Node
├── tsconfig.json               # Configuración de TypeScript
├── vite.config.ts              # Configuración de Vite y plugins
└── src/
    ├── main.tsx                # Punto de entrada de la aplicación React
    ├── App.tsx                 # Componente contenedor: estado global (useState), efectos (useEffect) y llamadas fetch
    ├── index.css               # Importación de directivas de Tailwind CSS v4
    ├── types/
    │   └── categoria.ts        # Interface TypeScript para la entidad Categoria
    └── components/
        ├── Navbar.tsx          # Barra de navegación accesible con branding
        ├── CategoriaCard.tsx   # Tarjeta atómica: muestra nombre, descripción, estado y botones Editar/Eliminar
        ├── CategoriaList.tsx   # Grilla contenedora: recibe lista de categorías por props y mapea las tarjetas
        ├── CategoriaModal.tsx  # Formulario modal accesible para creación y edición de categorías
        └── Footer.tsx          # Pie de página institucional con año dinámico
```

---

## 🧩 Principios de Diseño y Componentes

1. **Componentes Funcionales Puros:**  
   Los componentes en `src/components/` son puramente presentacionales (*dumb components*). Reciben datos y funciones callback mediante `props` fuertemente tipados con TypeScript. No gestionan estado global ni realizan llamadas de red autónomas.
2. **Centralización de Estado (`App.tsx`):**  
   Conforme a la consigna, la lógica de estado reside exclusivamente en el componente contenedor raíz:
   - `useState` para la lista de categorías (`categorias`).
   - `useState` para la visibilidad del modal (`isModalOpen`).
   - `useState` para la categoría en edición (`categoriaEnEdicion`).
3. **Efectos Secundarios (`useEffect`):**  
   Al montar la aplicación (`[]`), se invoca automáticamente el endpoint `GET http://localhost:8000/categorias/` para sincronizar los datos del backend.
4. **Fetch Nativo:**  
   Se utiliza la API estándar `window.fetch` con funciones `async/await`, gestionando encabezados `Content-Type: application/json` y control de respuestas HTTP (`res.ok`).
