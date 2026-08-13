# Trabajo Práctico - Unidad 2 (Java -  )

Cree un archivo Markdown para la resolución de cada una de las consignas (principalmente para guiarme yo y poder revisar los cambios unidad por unidad en el proyecto.). Pueden verlo aquí: [docs/resolucion_tp2.md](docs/resolucion_tp1.md)

---

**Aclaración Importante**: Ya había realizado este mismo trabajo práctico durante la cursada de Programación 3, primer cuatrimestre 2026. Al mismo tiempo que lo entregué [unos meses atrás](https://github.com/santiagovOK/UTN-TUPaD-P3/tree/main/unidad9_fundamentosSpringboot), bloquearon esas unidades para dejarlas libres por si nosotros llegábamos y queríamos estudiarlas. Finalmente el trabajo no fue corregido en aquel entonces.

Lo que hice fue revisar nuevamente este trabajo, aunque en aquel entonces lo consideraba entregable y acorde a la resolución de las consignas (suficiente para esta instancia, aunque arreglé algunos errores menores). Creo que debe ser considerado que estuve al día con la materia en aquel momento y, por lo tanto, que me permitan considerar esto como un repaso para hacer más énfasis en los nuevos temas de esta asignatura y las del resto.

---

✨ Estudiante

- Nombre: Varela, Santiago Octavio
- Email institucional: santiago.varela@tupad.utn.edu.ar

Repositorio donde podrán encontrar mis trabajos de Programación IV: https://github.com/santiagovOK/UTN-TUPaD-P4

---

> **Nota:** Este proyecto está configurado en su `build.gradle` para compilar utilizando **Java 25**.

### Base de Datos H2

La base de datos H2 está configurada para levantarse y correr en memoria. Para visualizar las tablas y los datos que se cargan automáticamente desde DataInitializer:
1. Es requisito indispensable que el proyecto de Spring Boot se encuentre **en ejecución**.
2. Una vez que la aplicación esté corriendo, ingresa a la siguiente ruta desde tu navegador: `http://localhost:8080/h2-console`
3. En la interfaz de login, hay que colocar en **JDBC URL** el valor: `jdbc:h2:mem:jpa_db`
4. User Name: `sa` (dejar el password en blanco) y hacer clic en Connect.

> **Aclaración sobre la configuración:** 
> La configuración de la base de datos se encuentra escrita de manera explícita en el archivo `application.properties`. **El no uso de variables de entorno (como archivos `.env`) es totalmente adrede, con el conocimiento de que no se recomienda en producción.** Se decidió seguir utilizando una configuración estática muy similar a la que se venía manejando en el **TP Nº8 sobre JPA** del cuatrimestre anterior (Programación 3, pueden verlo [aquí](https://github.com/santiagovOK/UTN-TUPaD-P3/tree/main/unidad8_jpa)), esto con el objetivo de no sobrecomplicar el proyecto ni añadir capas extra de abstracción a este ejercicio de práctica de los fundamentos de Spring Boot.
