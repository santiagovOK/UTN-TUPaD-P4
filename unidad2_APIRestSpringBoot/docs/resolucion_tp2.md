# Resolución TP2: API Rest Spring Boot

En este documento se detallará el proceso paso a paso de la resolución del Trabajo Práctico de la Unidad 2.

## 1. Migración del Proyecto Anterior (Unidad 1 - Fundamentos Spring Boot)

Dado que la estructura y la base de código que provenían del Trabajo Práctico de la Unidad 1 eran directamente útiles y compatibles para realizar el Trabajo Práctico de la Unidad 2, se tomó la decisión de copiar el proyecto tal cual estaba. 

Posteriormente, se llevó a cabo una refactorización integral del proyecto en la cual:
- Se renombraron los directorios fuente para reflejar la nueva unidad (`src/main/java/com/tpUnidad2/unidad2_APIRestSpringBoot`).
- Se actualizaron en bloque todos los nombres de los paquetes (`package`) y las sentencias de importación (`import`) a lo largo de todo el código.
- Se reconfiguraron los archivos de compilación (`build.gradle`, `settings.gradle`) y las configuraciones de entorno del IDE para que no queden vestigios del proyecto anterior.

## 2. Configuración de Swagger (OpenAPI)
Para poder documentar de forma interactiva nuestra API, se agregó al archivo `build.gradle` la dependencia correspondiente a Springdoc OpenAPI:
`implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:3.0.3'`. También se agregó `org.springframework.boot:spring-boot-starter-validation` para implementar validaciones (@NotBlanl, @NotNull, etc.).

## 3. Ajuste de Repositorios y Servicios (Búsqueda por Mail)
Para cumplir con las consignas, específicamente la búsqueda de un usuario por su correo electrónico, se extendió la capa de persistencia y lógica de negocio heredada de la Unidad 1:
- **`UsuarioRepository`**: Se agregó la firma `Optional<Usuario> findByMail(String mail);` delegando a Spring Data JPA la creación automática de la consulta a la base de datos.
- **`UsuarioService`**: Se definió el nuevo contrato `UsuarioDto findByMail(String mail);`.
- **`UsuarioServiceImp`**: Se implementó el método utilizando `.orElseThrow()` para arrojar una excepción (posteriormente manejada) en caso de que no exista el usuario, y transformando la entidad encontrada a un `UsuarioDto` antes de ser devuelta.

## 4. Desarrollo de la capa de Controladores (REST API)
Para exponer nuestra lógica de negocio, se creó el paquete `controllers` y las siguientes clases anotadas con `@RestController` y `@RequestMapping`:
- `CategoriaController` (`/api/categorias`)
- `ProductoController` (`/api/productos`)
- `PedidoController` (`/api/pedidos`)
- `UsuarioController` (`/api/usuarios`)

Todos incluyen métodos estándar (GET, POST, PUT, DELETE) y retornan estructuras `ResponseEntity` parametrizadas con sus DTOs específicos (por ejemplo, `ResponseEntity<CategoriaDto>`), haciendo uso de las constantes de `HttpStatus` (`HttpStatus.OK`, `HttpStatus.CREATED`, `HttpStatus.NO_CONTENT`) para definir los códigos de estado.
Además, se incorporó la anotación `@Valid` junto a los parámetros `@RequestBody` (en métodos POST y PUT) para ejecutar automáticamente las validaciones de entrada configuradas en los DTOs.
En particular, para cumplir con las consignas, en `UsuarioController` se añadieron las sentencias `System.out.println` en los métodos de búsqueda (por ID y por el nuevo endpoint `/search?mail=...`) para garantizar que la información se imprima por consola al ser solicitada.

## 5. Manejo Global de Excepciones (AdviceController)
Para lograr una API robusta y evitar que las excepciones internas de Java rompan la respuesta JSON, se creó `AdviceController` decorado con `@RestControllerAdvice`.
Este controlador intercepta globalmente:
- `NullPointerException`: Utilizada para cuando nuestros servicios no encuentran un recurso (retorna `404 Not Found`).
- `MethodArgumentNotValidException` e `IllegalArgumentException`: Utilizadas para capturar errores de validación de los DTOs y peticiones inválidas (retornan `400 Bad Request`).
- `Exception`: Captura errores genéricos o imprevistos (retorna `500 Internal Server Error`).

---


## Estructura de Archivos Planificada

A continuación se detalla cómo quedará la estructura del proyecto en `src/main/java/com/tpUnidad2/unidad2_APIRestSpringBoot/` para cumplir con todas las consignas. Se señalan específicamente los archivos que **aún no existen** y deben crearse.

```text
unidad2_APIRestSpringBoot/
├── config/
├── controllers/                       (NUEVO - A CREAR)
│   ├── AdviceController.java          (NUEVO - A CREAR)
│   ├── CategoriaController.java       (NUEVO - A CREAR)
│   ├── PedidoController.java          (NUEVO - A CREAR)
│   ├── ProductoController.java        (NUEVO - A CREAR)
│   └── UsuarioController.java         (NUEVO - A CREAR)
├── dtos/
├── entities/
├── enums/
├── interfaces/
├── repository/
├── service/
└── Unidad2APIRestSpringBootApplication.java
```