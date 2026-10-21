"""
Base heredada del TP7; identidad y documentación adaptadas al TP8.
[Arquitectura Backend & Validación con Pydantic]:
Validación temprana de cadenas no vacías para schemas de entrada antes de invocar la capa de servicio.

[Diagrama UML - Entidad PRODUCTO]:
Garantiza la restricción {NN} (Not Null / no vacío) sobre el atributo nombre : VARCHAR(150) {NN}.

Este módulo es importado por schemas.py (validación temprana, antes del service).
No importa el estado de la BD ni los services.
"""


def validate_producto_nombres(value: str) -> str:
    """Validador pequeño y enfocado: nombre sin espacios en blanco.

    Regla de negocio (RN-06): el nombre no debe contener
    solo caracteres de espacio en blanco (espacio, tabulación, salto de línea).
    Valida antes de cualquier operación de escritura para fallar rápido
    con un error 422 descriptivo y localizado.

    Excepciones que lanza: ValueError con mensaje claro si el nombre
    falla la validación; Pydantic lo capturará y traducirá a HTTP 422.

    Parámetros:
        value (str): Valor del nombre a validar.

    Retorna:
        str: El valor sanitizado (sin espacios al inicio o final).

    Excepciones:
        ValueError: Si el nombre está vacío o contiene solo espacios en blanco.
    """
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("El nombre no puede estar vacío o contener solo espacios.")
    return cleaned
