# Trabajo Práctico - Unidad 5 (FastAPI - Pydantic)

Siguiendo las [consignas](/docs/consignas.md), la realización de este trabajo parte de lo realizado en la [unidad anterior](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad4_FastApi). Allí dice "unidad 1", pero según lo que se solicita deduzco que es un error y hay que basarse en el práctico de la unidad 4

Resolución paso a paso de este trabajo en: [resolucion_tp5.md](/docs/resolucion_tp5.md).

---

## ✨ Estudiante

- Nombre: Varela, Santiago Octavio
- Email institucional: santiago.varela@tupad.utn.edu.ar

Repositorio donde podrán encontrar mis trabajos de Programación IV: https://github.com/santiagovOK/UTN-TUPaD-P4

---

## Inicialización

### Crear entorno virtual (.venv)

En directorio raíz del proyecto:

```bash
python -m venv .venv
```

### Activar entorno

Con el entorno virtual ya creado, activarlo:

```bash
source .venv/bin/activate
```

### Instalar dependencias

Con el entorno virtual activado, instalar los paquetes declarados en `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Configuración de Base de Datos (PostgreSQL / SQLite como Fallback)

El backend utiliza **SQLModel / SQLAlchemy**, lo que permite interactuar indistintamente con PostgreSQL o SQLite mediante la variable de entorno `DATABASE_URL`.

Cree un archivo `.env` en la raíz del proyecto (basado en `.env.example`):

1. **PostgreSQL (Entorno de producción / entrega):**
   ```env
   DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/tp5_react
   ```

2. **SQLite como Fallback Local (Pruebas y desarrollo sin PostgreSQL):**
   Si no se dispone de una instancia de PostgreSQL activa, se puede utilizar SQLite sin alterar el código de la aplicación:
   ```env
   # Base de datos en archivo local (persistente, inspeccionable con DBeaver):
   DATABASE_URL=sqlite:///./dev.db

   # Base de datos en memoria (volátil, reinicia con el servidor):
   DATABASE_URL=sqlite:///:memory:
   ```

   **Inspección visual en DBeaver:**
   Para abrir la base de datos local en DBeaver, crear una conexión de tipo **SQLite** e ingresar en el campo de conexión/URL JDBC:
   ```text
   jdbc:sqlite:/path/proyecto/dev.db
   ```
   *(O adaptar con la ruta absoluta correspondiente a la ubicación del proyecto).*

> **Nota sobre pruebas automatizadas (`pytest`):**  
> La suite de tests automatizados (`tests/conftest.py`) ya utiliza por defecto un motor **SQLite en memoria (`sqlite:///:memory:`)** con `StaticPool` de manera aislada por prueba. Por lo tanto, `pytest` siempre ejecuta y valida los 43 tests  sin necesidad de tener PostgreSQL u otro servicio externo en ejecución.

### Inicialización y Scripts del Frontend (Vite + React + TypeScript)

En la raíz del proyecto, instalar las dependencias de Node:

```bash
pnpm install
```

#### Scripts de Ejecución Disponibles (`package.json`)

| Comando | Descripción | Entorno / URL |
| :--- | :--- | :--- |
| **`pnpm dev`** | **Frontend único (`RN-12`):** Levanta el servidor Vite para maquetado estático con componentes funcionales puros. | `http://localhost:5173` |
| **`pnpm dev:back`** | **Backend único:** Levanta la API FastAPI con Uvicorn en modo `--reload` utilizando el entorno virtual. | `http://localhost:8000` (`/docs`) |
| **`pnpm dev:all`** | **Fullstack unificado:** Levanta **Frontend y Backend simultáneamente** en una única terminal mediante `concurrently`. | Ambos servidores |
| **`pnpm build`** | Verificación de tipos (`tsc -b`) y empaquetado de producción con Vite. | Directorio `dist/` |
| **`pnpm preview`** | Servidor local para previsualizar el bundle de producción compilado. | Localhost |

---

### Documentación Interactiva y Pruebas Backend

1. **Swagger UI:** Con el backend en ejecución, acceder a [http://localhost:8000/docs](http://localhost:8000/docs) para probar interactivamente las operaciones CRUD completas del catálogo de productos y verificar los esquemas OpenAPI y respuestas (200, 201, 204, 404, 409, 422).
2. **ReDoc:** Disponible en [http://localhost:8000/redoc](http://localhost:8000/redoc).
3. **Pruebas Automatizadas (`pytest`):**  
   Ejecutar en la terminal con el entorno virtual activo:
   ```bash
   pytest -v
   ```
   (Ejecuta los 43 casos de prueba con SQLite en memoria aislado).
4. **Pruebas Manuales (REST Client / VS Code):**  
   Documentadas y listas para disparar en [`src/tests/test_api.http`](src/tests/test_api.http).