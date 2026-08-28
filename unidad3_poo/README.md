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

> Poetry se usa para reproducibilidad (entorno `.venv` propio del proyecto y `poetry.lock` bloqueado), no porque el código lo exija. En este caso ni siquiera se pide instalar dependencias.

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

```
unidad3_poo/
├── README.md              # este archivo
├── figuras.py             # dominio resuelto (Partes 1-4)
├── parte1_diagnostico.py  # punto de partida (sin modificar)
├── demo_sintomas.py       # 2 síntomas de la Parte 1
├── libreria_externa.py    # PlanoCAD (librería externa)
├── main.py                # demo ejecutable
├── informe.md
├── uml/modelo_final.md
├── pyproject.toml
├── poetry.lock            # ← TRACKED, garantiza reproducibilidad
└── .venv/                 # ← UNTRACKED
```

---

## ▶Ejecución

**Con Poetry** (dentro del `.venv` del proyecto):

```bash
poetry run main
poetry run demo-sintomas
```

**Sin Poetry**: como el proyecto no tiene dependencias de terceros, corre con cualquier Python 3.13+ directamente, sin instalar nada:

```bash
python main.py
python demo_sintomas.py
```

> Poetry solo aporta el entorno virtual aislado y el lockfile. No es obligatorio para que el código funcione.


