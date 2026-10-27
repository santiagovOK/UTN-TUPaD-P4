#!/usr/bin/env bash
# ==============================================================================
# setup.sh — Script Automatizado de Aprovisionamiento Integral Full Stack
# ==============================================================================
# Script agnóstico, desatendido e idempotente para aprovisionar entornos Full Stack
# (Python / FastAPI + Node.js / React / TypeScript / Vite / TanStack y Orquestador).
# Diseñado para ser reutilizable en trabajos prácticos, exámenes y proyectos finales.
# ==============================================================================

set -Eeuo pipefail
IFS=$'\n\t'

# ==============================================================================
# BLOQUE DE CONFIGURACIÓN DEL PROYECTO (PERSONALIZACIÓN RÁPIDA)
# ==============================================================================
# Este script auto-detecta la estructura del proyecto por convenciones estándar.
# Si su proyecto utiliza nombres de carpetas diferentes o específicos, puede
# configurarlo de cualquiera de estas tres formas (primera que defina gana):
#
#   1. Modificando los valores por defecto en este bloque de configuración.
#   2. Exportando variables de entorno antes de ejecutar:
#        BACKEND_DIR="mi_api" FRONTEND_DIR="mi_web" ./setup.sh
#   3. Pasando argumentos por línea de comandos:
#        ./setup.sh --backend-dir mi_api --frontend-dir mi_web
# ==============================================================================

# 1. Título del proyecto (si está vacío, se autoinfiere de package.json o de la carpeta raíz)
PROJECT_TITLE="${PROJECT_TITLE:-}"

# 2. Directorio de Backend:
# Si se deja vacío (""), auto-detecta carpetas que coincidan con:
# '*backend*', 'backend', 'api', 'server', 'app' (ej: 'unidad8_backend', 'backend')
CONFIG_BACKEND_DIR="${BACKEND_DIR:-}"

# 3. Directorio de Frontend:
# Si se deja vacío (""), auto-detecta carpetas que coincidan con:
# '*frontend*', 'frontend', 'client', 'web', 'ui' (ej: 'unidad8_frontend', 'frontend')
CONFIG_FRONTEND_DIR="${FRONTEND_DIR:-}"

# 4. Módulo principal de FastAPI para verificar la importación limpia en memoria:
# Si está vacío (""), auto-detecta 'app.main' (si existe app/main.py) o 'main' (si existe main.py)
FASTAPI_APP_MODULE="${FASTAPI_APP_MODULE:-}"

# 5. Módulos Python esenciales cuya importación se valida tras la instalación:
CORE_PY_MODULES="${CORE_PY_MODULES:-"fastapi uvicorn sqlmodel sqlalchemy psycopg2 pydantic dotenv pytest httpx"}"

# 6. Nombre por defecto de la base de datos PostgreSQL:
# Si se deja vacío (""), se extrae automáticamente de .env.example o del nombre del proyecto.
DEFAULT_PG_DB="${DEFAULT_PG_DB:-}"
# ==============================================================================

# ------------------------------------------------------------------------------
# Resolución de Rutas Absolutas y Auto-Detección de Carpetas
# ------------------------------------------------------------------------------
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Función para auto-detectar o resolver carpetas de subproyectos
detect_subproject_dir() {
    local explicit="$1"
    local role="$2"
    shift 2
    local patterns=("$@")

    # 1. Prioridad: valor explícito (entorno o bloque de configuración)
    if [[ -n "$explicit" ]]; then
        if [[ -d "$explicit" ]]; then
            (cd "$explicit" && pwd)
            return 0
        elif [[ -d "${ROOT_DIR}/${explicit}" ]]; then
            (cd "${ROOT_DIR}/${explicit}" && pwd)
            return 0
        else
            echo -e "\033[1;31m[ERROR]\033[0m El directorio de ${role} especificado no existe: '${explicit}'" >&2
            exit 1
        fi
    fi

    # 2. Prioridad: auto-detección por patrones en ROOT_DIR
    for pat in "${patterns[@]}"; do
        for candidate in "${ROOT_DIR}"/${pat}; do
            if [[ -d "$candidate" ]]; then
                (cd "$candidate" && pwd)
                return 0
            fi
        done
    done

    # 3. Fallback: carpeta con el nombre del rol en ROOT_DIR
    echo "${ROOT_DIR}/${role}"
}

# Auto-inferir título del proyecto si no fue provisto
if [[ -z "$PROJECT_TITLE" ]]; then
    if [[ -f "${ROOT_DIR}/package.json" ]] && command -v node >/dev/null 2>&1; then
        PROJECT_TITLE="$(node -e "try { console.log(JSON.parse(require('fs').readFileSync('${ROOT_DIR}/package.json', 'utf8')).name || ''); } catch {}" 2>/dev/null || true)"
    fi
    if [[ -z "$PROJECT_TITLE" ]]; then
        PROJECT_TITLE="$(basename "${ROOT_DIR}")"
    fi
fi

# Resolver directorios de Backend y Frontend
BACKEND_DIR="$(detect_subproject_dir "$CONFIG_BACKEND_DIR" "backend" "*backend*" "backend" "api" "server" "app")"
FRONTEND_DIR="$(detect_subproject_dir "$CONFIG_FRONTEND_DIR" "frontend" "*frontend*" "frontend" "client" "web" "ui")"

BACKEND_REL_DIR="$(realpath --relative-to="${ROOT_DIR}" "${BACKEND_DIR}" 2>/dev/null || basename "${BACKEND_DIR}")"
FRONTEND_REL_DIR="$(realpath --relative-to="${ROOT_DIR}" "${FRONTEND_DIR}" 2>/dev/null || basename "${FRONTEND_DIR}")"

# Auto-detectar módulo principal de FastAPI
if [[ -z "$FASTAPI_APP_MODULE" ]]; then
    if [[ -f "${BACKEND_DIR}/app/main.py" ]]; then
        FASTAPI_APP_MODULE="app.main"
    elif [[ -f "${BACKEND_DIR}/main.py" ]]; then
        FASTAPI_APP_MODULE="main"
    fi
fi

# Auto-detectar nombre por defecto de PostgreSQL
if [[ -z "$DEFAULT_PG_DB" ]]; then
    if [[ -f "${BACKEND_DIR}/.env.example" ]]; then
        DEFAULT_PG_DB="$(grep -E "DATABASE_URL=.*postgresql.*/" "${BACKEND_DIR}/.env.example" 2>/dev/null | head -n1 | sed -E 's/.*\///; s/[?#].*//; s/[^a-zA-Z0-9_-]//g' || true)"
    fi
    if [[ -z "$DEFAULT_PG_DB" ]]; then
        DEFAULT_PG_DB="$(echo "${PROJECT_TITLE}" | tr -cs '[:alnum:]_' '_' | sed 's/^_//;s/_$//')"
    fi
fi

# ------------------------------------------------------------------------------
# Trap de Errores y Diagnóstico
# ------------------------------------------------------------------------------
trap_error() {
    local exit_code="$?"
    local line_no="$1"
    local command_str="$2"
    echo "" >&2
    echo -e "\033[1;31m[ERROR CRÍTICO]\033[0m Falló la ejecución de setup.sh:" >&2
    echo -e "  - Comando : ${command_str}" >&2
    echo -e "  - Línea   : ${line_no}" >&2
    echo -e "  - Código  : ${exit_code}" >&2
    echo -e "Revise los registros superiores o ejecute con --help para opciones de diagnóstico." >&2
    exit "${exit_code}"
}
trap 'trap_error ${LINENO} "${BASH_COMMAND}"' ERR
trap 'echo -e "\n\033[1;33m[INTERRUPCIÓN]\033[0m Instalación cancelada por el usuario."; exit 130' INT TERM

# ------------------------------------------------------------------------------
# Configuración de Consola y Formato Visual
# ------------------------------------------------------------------------------
if [[ -t 1 && "${NO_COLOR:-0}" != "1" ]]; then
    C_RESET='\033[0m'
    C_BOLD='\033[1m'
    C_DIM='\033[2m'
    C_GREEN='\033[32m'
    C_BLUE='\033[34m'
    C_CYAN='\033[36m'
    C_YELLOW='\033[33m'
    C_RED='\033[31m'
    C_MAGENTA='\033[35m'
else
    C_RESET=''
    C_BOLD=''
    C_DIM=''
    C_GREEN=''
    C_BLUE=''
    C_CYAN=''
    C_YELLOW=''
    C_RED=''
    C_MAGENTA=''
fi

log_info()    { echo -e "${C_CYAN}[INFO]${C_RESET} $*"; }
log_step()    { echo -e "\n${C_BOLD}${C_BLUE}==>${C_RESET} ${C_BOLD}$*${C_RESET}"; }
log_success() { echo -e "${C_GREEN}[OK]${C_RESET} $*"; }
log_warn()    { echo -e "${C_YELLOW}[AVISO]${C_RESET} $*"; }
log_error()   { echo -e "${C_RED}[ERROR]${C_RESET} $*" >&2; }

# ------------------------------------------------------------------------------
# Banderas CLI y Opciones de Ejecución
# ------------------------------------------------------------------------------
NON_INTERACTIVE=false
NO_SYSTEM_INSTALL=false
RECREATE_VENV=false
SKIP_CHECKS=false
DB_MODE="auto" # auto | postgres | sqlite | memory
START_SERVERS=false

print_help() {
    cat <<EOF
Uso: $(basename "$0") [OPCIONES]

Script agnóstico, integral e idempotente para aprovisionar entornos Full Stack
(Backend FastAPI + Frontend React/TypeScript/Vite y Orquestador de Raíz).

CONFIGURACIÓN DETECTADA:
  Proyecto     : ${PROJECT_TITLE}
  Backend      : ${BACKEND_REL_DIR} (${BACKEND_DIR})
  Frontend     : ${FRONTEND_REL_DIR} (${FRONTEND_DIR})
  Postgres DB  : ${DEFAULT_PG_DB}

OPCIONES GENERALES:
  -y, --yes, --non-interactive   Modo no interactivo; asume 'sí' a todas las confirmaciones.
  -s, --start, --run             Inicia los servidores de desarrollo (Frontend + Backend) al finalizar.
      --no-system-install        Omite invocaciones con sudo/gestor de paquetes del sistema.
                                 Usa exclusivamente gestores y binarios en espacio de usuario.
      --recreate-venv            Elimina y recrea desde cero el entorno virtual Python (.venv).
      --skip-checks              Omite las verificaciones finales de humo (pytest y vite build).
      --db-mode <modo>           Configura DATABASE_URL en el archivo .env del backend.
                                 Modos válidos:
                                   auto     : Intenta PostgreSQL; si no responde, conmuta a SQLite (predeterminado).
                                   postgres : Fuerza PostgreSQL (${DEFAULT_PG_DB}).
                                   sqlite   : Fuerza SQLite en archivo (sqlite:///./dev.db).
                                   memory   : Fuerza SQLite en memoria (sqlite:///:memory:).

OPCIONES DE PERSONALIZACIÓN DE CARPETAS / PROYECTO:
      --backend-dir <ruta>       Especifica la ruta del directorio de backend (ej: backend, mi_api).
      --frontend-dir <ruta>      Especifica la ruta del directorio de frontend (ej: frontend, mi_web).
      --pg-db <nombre>           Especifica el nombre de la base PostgreSQL por defecto.
  -h, --help                     Muestra este mensaje de ayuda y finaliza.

EJEMPLOS:
  ./setup.sh                                     # Instalación estándar auto-detectada
  ./setup.sh --yes                               # Aprovisionamiento desatendido para CI o scripts
  ./setup.sh --db-mode sqlite                    # Fuerza el uso directo de SQLite en disco
  ./setup.sh --backend-dir api --frontend-dir ui # Personaliza rutas para proyectos no estándar
  ./setup.sh --recreate-venv                     # Reconstruye el entorno virtual de Python
  ./setup.sh --start                             # Verifica el entorno e inicia Frontend y Backend
  ./setup.sh --yes --skip-checks --start         # Arranque rápido desatendido
EOF
}

# Auto-detección de terminal no interactiva o entorno CI
if [[ ! -t 0 ]] || [[ "${CI:-false}" == "true" ]]; then
    NON_INTERACTIVE=true
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes|--non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        -s|--start|--run)
            START_SERVERS=true
            shift
            ;;
        --no-system-install)
            NO_SYSTEM_INSTALL=true
            shift
            ;;
        --recreate-venv)
            RECREATE_VENV=true
            shift
            ;;
        --skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        --backend-dir)
            if [[ -n "${2:-}" ]]; then
                CONFIG_BACKEND_DIR="$2"
                BACKEND_DIR="$(detect_subproject_dir "$CONFIG_BACKEND_DIR" "backend" "*backend*" "backend" "api" "server" "app")"
                BACKEND_REL_DIR="$(realpath --relative-to="${ROOT_DIR}" "${BACKEND_DIR}" 2>/dev/null || basename "${BACKEND_DIR}")"
                shift 2
            else
                log_error "La opción --backend-dir requiere una ruta."
                exit 1
            fi
            ;;
        --frontend-dir)
            if [[ -n "${2:-}" ]]; then
                CONFIG_FRONTEND_DIR="$2"
                FRONTEND_DIR="$(detect_subproject_dir "$CONFIG_FRONTEND_DIR" "frontend" "*frontend*" "frontend" "client" "web" "ui")"
                FRONTEND_REL_DIR="$(realpath --relative-to="${ROOT_DIR}" "${FRONTEND_DIR}" 2>/dev/null || basename "${FRONTEND_DIR}")"
                shift 2
            else
                log_error "La opción --frontend-dir requiere una ruta."
                exit 1
            fi
            ;;
        --pg-db)
            if [[ -n "${2:-}" ]]; then
                DEFAULT_PG_DB="$2"
                shift 2
            else
                log_error "La opción --pg-db requiere un nombre de base de datos."
                exit 1
            fi
            ;;
        --db-mode)
            if [[ -n "${2:-}" ]]; then
                case "$2" in
                    auto|postgres|sqlite|memory)
                        DB_MODE="$2"
                        shift 2
                        ;;
                    *)
                        log_error "Modo de base de datos desconocido: '$2'. Modos válidos: auto, postgres, sqlite, memory."
                        exit 1
                        ;;
                esac
            else
                log_error "La opción --db-mode requiere un argumento."
                exit 1
            fi
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            log_error "Opción no reconocida: '$1'. Ejecute './setup.sh --help' para ver la lista de opciones."
            exit 1
            ;;
    esac
done

# ------------------------------------------------------------------------------
# 1. Validación de Manifiestos y Archivos Críticos
# ------------------------------------------------------------------------------
log_step "1/6. Validando integridad de la estructura del proyecto (${PROJECT_TITLE})..."
log_info "Backend detectado  : ${BACKEND_REL_DIR} (${BACKEND_DIR})"
log_info "Frontend detectado : ${FRONTEND_REL_DIR} (${FRONTEND_DIR})"

REQUIRED_FILES=()
[[ -f "${ROOT_DIR}/package.json" ]] && REQUIRED_FILES+=("${ROOT_DIR}/package.json")
[[ -f "${BACKEND_DIR}/requirements.txt" ]] && REQUIRED_FILES+=("${BACKEND_DIR}/requirements.txt")
[[ -f "${FRONTEND_DIR}/package.json" ]] && REQUIRED_FILES+=("${FRONTEND_DIR}/package.json")

if [[ ${#REQUIRED_FILES[@]} -eq 0 ]]; then
    log_error "No se encontraron manifiestos esenciales (requirements.txt ni package.json) en: ${ROOT_DIR}"
    exit 1
fi

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        log_error "Falta el archivo indispensable: ${file}"
        exit 1
    fi
done

# Saneamiento preventivo de permisos de ejecución y formato CRLF
fix_project_permissions() {
    local target_dir script_file
    for target_dir in "${ROOT_DIR}" "${BACKEND_DIR}" "${FRONTEND_DIR}"; do
        if [[ -d "$target_dir" ]]; then
            while IFS= read -r -d '' script_file; do
                sed -i 's/\r$//' "$script_file" 2>/dev/null || true
                chmod +x "$script_file" 2>/dev/null || true
            done < <(find "$target_dir" -maxdepth 2 -type f \( -name "*.sh" -o -name "gradlew" -o -name "mvnw" \) ! -path "*/.venv/*" ! -path "*/node_modules/*" -print0 2>/dev/null)
        fi
    done
}
fix_project_permissions
log_success "Estructura base verificada en: ${ROOT_DIR}"

# ------------------------------------------------------------------------------
# 2. Detección de Plataforma y Gestor de Paquetes
# ------------------------------------------------------------------------------
PKG_MGR="unknown"
detect_pkg_manager() {
    if command -v apt-get >/dev/null 2>&1; then
        PKG_MGR="apt"
    elif command -v dnf >/dev/null 2>&1; then
        PKG_MGR="dnf"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MGR="yum"
    elif command -v pacman >/dev/null 2>&1; then
        PKG_MGR="pacman"
    elif command -v apk >/dev/null 2>&1; then
        PKG_MGR="apk"
    elif command -v zypper >/dev/null 2>&1; then
        PKG_MGR="zypper"
    elif command -v brew >/dev/null 2>&1; then
        PKG_MGR="brew"
    elif command -v choco >/dev/null 2>&1; then
        PKG_MGR="choco"
    elif command -v winget >/dev/null 2>&1; then
        PKG_MGR="winget"
    fi
}
detect_pkg_manager

run_privileged() {
    local cmd=("$@")
    if [[ "$NO_SYSTEM_INSTALL" == "true" ]]; then
        log_warn "Omitiendo ejecución con privilegios de sistema (--no-system-install): ${cmd[*]}"
        return 1
    fi

    if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
        "${cmd[@]}"
        return $?
    fi

    if command -v sudo >/dev/null 2>&1; then
        if sudo -n true 2>/dev/null; then
            sudo "${cmd[@]}"
            return $?
        elif [[ "$NON_INTERACTIVE" == "true" ]]; then
            log_warn "Sudo requiere contraseña en modo no interactivo. Omitiendo instalación con privilegios."
            return 1
        else
            log_info "Se requieren privilegios para instalar paquetes del sistema: ${cmd[*]}"
            sudo "${cmd[@]}"
            return $?
        fi
    else
        log_warn "No se dispone de sudo ni privilegios root para ejecutar: ${cmd[*]}"
        return 1
    fi
}

# Comprobar utilidades de descarga (curl o wget)
HTTP_GET=""
if command -v curl >/dev/null 2>&1; then
    HTTP_GET="curl -fsSL"
elif command -v wget >/dev/null 2>&1; then
    HTTP_GET="wget -qO-"
else
    log_info "Instalando curl para descargas seguras..."
    case "$PKG_MGR" in
        apt)    run_privileged apt-get update -y && run_privileged apt-get install -y curl ca-certificates ;;
        dnf)    run_privileged dnf install -y curl ca-certificates ;;
        yum)    run_privileged yum install -y curl ca-certificates ;;
        pacman) run_privileged pacman -S --noconfirm curl ca-certificates ;;
        apk)    run_privileged apk add --no-cache curl ca-certificates ;;
        brew)   brew install curl ;;
    esac
    if command -v curl >/dev/null 2>&1; then
        HTTP_GET="curl -fsSL"
    fi
fi

# ------------------------------------------------------------------------------
# 3. Motor Python (>= 3.11), Módulo venv/pip y Entorno Virtual
# ------------------------------------------------------------------------------
log_step "2/6. Verificando motor Python (>= 3.11) y entorno virtual..."

PYTHON_CANDIDATES=(
    "python3.13"
    "python3.12"
    "python3.11"
    "python3"
    "python"
)

PYTHON_BIN=""
find_valid_python() {
    PYTHON_BIN=""
    for cand in "${PYTHON_CANDIDATES[@]}"; do
        if command -v "$cand" >/dev/null 2>&1; then
            if "$cand" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
                PYTHON_BIN="$(command -v "$cand")"
                break
            fi
        fi
    done
}

find_valid_python

if [[ -z "$PYTHON_BIN" ]]; then
    log_warn "No se encontró un binario Python >= 3.11 en el PATH. Intentando provisión..."
    case "$PKG_MGR" in
        apt)
            run_privileged apt-get update -y && run_privileged apt-get install -y python3 python3-venv python3-pip python3-dev
            ;;
        dnf)
            run_privileged dnf install -y python3 python3-pip python3-devel
            ;;
        pacman)
            run_privileged pacman -S --noconfirm python python-pip
            ;;
        apk)
            run_privileged apk add --no-cache python3 py3-pip python3-dev
            ;;
        brew)
            brew install python@3.12 || brew install python
            ;;
        *)
            log_error "No se pudo proveer Python >= 3.11 automáticamente para el gestor '${PKG_MGR}'."
            log_error "Por favor, instale Python 3.11+ manualmente y vuelva a ejecutar setup.sh."
            exit 1
            ;;
    esac
    find_valid_python
    if [[ -z "$PYTHON_BIN" ]]; then
        log_error "No se detectó un Python >= 3.11 tras el intento de instalación."
        exit 1
    fi
fi

PY_VERSION_DETECTED="$("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")"
log_info "Intérprete Python base detectado: ${PYTHON_BIN} (v${PY_VERSION_DETECTED})"

# Verificar módulos venv y ensurepip en el Python base
HAS_VENV=true
if ! "$PYTHON_BIN" -c "import venv, ensurepip" 2>/dev/null; then
    HAS_VENV=false
    log_warn "El intérprete base carece de los módulos estándar venv o ensurepip."
    if [[ "$PKG_MGR" == "apt" ]]; then
        PY_MM="$("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
        log_info "Instalando python${PY_MM}-venv y python3-pip vía apt..."
        run_privileged apt-get update -y && run_privileged apt-get install -y "python${PY_MM}-venv" python3-venv python3-pip || true
        if "$PYTHON_BIN" -c "import venv, ensurepip" 2>/dev/null; then
            HAS_VENV=true
        fi
    fi
fi

# Resolución de canonicidad del .venv:
CANONICAL_VENV="${ROOT_DIR}/.venv"
BACKEND_VENV_LINK="${BACKEND_DIR}/.venv"

# Validar si el .venv existente es saludable
VENV_HEALTHY=false
if [[ "$RECREATE_VENV" == "false" && -d "${CANONICAL_VENV}" ]]; then
    if [[ -x "${CANONICAL_VENV}/bin/python" ]]; then
        if "${CANONICAL_VENV}/bin/python" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
            if "${CANONICAL_VENV}/bin/python" -m pip --version >/dev/null 2>&1; then
                VENV_HEALTHY=true
            fi
        fi
    fi
fi

if [[ "$VENV_HEALTHY" == "true" ]]; then
    log_info "Entorno virtual existente saludable en: ${CANONICAL_VENV}"
else
    if [[ -d "${CANONICAL_VENV}" ]]; then
        log_warn "El entorno virtual previo está ausente, corrupto o desactualizado. Recreando..."
        rm -rf "${CANONICAL_VENV}"
    else
        log_info "Creando entorno virtual aislado en: ${CANONICAL_VENV}..."
    fi

    if [[ "$HAS_VENV" == "true" ]]; then
        "$PYTHON_BIN" -m venv "${CANONICAL_VENV}"
    else
        log_warn "Creando venv sin pip incorporado (--without-pip) y bootstraping get-pip.py..."
        "$PYTHON_BIN" -m venv --without-pip "${CANONICAL_VENV}"
        if [[ -n "$HTTP_GET" ]]; then
            $HTTP_GET "https://bootstrap.pypa.io/get-pip.py" | "${CANONICAL_VENV}/bin/python" -
        else
            log_error "No se dispone de conexión HTTP ni pip en el entorno base."
            exit 1
        fi
    fi
fi

# Sincronización de enlace relativo en BACKEND_DIR/.venv si BACKEND_DIR != ROOT_DIR
if [[ "${BACKEND_DIR}" != "${ROOT_DIR}" ]]; then
    if [[ -L "${BACKEND_VENV_LINK}" ]]; then
        rm -f "${BACKEND_VENV_LINK}"
    elif [[ -d "${BACKEND_VENV_LINK}" && ! -L "${BACKEND_VENV_LINK}" ]]; then
        log_info "Migrando carpeta residual ${BACKEND_VENV_LINK} hacia enlace relativo..."
        rm -rf "${BACKEND_VENV_LINK}"
    fi
    REL_VENV_PATH="$("$PYTHON_BIN" -c "import os.path; print(os.path.relpath('${CANONICAL_VENV}', '${BACKEND_DIR}'))" 2>/dev/null || echo "../.venv")"
    (cd "${BACKEND_DIR}" && ln -s "${REL_VENV_PATH}" ".venv")
    log_success "Entorno virtual sincronizado en raíz y accesible desde ${BACKEND_REL_DIR}/.venv"
fi

VENV_PYTHON="${CANONICAL_VENV}/bin/python"

# ------------------------------------------------------------------------------
# 4. Instalación y Validación de Dependencias Backend (.py)
# ------------------------------------------------------------------------------
log_step "3/6. Instalando y verificando paquetes Python en ${BACKEND_REL_DIR}..."

# Actualizar herramientas de empaquetado para compatibilidad con manylinux/musllinux
"$VENV_PYTHON" -m pip install --upgrade --quiet pip setuptools wheel

if [[ -f "${BACKEND_DIR}/requirements.txt" ]]; then
    # Saneamiento de finales de línea CRLF en requirements.txt
    if command -v sed >/dev/null 2>&1; then
        sed -i 's/\r$//' "${BACKEND_DIR}/requirements.txt" 2>/dev/null || true
    fi

    install_py_requirements() {
        "$VENV_PYTHON" -m pip install -r "${BACKEND_DIR}/requirements.txt"
    }

    if ! install_py_requirements; then
        log_warn "Falló la instalación directa de dependencias Python. Posible falta de librerías nativas (psycopg2/libpq)."
        log_info "Intentando proveer herramientas de compilación C y encabezados de base de datos..."
        case "$PKG_MGR" in
            apt)
                run_privileged apt-get update -y && run_privileged apt-get install -y build-essential libpq-dev python3-dev
                ;;
            dnf|yum)
                run_privileged "${PKG_MGR}" install -y gcc postgresql-devel python3-devel
                ;;
            pacman)
                run_privileged pacman -S --noconfirm base-devel postgresql-libs
                ;;
            apk)
                run_privileged apk add --no-cache build-base postgresql-dev python3-dev
                ;;
            brew)
                brew install libpq
                ;;
        esac
        log_info "Reintentando instalación de dependencias Python..."
        install_py_requirements
    fi
fi

# Verificación de importabilidad de módulos configurados
"$VENV_PYTHON" -c "
import importlib, sys
mods = '${CORE_PY_MODULES}'.split()
for m in mods:
    try:
        importlib.import_module(m)
    except Exception as e:
        print(f'Error al importar módulo {m}: {e}', file=sys.stderr)
        sys.exit(1)
print(f'  {len(mods)} módulos esenciales importados correctamente.')
"

# Verificación de importación limpia del módulo de aplicación en memoria (si existe)
if [[ -n "$FASTAPI_APP_MODULE" ]]; then
    (
        cd "${BACKEND_DIR}" && \
        DATABASE_URL="sqlite:///:memory:" "$VENV_PYTHON" -c "
import importlib, sys
try:
    importlib.import_module('${FASTAPI_APP_MODULE}')
    print('  FastAPI ${FASTAPI_APP_MODULE} cargado satisfactoriamente.')
except Exception as e:
    print(f'Aviso: no se pudo cargar ${FASTAPI_APP_MODULE}: {e}', file=sys.stderr)
" || true
    )
fi
log_success "Paquetes Python y entorno backend validados."

# ------------------------------------------------------------------------------
# 5. Configuración y Validación de .env y Base de Datos
# ------------------------------------------------------------------------------
log_step "4/6. Configurando variables de entorno (.env) y conectividad a base de datos..."

ENV_FILE="${BACKEND_DIR}/.env"
ENV_EXAMPLE="${BACKEND_DIR}/.env.example"

if [[ ! -f "$ENV_FILE" && -f "$ENV_EXAMPLE" ]]; then
    log_info "Generando '${ENV_FILE}' a partir de '${ENV_EXAMPLE}'..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
fi

if [[ -f "$ENV_FILE" ]]; then
    # Eliminar posibles retornos de carro CRLF
    if command -v sed >/dev/null 2>&1; then
        sed -i 's/\r$//' "$ENV_FILE" 2>/dev/null || true
    fi

    # Aplicar modo explícito de base de datos si fue solicitado por CLI
    apply_db_mode() {
        local mode="$1"
        case "$mode" in
            sqlite)
                log_info "Aplicando modo SQLite en disco en .env..."
                sed -i 's/^DATABASE_URL=/# DATABASE_URL=/g' "$ENV_FILE" 2>/dev/null || true
                if grep -q "DATABASE_URL=sqlite:///./dev.db" "$ENV_FILE"; then
                    sed -i 's/^# *DATABASE_URL=sqlite:\/\/\/.\/dev\.db/DATABASE_URL=sqlite:\/\/\/.\/dev\.db/' "$ENV_FILE"
                else
                    echo "DATABASE_URL=sqlite:///./dev.db" >> "$ENV_FILE"
                fi
                ;;
            memory)
                log_info "Aplicando modo SQLite en memoria en .env..."
                sed -i 's/^DATABASE_URL=/# DATABASE_URL=/g' "$ENV_FILE" 2>/dev/null || true
                if grep -q "DATABASE_URL=sqlite:///:memory:" "$ENV_FILE"; then
                    sed -i 's/^# *DATABASE_URL=sqlite:\/\/\/:memory:/DATABASE_URL=sqlite:\/\/\/:memory:/' "$ENV_FILE"
                else
                    echo "DATABASE_URL=sqlite:///:memory:" >> "$ENV_FILE"
                fi
                ;;
            postgres)
                log_info "Aplicando modo PostgreSQL (${DEFAULT_PG_DB}) en .env..."
                sed -i 's/^DATABASE_URL=/# DATABASE_URL=/g' "$ENV_FILE" 2>/dev/null || true
                if grep -q "DATABASE_URL=postgresql+psycopg2" "$ENV_FILE"; then
                    sed -i 's/^# *DATABASE_URL=postgresql+psycopg2\(.*\)/DATABASE_URL=postgresql+psycopg2\1/' "$ENV_FILE"
                else
                    echo "DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/${DEFAULT_PG_DB}" >> "$ENV_FILE"
                fi
                ;;
            auto)
                # Asegurar que al menos una DATABASE_URL esté activa
                if ! grep -q "^DATABASE_URL=" "$ENV_FILE"; then
                    log_info "No se encontró DATABASE_URL activa en .env; activando valor por defecto de .env.example..."
                    if grep -q "^# *DATABASE_URL=postgresql" "$ENV_FILE"; then
                        sed -i 's/^# *DATABASE_URL=postgresql/DATABASE_URL=postgresql/' "$ENV_FILE"
                    else
                        echo "DATABASE_URL=sqlite:///./dev.db" >> "$ENV_FILE"
                    fi
                fi
                ;;
        esac
    }

    apply_db_mode "$DB_MODE"

    # Probar la conectividad real de la URL configurada
    test_db_connection() {
        (
            cd "${BACKEND_DIR}" && \
            "$VENV_PYTHON" -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
load_dotenv(override=True)
url = os.getenv('DATABASE_URL', '')
if not url:
    raise SystemExit(2)
extra = {}
if url.startswith('sqlite'):
    extra['connect_args'] = {'check_same_thread': False}
engine = create_engine(url, **extra)
with engine.connect() as conn:
    pass
" 2>/dev/null
        )
    }

    if test_db_connection; then
        CURRENT_DB_URL="$(grep "^DATABASE_URL=" "$ENV_FILE" | head -n1)"
        log_success "Conexión a base de datos validada con éxito: ${CURRENT_DB_URL}"
    else
        CURRENT_DB_URL="$(grep "^DATABASE_URL=" "$ENV_FILE" | head -n1)"
        log_warn "Falló la conexión con la configuración activa: ${CURRENT_DB_URL}"
        if [[ "$DB_MODE" == "auto" && "$CURRENT_DB_URL" == *"postgresql"* ]]; then
            log_warn "El servidor PostgreSQL no responde localmente. Aplicando fallback automático a SQLite (dev.db)..."
            apply_db_mode "sqlite"
            if test_db_connection; then
                log_success "Fallback a SQLite verificado: DATABASE_URL=sqlite:///./dev.db"
            else
                log_error "No fue posible conectar ni con PostgreSQL ni con SQLite local."
                exit 1
            fi
        else
            log_error "No se pudo conectar a la base de datos especificada (${CURRENT_DB_URL})."
            log_error "Verifique que el servicio PostgreSQL esté activo o ejecute con '--db-mode sqlite'."
            exit 1
        fi
    fi
else
    log_info "No se detectó archivo .env ni .env.example en ${BACKEND_REL_DIR}. Omitiendo configuración de BD."
fi

# ------------------------------------------------------------------------------
# 6. Motor Node.js (>= 18.18), Gestor pnpm y Paquetes Frontend/Raíz (.ts / .tsx)
# ------------------------------------------------------------------------------
log_step "5/6. Verificando motor Node.js (>= 18.18), pnpm y dependencias Frontend/Raíz..."

hydrate_node_env() {
    # NVM
    if [[ -d "${HOME}/.nvm" && -s "${HOME}/.nvm/nvm.sh" ]]; then
        export NVM_DIR="${HOME}/.nvm"
        # shellcheck disable=SC1091
        source "${NVM_DIR}/nvm.sh" || true
    fi
    # FNM
    if [[ -d "${HOME}/.local/share/fnm" ]]; then
        export PATH="${HOME}/.local/share/fnm:${PATH}"
        eval "$(fnm env 2>/dev/null || true)"
    fi
    # Volta
    if [[ -d "${HOME}/.volta/bin" ]]; then
        export VOLTA_HOME="${HOME}/.volta"
        export PATH="${VOLTA_HOME}/bin:${PATH}"
    fi
    # asdf
    if [[ -d "${HOME}/.asdf/shims" ]]; then
        export PATH="${HOME}/.asdf/shims:${PATH}"
    fi
    # mise
    if [[ -d "${HOME}/.local/share/mise/shims" ]]; then
        export PATH="${HOME}/.local/share/mise/shims:${PATH}"
    fi
    # PNPM global / local bin
    export PNPM_HOME="${HOME}/.local/share/pnpm"
    export PATH="${PNPM_HOME}:${HOME}/.local/bin:${HOME}/.npm-global/bin:${PATH}"
}

hydrate_node_env

check_node_version() {
    if command -v node >/dev/null 2>&1; then
        node -e "const [M,m]=process.versions.node.split('.').map(Number); process.exit((M>18||(M===18&&m>=18))?0:1)" 2>/dev/null
        return $?
    fi
    return 1
}

if ! check_node_version; then
    log_warn "Node.js no está instalado o su versión es menor a 18.18. Intentando provisión..."
    if command -v nvm >/dev/null 2>&1; then
        log_info "Instalando Node LTS vía nvm..."
        nvm install --lts && nvm use --lts
    elif command -v fnm >/dev/null 2>&1; then
        log_info "Instalando Node LTS vía fnm..."
        fnm install --lts && fnm use lts-latest
    else
        log_info "Intentando instalar Node.js mediante gestor de paquetes de sistema o binario local..."
        case "$PKG_MGR" in
            apt)
                run_privileged apt-get update -y && run_privileged apt-get install -y nodejs npm || true
                ;;
            dnf|yum)
                run_privileged "${PKG_MGR}" install -y nodejs npm || true
                ;;
            pacman)
                run_privileged pacman -S --noconfirm nodejs npm || true
                ;;
            apk)
                run_privileged apk add --no-cache nodejs npm || true
                ;;
            brew)
                brew install node || true
                ;;
        esac
    fi
    hydrate_node_env
fi

if ! check_node_version; then
    log_error "No se pudo proveer un motor Node.js >= 18.18."
    log_error "Por favor instale Node.js 18.18+, 20 LTS o 22 LTS (recomendado: fnm o nvm) y reintente."
    exit 1
fi

NODE_VERSION_DETECTED="$(node -v)"
log_info "Motor Node.js verificado: $(command -v node) (${NODE_VERSION_DETECTED})"

check_pnpm() {
    if command -v pnpm >/dev/null 2>&1; then
        local pnpm_maj
        pnpm_maj="$(pnpm -v | cut -d. -f1)"
        if [[ "$pnpm_maj" -ge 8 ]]; then
            return 0
        fi
    fi
    return 1
}

if ! check_pnpm; then
    log_warn "pnpm (>= 8) no disponible en PATH. Iniciando provisión en espacio de usuario..."
    mkdir -p "${HOME}/.local/bin" "${HOME}/.local/share/pnpm"
    
    # Intento 1: Corepack
    if command -v corepack >/dev/null 2>&1; then
        log_info "Activando pnpm vía corepack en ~/.local/bin..."
        corepack enable --install-directory "${HOME}/.local/bin" 2>/dev/null || true
        corepack prepare pnpm@latest --activate 2>/dev/null || true
    fi

    # Intento 2: npm global con prefix en ~/.local
    if ! check_pnpm && command -v npm >/dev/null 2>&1; then
        log_info "Instalando pnpm vía npm con prefijo en ~/.local..."
        npm install -g pnpm --prefix "${HOME}/.local" --silent 2>/dev/null || true
    fi

    # Intento 3: Instalador standalone oficial de pnpm
    if ! check_pnpm && [[ -n "$HTTP_GET" ]]; then
        log_info "Descargando instalador standalone oficial de pnpm..."
        SHELL="$(command -v bash)" PNPM_HOME="${HOME}/.local/share/pnpm" $HTTP_GET "https://get.pnpm.io/install.sh" | sh - 2>/dev/null || true
    fi

    hydrate_node_env
fi

if ! check_pnpm; then
    log_error "No se pudo aprovisionar 'pnpm'. Instálelo ejecutando: 'npm install -g pnpm' o 'corepack enable'."
    exit 1
fi

PNPM_VERSION_DETECTED="$(pnpm -v)"
log_info "Gestor pnpm verificado: $(command -v pnpm) (v${PNPM_VERSION_DETECTED})"

# Instalación en raíz si existe package.json
if [[ -f "${ROOT_DIR}/package.json" ]]; then
    log_info "Instalando dependencias de orquestación en raíz..."
    if ! pnpm --dir "${ROOT_DIR}" install --frozen-lockfile >/dev/null 2>&1; then
        pnpm --dir "${ROOT_DIR}" install --no-frozen-lockfile
    fi
    chmod +x "${ROOT_DIR}/node_modules/.bin/"* 2>/dev/null || true
fi

# Instalación en frontend si existe y difiere de raíz
if [[ -d "${FRONTEND_DIR}" && -f "${FRONTEND_DIR}/package.json" && "${FRONTEND_DIR}" != "${ROOT_DIR}" ]]; then
    log_info "Instalando dependencias en ${FRONTEND_REL_DIR}..."
    if ! pnpm --dir "${FRONTEND_DIR}" install --frozen-lockfile >/dev/null 2>&1; then
        pnpm --dir "${FRONTEND_DIR}" install --no-frozen-lockfile
    fi

    chmod +x "${FRONTEND_DIR}/node_modules/.bin/"* 2>/dev/null || true
    # Chequeo dinámico de salud de dependencias de frontend
    check_frontend_health() {
        local tsc_bin="${FRONTEND_DIR}/node_modules/.bin/tsc"
        local vite_bin="${FRONTEND_DIR}/node_modules/.bin/vite"

        if [[ -f "${FRONTEND_DIR}/tsconfig.json" ]]; then
            if [[ ! -x "$tsc_bin" ]] || ! "$tsc_bin" --version >/dev/null 2>&1; then
                return 1
            fi
        fi

        if grep -q '"vite"' "${FRONTEND_DIR}/package.json" 2>/dev/null; then
            if [[ ! -x "$vite_bin" ]]; then
                return 1
            fi
        fi

        (
            cd "${FRONTEND_DIR}" && \
            node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const deps = Object.keys(Object.assign({}, pkg.dependencies, pkg.devDependencies));
for (const p of deps) {
    try {
        require.resolve(p, { paths: [process.cwd()] });
    } catch (e) {
        if (!p.startsWith('@types/')) {
            process.exit(1);
        }
    }
}
" >/dev/null 2>&1
        )
    }

    if ! check_frontend_health; then
        log_warn "Se detectaron binarios nativos desalineados o paquetes incompletos en ${FRONTEND_REL_DIR}. Reinstalando..."
        rm -rf "${FRONTEND_DIR}/node_modules"
        pnpm --dir "${FRONTEND_DIR}" install --no-frozen-lockfile
        chmod +x "${FRONTEND_DIR}/node_modules/.bin/"* 2>/dev/null || true
        if ! check_frontend_health; then
            log_error "Persiste un fallo de resolución en dependencias de ${FRONTEND_REL_DIR}."
            exit 1
        fi
    fi
    log_success "Dependencias y herramientas de ${FRONTEND_REL_DIR} validadas."
fi

# ------------------------------------------------------------------------------
# 7. Validaciones de Humo Post-Instalación
# ------------------------------------------------------------------------------
if [[ "$SKIP_CHECKS" == "true" ]]; then
    log_step "6/6. Omitiendo pruebas de humo finales (--skip-checks activo)."
else
    log_step "6/6. Ejecutando pruebas de humo integrales..."

    # Verificación 1: Suite de tests backend (si existe configuración de pruebas)
    if [[ -f "${BACKEND_DIR}/pytest.ini" || -d "${BACKEND_DIR}/tests" ]]; then
        log_info "Ejecutando suite de pruebas backend (pytest) en ${BACKEND_REL_DIR}..."
        (
            cd "${BACKEND_DIR}" && \
            "${VENV_PYTHON}" -m pytest
        )
        log_success "Pruebas backend superadas al 100%."
    else
        log_info "No se detectaron tests backend (pytest.ini ni tests/). Omitiendo pytest."
    fi

    # Verificación 2: Compilación y empaquetado frontend
    if [[ -f "${FRONTEND_DIR}/package.json" ]]; then
        log_info "Ejecutando verificación de tipos y empaquetado frontend en ${FRONTEND_REL_DIR}..."
        if grep -q '"build"' "${FRONTEND_DIR}/package.json" 2>/dev/null; then
            (
                cd "${FRONTEND_DIR}" && \
                pnpm run build
            )
        elif [[ -x "${FRONTEND_DIR}/node_modules/.bin/tsc" ]]; then
            (
                cd "${FRONTEND_DIR}" && \
                "${FRONTEND_DIR}/node_modules/.bin/tsc" -b
            )
        fi
        log_success "Compilación de frontend completada sin errores."
    fi
fi

# ------------------------------------------------------------------------------
# 8. Cuadro Resumen Final y Comandos Rápidos
# ------------------------------------------------------------------------------
ACTIVE_DB_URL="N/A"
if [[ -f "$ENV_FILE" ]]; then
    ACTIVE_DB_URL="$(grep "^DATABASE_URL=" "$ENV_FILE" 2>/dev/null | head -n1 | cut -d= -f2- || echo "N/A")"
fi

TSC_VERSION="N/A"
[[ -x "${FRONTEND_DIR}/node_modules/.bin/tsc" ]] && TSC_VERSION="$("${FRONTEND_DIR}/node_modules/.bin/tsc" --version 2>/dev/null || echo "N/A")"

VITE_VERSION="N/A"
[[ -x "${FRONTEND_DIR}/node_modules/.bin/vite" ]] && VITE_VERSION="$("${FRONTEND_DIR}/node_modules/.bin/vite" --version 2>&1 | head -n1 || echo "N/A")"

echo ""
echo -e "${C_BOLD}${C_GREEN}==============================================================================${C_RESET}"
echo -e "${C_BOLD}${C_GREEN}  ¡Aprovisionamiento del Entorno Completado Exitosamente!                     ${C_RESET}"
echo -e "${C_BOLD}${C_GREEN}  Proyecto: ${PROJECT_TITLE}                                                  ${C_RESET}"
echo -e "${C_BOLD}${C_GREEN}==============================================================================${C_RESET}"
echo -e "  ${C_BOLD}Directorio Raíz :${C_RESET} ${ROOT_DIR}"
echo -e "  ${C_BOLD}Backend         :${C_RESET} ${BACKEND_REL_DIR} (${BACKEND_DIR})"
echo -e "  ${C_BOLD}Frontend        :${C_RESET} ${FRONTEND_REL_DIR} (${FRONTEND_DIR})"
echo -e "  ${C_BOLD}Python Base     :${C_RESET} ${PYTHON_BIN} (v${PY_VERSION_DETECTED})"
echo -e "  ${C_BOLD}Entorno Virtual :${C_RESET} ${CANONICAL_VENV}"
[[ -e "${BACKEND_VENV_LINK}" ]] && echo -e "  ${C_BOLD}Acceso Backend  :${C_RESET} ${BACKEND_VENV_LINK} -> $(readlink "${BACKEND_VENV_LINK}" 2>/dev/null || echo ".venv")"
echo -e "  ${C_BOLD}Base de Datos   :${C_RESET} ${ACTIVE_DB_URL}"
echo -e "  ${C_BOLD}Node.js         :${C_RESET} $(command -v node) (${NODE_VERSION_DETECTED})"
echo -e "  ${C_BOLD}pnpm            :${C_RESET} $(command -v pnpm) (v${PNPM_VERSION_DETECTED})"
echo -e "  ${C_BOLD}Frontend Tools  :${C_RESET} ${TSC_VERSION} / ${VITE_VERSION}"
echo -e "${C_BOLD}${C_GREEN}==============================================================================${C_RESET}"
echo -e "${C_BOLD}Comandos rápidos para desarrollo y ejecución:${C_RESET}"
echo -e "  ${C_CYAN}pnpm run dev${C_RESET}        Inicia los servicios en desarrollo (según scripts en package.json)."
echo -e "  ${C_CYAN}./setup.sh --start${C_RESET}  Verifica el entorno y levanta ambos servidores directamente."
echo -e "  ${C_CYAN}pnpm run dev:back${C_RESET}   Inicia únicamente el servidor backend."
echo -e "  ${C_CYAN}pnpm run dev:front${C_RESET}  Inicia únicamente el servidor frontend."
echo -e "  ${C_CYAN}pnpm run test:back${C_RESET}  Ejecuta la suite de pruebas backend."
echo -e "  ${C_CYAN}pnpm run stop${C_RESET}       Detiene procesos locales en puertos de desarrollo."
echo -e "${C_BOLD}${C_GREEN}==============================================================================${C_RESET}"
echo ""
if [[ "$START_SERVERS" == "true" ]]; then
    log_step "Iniciando servidores de desarrollo Full Stack (--start activo)..."
    export PATH="${CANONICAL_VENV}/bin:${PATH}"
    cd "${ROOT_DIR}"
    if [[ -f "${ROOT_DIR}/package.json" ]] && grep -q '"dev"' "${ROOT_DIR}/package.json" 2>/dev/null; then
        exec pnpm run dev
    else
        FRONTEND_CMD="pnpm --dir \"${FRONTEND_DIR}\" run dev"
        BACKEND_ENTRY="${FASTAPI_APP_MODULE//./\/}.py"
        BACKEND_CMD="cd \"${BACKEND_DIR}\" && (\"${VENV_PYTHON}\" -m fastapi dev \"${BACKEND_ENTRY}\" || \"${VENV_PYTHON}\" -m uvicorn \"${FASTAPI_APP_MODULE}:app\" --reload --port 8000)"
        exec npx --yes concurrently -k -n "FRONT,BACK" -c "bgGreen.bold,bgBlue.bold" "${FRONTEND_CMD}" "${BACKEND_CMD}"
    fi
fi
