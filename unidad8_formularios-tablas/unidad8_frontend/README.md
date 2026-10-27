# Frontend — Food Store Admin SPA (React 19 + TypeScript — Unidad 8)

Interfaz de usuario para el Trabajo Práctico de la **Unidad 8** de **Programación IV (TUPaD - UTN)**. Construida como una Single Page Application (SPA) modular con **React 19**, **TypeScript**, **TanStack Query** (v5), **React Router** (v7) y **Tailwind CSS v4**, empaquetada mediante **Vite 6**.

---

## 📋 Alcance y Estado del Frontend en la Unidad 8

El frontend continúa la arquitectura desacoplada del catálogo e incorpora la planificación de formularios tipados y tablas dinámicas:

1. **Catálogo de Categorías y Productos (Implementado — Base Heredada del TP7):**  
   Navegación por páginas (`/categorias`, `/productos`, `/productos/:id`), consumo de API mediante `useQuery` y `useMutation` con invalidación de caché, y modales interactivos controlados con `useState` para operaciones CRUD.
2. **Adopción de TanStack Form y TanStack Table (Planificado — Épicas 1 y 3):**  
   Reemplazo de los formularios HTML y estados manuales por **TanStack Form** (control unificado, validación tipada, prevención de doble submit), y transformación de las listas/grillas de administración en **TanStack Table v8** con ordenamiento por columnas, filtros locales y paginación en cliente sobre el conjunto total.
3. **Módulo CRUD de Ingredientes (Planificado — Épica 4):**  
   Implementación de `src/services/ingredientes.service.ts`, `IngredientesPage.tsx`, modal de alta/edición con selector de unidades de medida y registro de la ruta `/ingredientes` en el Navbar.

> **Modalidad de Entrega:**  
> Comprimido en **`Varela_Santiago_TPI_unidad8_frontend.zip`** (excluyendo estrictamente `node_modules/`, `dist/`, artefactos temporales y cualquier carpeta `guidelines/`). Consulte [docs/resolucion_tp8.md](../docs/resolucion_tp8.md) para la estrategia detallada y la política de exclusión de bibliografía en los ZIPs de entrega.  
> Repositorio oficial: [https://github.com/santiagovOK/UTN-TUPaD-P4](https://github.com/santiagovOK/UTN-TUPaD-P4)  
> Antecedente histórico: [Directorio Unidad 7 en GitHub](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion)

---

## 🛠️ Tecnologías y Librerías

- **React 19:** Biblioteca declarativa para la construcción de interfaces basada en componentes funcionales y hooks.
- **TanStack Query (React Query v5):** Manejo declarativo del Server State: caché en memoria, deduplicación de peticiones, estados asíncronos e invalidación reactiva.
- **React Router (v7):** Enrutamiento SPA puro mediante `BrowserRouter`, `Routes`, `Route` y enlaces activos `NavLink`.
- **TypeScript (~5.7):** Tipado estático riguroso para interfaces de dominio (`Categoria`, `Producto`, `Ingrediente`), props de componentes y contratos de API.
- **Tailwind CSS v4:** Motor de estilos utilitarios integrado nativamente a través de `@tailwindcss/vite`.
- **Vite 6:** Bundler ultrarrápido con soporte de Hot Module Replacement (HMR).
- **⏳ TanStack Form & TanStack Table v8:** Librerías normativas planificadas para las Épicas 1 y 3.

---

## Inicialización y Ejecución Local

### 0. Aprovisionamiento Automatizado desde la Raíz (`../setup.sh`)

El proyecto dispone de un script agnóstico e idempotente en la raíz (`setup.sh`) que automatiza de punta a punta la preparación del frontend y backend:

```bash
# Desde la raíz del repositorio:
./setup.sh

# O bien, para instalar e iniciar ambos servidores de desarrollo directamente:
./setup.sh --start
```

**Beneficios y automatizaciones para Frontend:**
- **Node.js `>= 18.18`:** Detección e hidratación transparente mediante versionadores activos (`nvm`, `fnm`, `volta`, `asdf`, `mise`) o instalación en espacio de usuario si faltara en el sistema.
- **Aprovisionamiento de `pnpm`:** Garantiza la presencia de `pnpm` en el entorno.
- **Instalación y Resolución de Dependencias:** Instala dependencias tanto en el orquestador raíz como en `unidad8_frontend/` preservando lockfiles.
- **Saneamiento Preventivo de Permisos y CRLF:** Repara permisos de ejecución (`chmod +x`) en `node_modules/.bin/` (vital cuando el proyecto se descomprime desde un ZIP) y normaliza retornos de carro CRLF.
- **Chequeo Dinámico de Binarios Nativos:** Valida la salud de `tsc` y `vite`; si detecta librerías nativas incompatibles o desalineadas, reinstala limpiamente.
- **Validación de Humo:** Compila el bundle de producción (`tsc -b && vite build`) garantizando tipado estricto sin errores.

**Opciones CLI relevantes:**
- `-y`, `--yes`: Modo desatendido sin confirmaciones interactivas.
- `-s`, `--start`, `--run`: Inicia concurrentemente Vite en el puerto `5173` y FastAPI en el `8000`.
- `--skip-checks`: Omite el chequeo de compilación al finalizar.
- `--no-system-install`: Opera exclusivamente en espacio de usuario.
- `--frontend-dir <ruta>`: Permite especificar un directorio frontend no estándar.
- `-h`, `--help`: Muestra la ayuda y diagnóstico del entorno.

---

### Instalación Manual Paso a Paso

Si prefiere configurar el entorno de forma manual e individual:

#### 1. Instalación de Dependencias
Desde la carpeta `unidad8_frontend/`:

```bash
pnpm install
```

#### 2. Iniciar Servidor de Desarrollo

```bash
pnpm dev
```

- **Acceso Web:** [http://localhost:5173](http://localhost:5173)  
- Se recomienda tener el backend en ejecución en [http://localhost:8000](http://localhost:8000) para interactuar con datos reales.

#### 3. Compilación de Producción y Validación de Tipos

```bash
pnpm build
```

Ejecuta `tsc -b` (verificación de tipos de extremo a extremo sin emitir código si hay errores) y luego compila el bundle estático en `dist/`.

---

## 🗺️ Mapa de Navegación y Rutas SPA

| Ruta | Componente / Página | Estado Actual | Planificación Unidad 8 |
|---|---|---|---|
| `/` | `CategoriasPage` | Operativo con Query y modal | Migración a TanStack Table + TanStack Form (tarea E3.1) |
| `/categorias` | `CategoriasPage` | Operativo con Query y modal | Migración a TanStack Table + TanStack Form (tarea E3.1) |
| `/productos` | `ProductsPage` | Operativo con CRUD y modal | Migración a TanStack Table + TanStack Form (tarea E3.2) |
| `/productos/:id` | `ProductDetailPage` | Operativo con ficha y detalle | Preservar navegación e ingredientes hidratados |
| `/ingredientes` | `IngredientesPage` | ⏳ No implementado | Creación completa de página CRUD, tabla y modal (tarea E4.2) |

---

## 🧩 Principios Arquitectónicos y Estándares de Código

1. **`App.tsx` Desacoplado y Libre de Lógica:**  
   `App.tsx` no maneja variables de estado ni llamadas `fetch`. Su única responsabilidad es renderizar la barra de navegación global (`Navbar`) y definir la correspondencia de rutas mediante `<Routes>`.
2. **Propiedad de los Hooks en las Páginas:**  
   Cada página (`CategoriasPage`, `ProductsPage`, `IngredientesPage`) es dueña de sus instancias de `useQuery`, `useMutation`, `useForm`, `useReactTable` y el control booleano del modal (`useState`). Los componentes secundarios (`*List`, `*Card`, `*Modal`) son presentacionales y reciben datos y callbacks por props tipadas.
3. **Frontera Estricta: Server State vs. Client State:**  
   Los datos provenientes de la API son administrados exclusivamente por TanStack Query. Queda prohibido copiar el contenido de `data` en un `useState` local. El estado local se reserva para variables de UI: apertura del modal, ítem en edición y términos de búsqueda/filtros.
4. **Formularios Resilientes:**  
   Los formularios con TanStack Form validan en campo (`onBlur`) y al enviar. Si el backend rechaza la mutación (por ejemplo HTTP 409 por duplicado), el modal permanece abierto con los datos ingresados y presenta el error al usuario.
