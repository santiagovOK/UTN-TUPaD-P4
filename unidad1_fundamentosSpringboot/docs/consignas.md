# PROGRAMACIÓN IIITrabajo Práctico - Fundamentos de SpringOBJETIVO GENERAL

Desarrollar un Sistema de Gestión de Pedidos que demuestre tu comprensión de la arquitectura Spring Boot y las buenas prácticas de desarrollo.

# MARCO TEÓRICO

|     |     |
| --- | --- |
| **Concepto** | **Aplicación en el proyecto** |
| Application Context | Contenedor de IoC que gestiona el ciclo de vida de los beans y sus dependencias. |
| Beans | Objetos gestionados por Spring que representan componentes de la aplicación. |
| Inyección de Dependencias | Permite desacoplar componentes mediante la inyección automática de dependencias, preferentemente por constructor. |
| Estereotipos | Anotaciones especializadas (@Service, @Repository, @Component) que definen el rol de cada clase en la arquitectura. |

**Caso Práctico**

Dado el siguiente UML:

Continuando con las clases generadas en la Practica de “JPA” deberá:

1.  Crear un proyecto en Spring Initializr con las siguientes dependencias
    1.  Spring Web
    2.  Spring Data Jpa
    3.  Lombok
    4.  H2 Database
    5.  Spring Boot Dev Tools
2.  Desarrollar capa de DTOs

│

├── categoria

│ ├── CategoriaCreate.java

│ ├── CategoriaDto.java

│ └── CategoriaEdit.java

│

├── detallePedido

│ ├── DetallePedidoCreate.java

│ └── DetallePedidoDto.java

│

├── pedido

│ ├── PedidoDto.java

│ └── PedidoEdit.java

│

├── producto

│ ├── ProductoCreate.java

│ ├── ProductoDto.java

│ └── ProductoEdit.java

│

└── usuario

├── UsuarioCreate.java

├── UsuarioDto.java

└── UsuarioEdit.java

1.  Instanciar a partir de DTOs:
    1.  2 Usuarios
    2.  3 Pedidos (al menos 2 detalles pedido por cada uno)
    3.  3 Categorías
    4.  10 productos

# CONCLUSIONES ESPERADAS

- Aplicar inyección de dependencias por constructor
- Usar estereotipos según la responsabilidad de cada clase
- Configurar aplicaciones con properties