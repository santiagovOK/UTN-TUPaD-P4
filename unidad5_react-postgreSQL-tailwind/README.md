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

### Ejecutar servidor de desarrollo con Endpoints

Entrar al directorio del ejercicio y levantar el servidor:

```bash
cd src
fastapi dev app/main.py
# o uvicorn app.main:app --reload)
```

Acceder a la API en `http://127.0.0.1:8000/docs`.

### Validación y Pruebas (Swagger UI)

Para validar visualmente el funcionamiento del módulo de proveedores y probar interactivamente los escenarios de éxito y error exigidos (RN-01 a RN-05):

1. Asegúrate de tener el servidor en ejecución (`fastapi dev app/main.py`).
2. Ingresa a la interfaz interactiva de Swagger UI en tu navegador: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
3. Busca la etiqueta **"Proveedores"**, donde encontrarás todos los endpoints desarrollados (GET, POST, PUT).
4. Despliega cada endpoint, haz clic en el botón **"Try it out"**, completa los campos correspondientes (o déjalos deliberadamente inválidos) y presiona **"Execute"** para verificar los códigos de estado HTTP de retorno (200, 201, 404, 409, 422).
5. Como referencia técnica complementaria, todos estos escenarios se encuentran documentados en formato REST Client en el archivo [`u1_ej_8_integrador/tests/proveedores.http`](u1_ej_8_integrador/tests/proveedores.http)., como era exigido.

Dado que no se exigían capturas de pantalla en las consignas, no fueron añadidas.