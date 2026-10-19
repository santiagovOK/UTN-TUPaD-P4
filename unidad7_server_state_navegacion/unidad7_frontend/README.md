# Frontend — Food Store SPA (React 19 + TypeScript + TanStack Query + React Router)

Interfaz de usuario para el Trabajo Práctico de la **Unidad 7** de **Programación IV (TUPaD - UTN)**. Desarrollada con **React 19**, **TypeScript**, **TanStack Query** (v5), **React Router** (v7) y **Tailwind CSS v4**, empaquetada con **Vite**.

Implementa una Single Page Application (SPA) modular con navegación por páginas (`/categorias`, `/productos`, `/productos/:id`), CRUD de **Categorías** con edición mediante `PUT /categorias/{id}` y CRUD interactivo de **Productos** desde `ProductsPage` mediante `ProductoModal` (incluida la asociación de categorías). El detalle del producto presenta su ficha junto con las categorías asociadas y los ingredientes que entrega el backend.

> **Alcance de ingredientes en TP7:** Se incorporaron contratos TypeScript para ingredientes y asociaciones con productos, y el detalle del producto muestra los ingredientes que entrega el backend. Esto mantiene el frontend en concordancia con los modelos y respuestas del backend. TP7 no incluye aquí una pantalla de gestión (CRUD) de ingredientes ni una pantalla de unidades de medida.

> **Nota sobre Modalidad de Entrega y Ejecución Unificada:**  
> Según las pautas de evaluación de la Unidad 7, el frontend se entrega como un archivo comprimido independiente:  
> **`Varela_Santiago_TPI_unidad7_frontend.zip`** (eliminando estrictamente la carpeta `node_modules/` y artefactos temporales antes de comprimir).  
>
> Asimismo, el proyecto Full Stack completo puede clonarse y ejecutarse desde el repositorio en GitHub:  
> **[https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion)**

---

## 🛠️ Tecnologías y Herramientas

- **React 19:** Biblioteca declarativa para construcción de interfaces basada en componentes funcionales y hooks.
- **TanStack Query (React Query v5):** Gestión declarativa del Server State: caché en memoria, deduplicación de consultas, estados de carga/error e invalidación automática tras mutaciones.
- **React Router (v7):** Enrutamiento declarativo para SPAs sin recarga de página, con navegación mediante enlaces activos (`NavLink`).
- **TypeScript (~5.7):** Tipado estático estricto para interfaces de dominio (`Categoria`, `Producto`) y props de componentes (`.tsx`).
- **Tailwind CSS v4:** Motor de estilos utilitarios integrado de forma nativa mediante `@tailwindcss/vite`.
- **Vite 6:** Entorno de desarrollo ultrarrápido con soporte de Hot Module Replacement (HMR).
- **pnpm:** Gestor de paquetes eficiente y determinista.

---

## 📋 Requisitos Previos

- **Node.js:** Versión 18.x o 20.x+ (LTS recomendado).
- **pnpm:** Versión 9.x+ (instalable vía `corepack enable` o `npm install -g pnpm`).

---

## 🚀 Inicialización y Ejecución Individual

### 1. Instalar dependencias

Desde el directorio `unidad7_frontend/`:

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
| **`pnpm build`** | `tsc -b && vite build` | Realiza el chequeo estricto de tipos con el compilador de TypeScript y compila el bundle optimizado para producción en `dist/`. |
| **`pnpm preview`** | `vite preview` | Previsualiza localmente la compilación de producción generada en `dist/`. |

---

## 📁 Estructura del Código Fuente

```text
unidad7_frontend/
├── index.html                  # Plantilla HTML principal
├── package.json                # Dependencias (React, TanStack Query, React Router) y scripts
├── tsconfig.json               # Configuración de referencias TypeScript
├── tsconfig.app.json           # Configuración de compilación para la aplicación React
├── tsconfig.node.json          # Configuración de TypeScript para herramientas de Vite
├── vite.config.ts              # Configuración de Vite y plugins (React + Tailwind CSS v4)
├── pnpm-workspace.yaml         # Configuración de workspace para builds de esbuild
├── README.md                   # Documentación técnica específica del frontend
└── src/
    ├── main.tsx                # Punto de entrada: monta QueryClientProvider y BrowserRouter
    ├── App.tsx                 # Enrutador estructural: define <Routes> y <Navbar /> (CERO lógica de negocio)
    ├── index.css               # Importación nativa de directivas de Tailwind CSS v4
    ├── types/                  # Interfaces de datos y contratos TypeScript
    │   ├── categoria.ts        # Interfaces Categoria, CategoriaCreate, CategoriaUpdate y PaginatedResponse
    │   ├── producto.ts         # Interfaces Producto, ProductoCreate y ProductoUpdate (con asociación N:N)
    │   ├── ingrediente.ts      # Contratos de ingredientes y asociaciones con productos
    │   └── index.ts            # Re-exportaciones centralizadas de tipos
    ├── services/               # Clientes y funciones HTTP puras (desacopladas de UI)
    │   ├── api.ts              # Configuración base de cliente fetch, manejo de errores HTTP y URL base
    │   ├── categorias.service.ts # Funciones asíncronas para el CRUD completo de Categorías
    │   ├── productos.service.ts  # Funciones asíncronas para catálogo paginado, detalle y CRUD de Productos
    │   └── index.ts            # Re-exportaciones centralizadas de servicios
    ├── pages/                  # Vistas completas por ruta
    │   ├── CategoriasPage.tsx  # Vista de Categorías: usa useQuery/useMutation y controla modal con useState
    │   ├── ProductsPage.tsx    # Catálogo paginado y filtrable; gestiona el CRUD de Productos
    │   ├── ProductDetailPage.tsx # Ficha del producto por ID con categorías e ingredientes asociados
    │   └── index.ts            # Re-exportaciones centralizadas de páginas
    └── components/             # Componentes de presentación puros
        ├── Navbar.tsx          # Barra de navegación con NavLink a Categorías y Productos
        ├── CategoriaCard.tsx   # Fila tabular: muestra id, nombre, descripción y acciones Editar/Eliminar
        ├── CategoriaList.tsx   # Contenedor tabular: renderiza cabeceras (NÚMERO, NOMBRE, etc.) y filas
        ├── CategoriaModal.tsx  # Formulario modal flotante accesible con backdrop para alta y edición
        └── ProductoModal.tsx   # Formulario modal controlado para crear y editar Productos y asociar categorías
```

---

## 🧩 Principios Arquitectónicos y Novedades de la Unidad 7

1. **`App.tsx` Libre de Lógica de Negocio (Regla Clave):**  
   A diferencia de implementaciones monolíticas anteriores, `App.tsx` ya no administra variables de estado ni realiza peticiones `fetch`. Su función es exclusivamente estructural: renderizar el layout global (`Navbar`) y definir la correspondencia de rutas mediante `<Routes>` y `<Route>`.
2. **Server State Gestionado con TanStack Query:**  
   - **Lecturas (`useQuery`):** Las páginas consultan el listado de categorías y el catálogo/detalle de productos mediante queries declarativas, que gestionan estados de carga, error y caché.
   - **Mutaciones (`useMutation`):** Las operaciones de alta (`POST`), modificación (`PUT`) y baja (`DELETE`) de categorías y productos se ejecutan como mutaciones.
   - **Invalidación Automática de Caché:** Tras el éxito de una mutación, se invalidan las queries relevantes con `queryClient.invalidateQueries(...)` para refrescar los datos en segundo plano, sin copiar listas del servidor a estado local.
3. **Client State Aislado con `useState`:**  
   El estado visual de apertura/cierre de los modales y la selección del registro para edición residen localmente en cada página. `CategoriasPage.tsx` y `ProductsPage.tsx` pasan esos datos y callbacks a sus respectivos modales controlados (`CategoriaModal` y `ProductoModal`).
4. **Enrutamiento Declarativo con React Router:**  
   - `BrowserRouter` envuelve la raíz en `main.tsx`.
   - Navegación instantánea sin recarga entre `/categorias`, `/productos` y `/productos/:id` mediante `<NavLink>` y `useNavigate`, con estilos activos automáticos para mejorar la experiencia de usuario.
5. **Componentes Presentacionales:**  
   `CategoriaList`, `CategoriaCard`, `CategoriaModal` y `ProductoModal` reciben datos, estado de apertura y callbacks por `props` tipados. Los modales sincronizan sus formularios con los datos de edición y no realizan directamente las peticiones HTTP.
