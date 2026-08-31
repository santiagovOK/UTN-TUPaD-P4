# Trabajo Práctico - Unidad 3 (POO: de Java a Python)

TP integrador de **Programación Orientada a Objetos: de Java a Python** (UTN-TUPaD — Programación IV).

Informe para este trabajo en: [informe.md](informe.md).

---

## ✨ Estudiante

- Nombre: Varela, Santiago Octavio
- Email institucional: santiago.varela@tupad.utn.edu.ar

Repositorio donde podrán encontrar mis trabajos de Programación IV: https://github.com/santiagovOK/UTN-TUPaD-P4

---

## Ecosistema de desarrollo

Por práctica, este proyecto se inicializó siguiendo el flujo descrito en [docs/ecosistema_esencial.md](docs/ecosistema_esencial.md): **pyenv** (versión de Python), **pipx** (herramientas globales), **Poetry** (gestor del proyecto) y **PyPI** (fuente de paquetes). El criterio central es que ninguna herramienta toque el sistema ni compita con `apt`; cada una opera en un espacio aislado (usuario o proyecto).

> Poetry se usa para reproducibilidad (entorno `.venv` propio del proyecto y `poetry.lock` bloqueado), no porque el código lo exija. En este caso la única dependencia instalada fue `mypy` para comprobaciones estáticas.

---

## Inicialización

```bash
# 1. Elegí la versión de Python (ya instalada con pyenv)
pyenv local 3.13.5

# 2. Iniciá el proyecto en el directorio actual (genera pyproject.toml)
cd unidad3_poo
poetry init

# 3. Poetry genera poetry.lock (lockfile de reproducibilidad)
poetry lock

# 4. Creá el entorno virtual y instalá dependencias (0 en este caso)
poetry install
```

**Estructura del proyecto:**

```text
unidad3_poo/
├── README.md                 # este archivo
├── figuras.py                # dominio resuelto (Partes 1-4)
├── fix_parte1_diagnostico.py # entregable ya corregido (prefijo 'fix_' para diferenciarlo del original)
├── demo_sintomas.py          # 2 síntomas de la Parte 1
├── libreria_externa.py       # PlanoCAD (librería externa - original sin modificar)
├── main.py                   # demo ejecutable
├── informe.md                # respuestas teóricas y decisiones
├── pyproject.toml
├── poetry.lock               # ← TRACKED, garantiza reproducibilidad
├── uml/
│   └── modelo_final.md       # diagrama de clases final
├── assets/
│   ├── parte1_diagnostico.py # código de partida original
│   └── libreria_externa.py   # original sin modificar
├── docs/                     # consignas y apuntes teóricos
```

---

## Ejecución

**Con Poetry**:

```bash
poetry run python main.py
poetry run python demo_sintomas.py
```

**Sin Poetry**: Si no usás Poetry, podés ejecutar los scripts directamente con cualquier Python 3.13+ (el código fuente no requiere dependencias para correr). Sin embargo, para ejecutar el análisis de tipos, primero debés instalar `mypy` manualmente usando pip:

```bash
pip install mypy

python main.py
python demo_sintomas.py
python -m mypy figuras.py
```

> Poetry solo aporta el entorno virtual aislado, el lockfile y la resolución de dependencias de desarrollo (como `mypy`). No es obligatorio para que el programa funcione.


---

## Análisis estático con Mypy

Dado que Python delega la validación de tipos al análisis estático fuera del tiempo de ejecución (resolviendo el Javismo #7), es necesario el uso de `mypy` para comprobar la solidez del diseño.

De acuerdo a las consignas, el análisis debe ejecutarse sobre:

* **`figuras.py`**: El núcleo del dominio. Mypy valida que las implementaciones de herencia (ABC) y duck typing (`Protocol` en `Exportable`) concuerden perfectamente con los tipos declarados, y que las listas heterogéneas se manejen sin errores.
* **`fix_parte1_diagnostico.py`**: El archivo original corregido, para validar que los type hints "engañosos" originales de la Parte 1 fueron exitosamente neutralizados.

Comando unificado para validar el proyecto:
```bash
poetry run mypy figuras.py fix_parte1_diagnostico.py
```

