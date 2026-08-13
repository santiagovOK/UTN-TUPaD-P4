# PROGRAMACIÓN IV

**Trabajo Práctico - Api Rest**

## OBJETIVO GENERAL

Desarrollar una API REST completa y profesional para la gestión de productos, aplicando arquitectura en capas, validaciones, manejo de errores, persistencia con Spring Data JPA y documentación con Swagger.

## MARCO TEÓRICO

|     |     |
| --- | --- |
| **Concepto** | **Aplicación en el proyecto** |
| API REST | Interfaz para comunicación entre sistemas mediante HTTP, siguiendo los principios REST (stateless, recursos, métodos HTTP). |
| Métodos HTTP | GET (leer), POST (crear), PUT (actualizar completo), PATCH (actualizar parcial), DELETE (eliminar). |
| Manejo de Excepciones | Control centralizado de errores mediante @ControllerAdvice para respuestas consistentes. |
| Swagger/OpenAPI | Documentación interactiva y automática de APIs REST. |

## Caso Práctico

Dado el siguiente UML:

Continuando con las clases generadas en la Practica de “JPA” deberá:

1.  Agregar dependencia de Swagger

implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0'

1.  Desarrollar capa Repository
2.  Desarrollar capa Service
3.  Desarrollar capa de Controller y AdviceController
4.  Crear y persistir a partir de DTOs utilizando Postman:
    1.  2 Usuarios
    2.  3 Pedidos (al menos 2 detalles pedido por cada uno)
    3.  3 Categorías
    4.  10 productos

1.  Actualizar 1 categoria
2.  Buscar Usuarios por id y mostrar información por consola
3.  Buscar Usuarios por mail y mostrar por consola
4.  Mostrar Swagger funcionando

## CONCLUSIONES ESPERADAS

- Diseñar y construir una API REST completa desde cero
- Aplicar correctamente todos los métodos HTTP según su propósito
- Implementar arquitectura en capas profesional