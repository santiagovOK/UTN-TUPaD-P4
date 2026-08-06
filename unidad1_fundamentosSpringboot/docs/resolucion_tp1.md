# Resolución TP1: Fundamentos de Spring Boot

En este documento se detallará el proceso paso a paso de la resolución del Trabajo Práctico de la Unidad 1.

## 1. Migración del Proyecto Anterior (Unidad 8 - JPA - Programación 3)
Dado que las anotaciones de Hibernate y la estructura de las entidades son compatibles con Spring Data JPA, se procedió a reciclar el modelo de dominio del trabajo anterior, que ya contaba con un análisis del UML y una implementación funcional.

Se importaron al nuevo proyecto de Spring Boot los siguientes paquetes:
- **`entities`**: `Base`, `Usuario`, `Pedido`, `DetallePedido`, `Producto`, `Categoria`.
- **`enums`**: `Rol`, `Estado`, `FormaPago`.
- **`interfaces`**: `Calculable`.

*(Los repositorios manuales y archivos como `persistence.xml` y `Main.java` fueron descartados, ya que Spring Boot gestiona el contexto de persistencia a través de `application.properties` y las interfaces de `JpaRepository`).*

## 2. Configuración y Corrección de Packages
Al migrar los archivos, se actualizaron todas las declaraciones de `package` y las importaciones (`import`) en las clases Java para reflejar la estructura de directorios del nuevo proyecto: `com.tpUnidad1.unidad1_fundamentosSpringboot`. Esto solucionó los errores de sintaxis del IDE y dejó la base lista para trabajar en la nueva arquitectura.

## 3. Creación de la capa DTO (Data Transfer Object)
Siguiendo las buenas prácticas y las consignas del trabajo práctico, se comenzó a estructurar la capa DTO para separar el modelo de base de datos de los datos expuestos en la API. Se utilizó la característica nativa `record` de Java por su inmutabilidad y concisión.

### 3.1. DTOs de Categoría
Se desarrollaron tres DTOs específicos para gestionar de forma segura los datos de la entidad `Categoria` según el tipo de operación:
- **`CategoriaCreate`**: Se encarga de la creación. Incluye únicamente `nombre` y `descripcion`. En su método `toEntity()`, utiliza el patrón Builder provisto por Lombok (`Categoria.builder()`) para instanciar la entidad de forma segura sin requerir constructores complejos.
- **`CategoriaDto`**: Se encarga de la lectura (lo que se expone al cliente). Contiene el `id`, el `nombre` y la `descripcion`. Utiliza un método estático `toDto()` que interactúa con los getters de la entidad generados por Lombok.
- **`CategoriaEdit`**: Se encarga de la edición. Su método `applyTo(Categoria)` verifica que los datos ingresados no sean nulos antes de modificar la entidad original, evitando borrar información por accidente durante actualizaciones parciales.

### 3.2. DTOs de Producto
Se implementó la misma arquitectura de DTOs para la entidad `Producto`, abordando en este caso el manejo de tipos de datos y relaciones de forma segura:
- **Relaciones por ID**: Para vincular un producto a una categoría, los DTOs (`ProductoCreate` y `ProductoEdit`) solicitan únicamente el identificador (`Long idCategoria`) en lugar de recibir un objeto anidado. Posteriormente, la lógica de negocio (Servicio) es la encargada de buscar la `Categoria` real e inyectarla en la entidad, manteniendo el payload de la API limpio y eficiente.
- **Uso de Clases Envoltorias (Wrappers - Esto tuvo un poco más de investigación)**: En el `ProductoEdit`, se reemplazaron los tipos primitivos (`int stock`, `boolean disponible`) por sus respectivas clases envoltorias (`Integer`, `Boolean`). Esta práctica es indispensable para operaciones de actualización parcial (PATCH), ya que un tipo primitivo nunca puede ser `null`, lo que causaría la sobreescritura accidental de datos si el cliente no los envía. Al usar Wrappers, se pueden validar los nulos (`if (this.stock != null)`) e ignorar los atributos que no requieren cambios.

### 3.3. DTOs de Usuario
Se estructuraron los DTOs (`UsuarioCreate`, `UsuarioDto`, `UsuarioEdit`) como `record` para aprovechar su inmutabilidad. En el `UsuarioDto` se agregó explícitamente el campo `id` necesario para la identificación en el cliente, y se excluyeron datos sensibles como la contraseña y el rol por seguridad. También se centralizó la lógica de conversión en el método estático `toDto()` y se implementó el patrón Builder de Lombok en `toEntity()` para construir la entidad de forma segura.

### 3.4. DTOs de Pedido
Para la entidad `Pedido`, el `PedidoDto` incluye los datos principales y se encarga de transformar su lista interna de `DetallePedido` a una lista de `DetallePedidoDto` usando *Streams*. Por su parte, el `PedidoEdit` se diseñó restringido para permitir únicamente la modificación del `estado` y la `formaPago`, protegiendo así el resto de la información inmutable del pedido.

### 3.5. DTOs de DetallePedido
El `DetallePedidoDto` expone la `cantidad`, el nombre del producto asociado y el `subtotal` (que es un valor calculado). Al igual que en la arquitectura de productos, el `DetallePedidoCreate` únicamente solicita la cantidad y el identificador referencial (`idProducto`), delegando la búsqueda de la entidad Producto real a la futura capa de Servicios.


## 4. Creación de la capa de Repositorios
Para cumplir con las "Conclusiones Esperadas" respecto al uso de estereotipos y proveer la persistencia de datos mediante Spring Data JPA, se crearon las interfaces de Repositorios para cada una de las entidades:
- `CategoriaRepository`
- `ProductoRepository`
- `UsuarioRepository`
- `PedidoRepository`
- `DetallePedidoRepository`

Todas estas interfaces extienden de `JpaRepository<Entidad, Long>`, delegando a Spring la generación de los métodos CRUD y la ejecución de consultas a la base de datos H2. Adicionalmente, fueron decoradas explícitamente con la anotación `@Repository` para denotar su rol en la arquitectura y cumplir con las consignas del Trabajo Práctico.

## 5. Creación de la capa de Servicios
Continuando con la arquitectura en capas y para cumplir con la consigna de Inyección de Dependencias, se comenzó a implementar la lógica de negocio mediante clases anotadas con `@Service`.

### 5.1. Servicio de Categorías
Se definió la interfaz `CategoriaService` para establecer el contrato de operaciones interactuando puramente con DTOs (`CategoriaCreate`, `CategoriaDto`, `CategoriaEdit`), aislando así las Entidades del exterior.
En su implementación, `CategoriaServiceImpl`, se inyectó el `CategoriaRepository` mediante constructor y se desarrollaron las siguientes lógicas:
- **Guardado (`save`)**: Conversión del DTO de creación a Entidad usando su método `.toEntity()`, persistencia en base de datos y retorno de un `CategoriaDto`.
- **Búsquedas (`findById` y `findAll`)**: Uso de `orElseThrow` para manejar entidades no encontradas de forma elegante, y uso de *Streams* de Java para mapear listas enteras de entidades a sus respectivos DTOs.
- **Actualización (`update`)**: Se busca la entidad original, se le aplican los cambios parciales con el método `.applyTo()` del DTO de edición, y se vuelve a persistir.
- **Baja Lógica (`deleteById`)**: En lugar de hacer un borrado físico destructivo, se aprovechó la propiedad `eliminado` heredada de la clase `Base` (migrada del trabajo práctico de JPA) para realizar un *soft delete*, cambiando el estado a `true` y conservando el historial en la base de datos.

### 5.2. Servicio de Productos
Siguiendo la misma estructura arquitectónica, se implementaron `ProductoService` y su respectiva implementación `ProductoServiceImp` (anotada con `@Service`). En este servicio se destaca el manejo de la relación entre entidades:
- **Asignación de Relaciones**: Al crear (`save`) o editar (`update`) un producto, los DTOs proporcionan únicamente el referencial `idCategoria`. Es responsabilidad exclusiva de la lógica de negocio del servicio utilizar el `CategoriaRepository` inyectado para buscar la entidad `Categoria` real en la base de datos y asociarla al Producto antes de persistirlo.
- Se replicaron también las buenas prácticas de manejo de excepciones con `orElseThrow`, transformación de colecciones mediante *Streams*, la inyección de dependencias por constructor, y el borrado seguro con baja lógica en el método `deleteById`.

### 5.3. Servicio de Usuarios
De manera similar a los servicios anteriores, se creó la interfaz `UsuarioService` y su implementación `UsuarioServiceImp` para gestionar las operaciones CRUD de los usuarios. La lógica se mantiene coherente con el resto de la aplicación, inyectando el `UsuarioRepository`, transformando los datos entre Entidades y sus correspondientes DTOs (`UsuarioCreate`, `UsuarioEdit`, `UsuarioDto`), y garantizando que no se expongan datos críticos hacia la capa exterior, a la vez que se implementa la eliminación mediante la baja lógica heredada de la clase `Base`.

### 5.4. Servicio de Pedidos y Detalles
Para la gestión de órdenes de compra, se elaboró `PedidoService` y `PedidoServiceImp`. En este punto se debió abordar el modelo estructurado de la relación `Pedido` - `DetallePedido`.
Se tomó la decisión arquitectónica de **no crear un servicio independiente para los Detalles del Pedido**, delegando el ciclo de vida completo de estos al `PedidoService`. La relación y creación se da del siguiente modo:
- **Agrupación en el DTO:** Al momento de la creación, el servicio recibe un `PedidoCreate` (creado para suplir la necesidad) que ya contiene la lista de `DetallePedidoCreate`.
- **Inyección y Búsqueda:** Dentro del método de guardado, el `PedidoService` itera sobre estos detalles utilizando el `ProductoRepository` inyectado para validar y recuperar cada `Producto` original de la base de datos.
- **Relación Bidireccional Interna:** Una vez verificado el producto, se hace uso del método `.addDetallePedido(cantidad, producto)` que reside internamente en la entidad `Pedido`. Dicho método encapsula la creación de la entidad `DetallePedido`, asignándole `this` (el propio pedido) para conformar la relación bidireccional correctamente y de manera segura.
- **Persistencia en Cascada:** Al encontrarse la relación de detalles anotada con `@OneToMany(cascade = CascadeType.ALL)`, el simple guardado del pedido al final del flujo (`pedidoRepository.save(pedido)`) instruye a Hibernate/JPA para que detecte las nuevas instancias de `DetallePedido` y las persista automáticamente en la base de datos de una sola vez, sin la necesidad de emplear explícitamente un `DetallePedidoRepository` o un servicio externo, manteniendo así la alta cohesión del diseño orientado a objetos.

## 6. Configuración de Base de Datos H2
Para cumplir con la consigna de configurar la aplicación mediante *properties*, se modificó el archivo `application.properties`. Se replicaron las configuraciones que originalmente se encontraban en el `persistence.xml` del proyecto anterior (Unidad 8 - Programación 3). Específicamente, se configuró una conexión JDBC hacia una base de datos H2 levantada en memoria (`jdbc:h2:mem:jpa_db`), utilizando las mismas credenciales originales. Además, se habilitó la visualización de la consola web de H2 y se instruyó a Hibernate mediante `ddl-auto=update` para que construya y actualice el esquema de tablas de manera automática.

## 7. Inicialización de Datos (BD)
Para finalizar el trabajo práctico, era necesario instanciar una serie de registros (2 Usuarios, 3 Categorías, 10 Productos, 3 Pedidos con al menos 2 detalles cada uno) partiendo desde los DTOs de creación a través de los servicios.

Para lograr esto, **se tomó una decisión de diseño apegada a los materiales teóricos de la cursada**: en lugar de utilizar una interfaz `CommandLineRunner` en la clase principal (que es una alternativa genérica frecuente pero que no fue cubierta explícitamente en los apuntes), se decidió separar responsabilidades creando una clase dedicada llamada `DataInitializer`.
- **Uso de `@Component`:** La clase fue decorada con este estereotipo para que el contenedor de IoC de Spring la detecte y gestione su ciclo de vida automáticamente de forma independiente.
- **Inyección por Constructor:** Se inyectaron todos los servicios requeridos (`UsuarioService`, `CategoriaService`, `ProductoService`, `PedidoService`) mediante el constructor de la clase, acatando con firmeza las buenas prácticas y conclusiones esperadas del Trabajo Práctico.
- **Uso de `@PostConstruct`:** Todo el código de instanciación fue encapsulado dentro de un método anotado con `@PostConstruct`. Según el marco teórico de la cursada, esta es la forma ideal de ejecutar lógica de inicialización, ya que Spring asegura que el método se ejecute de manera automática exactamente después de crear el Bean y resolver sus dependencias, logrando el mismo resultado pero con una arquitectura más limpia y desacoplada.


## 8. Corrección del Timestamp de Creación (`createdAt`)
Durante el desarrollo se detectó que el campo `createdAt` heredado de la clase abstracta `Base` persistía como `null` en la base de datos al momento de crear nuevas entidades.

Para solucionarlo de forma delegada al ORM, se modificó la entidad `Base`:
- Se incorporó la anotación `@CreationTimestamp` de Hibernate, la cual se encarga de asignar automáticamente la marca de tiempo actual (timestamp) justo antes de realizar el `INSERT` en la base de datos.
- Se agregó la anotación `@Column(updatable = false)` de JPA para proteger el campo, garantizando que el timestamp de creación sea inmutable y no pueda ser alterado accidentalmente durante posteriores consultas `UPDATE`.

Este enfoque garantiza que todas las entidades que extienden de `Base` conserven un registro cronológico veraz y automático de su creación.