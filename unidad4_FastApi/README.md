## Crear entorno virtual (.venv)

En directorio raíz del proyecto:

```bash
python -m venv .venv
```

## Activar entorno

Con el entorno virtual ya creado, activarlo:

```bash
source .venv/bin/activate
```

## Instalar dependencias

Con el entorno virtual activado, instalar los paquetes declarados en `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Ejecutar servidor de desarrollo con Endpoints

Entrar al directorio del ejercicio y levantar el servidor:

```bash
cd u1_ej_8_integrador
uvicorn app.main:app --reload
```

Acceder a la API en `http://127.0.0.1:8000/docs`.
