# Pruebas y Ejecución de la API (Postman y Swagger)

Partiendo de los registros creados con [DataInitializer](), se ejecutaron paso a paso las operaciones solicitadas en las consignas.


## 1. Creación de Usuarios (POST /api/usuarios)

### Estado inicial: 2 usuarios en la base de datos

| ID | Nombre | Apellido | Mail | Celular |
|----|--------|----------|------|---------|
| 1 | Juan | Pérez | juan@mail.com | 123456789 |
| 2 | María | Gómez | maria@mail.com | 987654321 |

---

### Paso 1: Crear usuario #3

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/usuarios` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Carlos",
  "apellido": "López",
  "mail": "carlos@mail.com",
  "celular": "1112345678",
  "password": "contraseña123",
  "rol": "ADMIN"
}
```

Imagen con el usuario Nº1 creado:

![Imagen con el usuario Nº1 creado](docs/images/primer_usuario.png)


---

### Paso 2: Crear usuario #4

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/usuarios` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Ana",
  "apellido": "Martínez",
  "mail": "ana@mail.com",
  "celular": "912345678",
  "password": "contraseña123",
  "rol": "USUARIO"
}
```

Imagen con el usuario Nº2 creado:

![Imagen con el usuario Nº2 creado](docs/images/segundo_usuario.png)

## 2. Creación de Pedidos (POST /api/pedidos)

### Estado inicial: 3 pedidos en la base de datos

---

### Paso 1: Crear Pedido (con detalles de pedido) #1

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/pedidos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "estado": "PENDIENTE",
  "formaPago": "TARJETA",
  "detalles": [
    {
      "cantidad": 1,
      "idProducto": 1
    },
    {
      "cantidad": 2,
      "idProducto": 4
    }
  ]
}
```

**Descripción:** Pedido con 1 TV 50' (producto ID 1) y 2 Mouse (producto ID 4). Estado: PENDIENTE. Forma de pago: TARJETA.

Imagen con el pedido Nº1 creado:

![Imagen con el pedido Nº1 creado](docs/images/primer_pedido.png)


---

### Paso 2: Crear Pedido (con detalles de pedido) #2

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/pedidos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "estado": "CONFIRMADO",
  "formaPago": "TRANSFERENCIA",
  "detalles": [
    {
      "cantidad": 1,
      "idProducto": 5
    },
    {
      "cantidad": 3,
      "idProducto": 7
    }
  ]
}
```

**Descripción:** Pedido con 1 Mesa (producto ID 5) y 3 Lámparas (producto ID 7). Estado: CONFIRMADO. Forma de pago: TRANSFERENCIA.

Imagen con el pedido Nº2 creado:

![Imagen con el pedido Nº2 creado](docs/images/segundo_pedido.png)


---

### Paso 3: Crear Pedido  (con detalles de pedido)  #3

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/pedidos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "estado": "TERMINADO",
  "formaPago": "EFECTIVO",
  "detalles": [
    {
      "cantidad": 1,
      "idProducto": 3
    },
    {
      "cantidad": 1,
      "idProducto": 8
    },
    {
      "cantidad": 1,
      "idProducto": 9
    }
  ]
}
```

**Descripción:** Pedido con 1 Notebook (producto ID 3), 1 Pelota (producto ID 8) y 1 Raqueta (producto ID 9). Estado: TERMINADO. Forma de pago: EFECTIVO.

Imagen con el pedido Nº3 creado:

![Imagen con el pedido Nº3 creado](docs/images/tercer_pedido.png)


---

### Estado final: 5 pedidos en la base de datos

---

## 3. Creación de Categorías (POST /api/categorias)

### Estado inicial: 3 categorías en la base de datos

| ID | Nombre | Descripción |
|----|--------|-------------|
| 1 | Electrónica | Aparatos electrónicos |
| 2 | Hogar | Elementos para el hogar |
| 3 | Deportes | Artículos deportivos |

---

### Paso 1: Crear categoría #4

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/categorias` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Oficina",
  "descripcion": "Suministros y mobiliario de oficina"
}
```

Imagen con la categoría Nº1 creada:

![Imagen con la categoría Nº1 creada](docs/images/primer_categoria.png)


---

### Paso 2: Crear categoría #5

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/categorias` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Jardin",
  "descripcion": "Artículos para jardinería"
}
```

Imagen con la categoría Nº2 creada:

![Imagen con la categoría Nº2 creada](docs/images/segunda_categoria.png)


---

### Paso 3: Crear categoría #6

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/categorias` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Libros",
  "descripcion": "Libros de diversas categorías"
}
```

Imagen con la categoría Nº3 creada:

![Imagen con la categoría Nº3 creada](docs/images/tercer_categoria.png)


---

### Estado final: 6 categorías en la base de datos

---

## 4. Creación de Productos (POST /api/productos)

### Estado inicial: 10 productos en la base de datos

| ID | Nombre | Precio | Stock | Categoría |
|----|--------|--------|-------|-----------|
| 1 | TV 50' | $500,000 | 10 | Electrónica (1) |
| 2 | Radio | $30,000 | 20 | Electrónica (1) |
| 3 | Notebook | $800,000 | 5 | Electrónica (1) |
| 4 | Mouse | $20,000 | 50 | Electrónica (1) |
| 5 | Mesa | $120,000 | 5 | Hogar (2) |
| 6 | Silla | $30,000 | 20 | Hogar (2) |
| 7 | Lámpara | $30,000 | 15 | Hogar (2) |
| 8 | Pelota | $25,000 | 30 | Deportes (3) |
| 9 | Raqueta | $80,000 | 10 | Deportes (3) |
| 10 | Bicicleta | $300,000 | 5 | Deportes (3) |

---

### Paso 1: Crear Producto #11 (Electrónica)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Smartphone",
  "precio": 450000,
  "descripcion": "Smartphone Android 128GB",
  "stock": 25,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 1
}
```

Imagen con el producto Nº1 creado (así fue con los 9 siguientes):

![Imagen con el producto Nº1 creado](docs/images/primer_producto.png)


---

### Paso 2: Crear Producto #12 (Electrónica)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Tablet",
  "precio": 300000,
  "descripcion": "Tablet 10 pulgadas 64GB",
  "stock": 15,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 1
}
```

---

### Paso 3: Crear Producto #13 (Electrónica)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Auriculares",
  "precio": 80000,
  "descripcion": "Auriculares Bluetooth noise cancelling",
  "stock": 40,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 1
}
```

---

### Paso 4: Crear Producto #14 (Hogar)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Almohadón",
  "precio": 15000,
  "descripcion": "Almohadón decorativo de algodón",
  "stock": 30,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 2
}
```

---

### Paso 5: Crear Producto #15 (Hogar)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Maceta",
  "precio": 20000,
  "descripcion": "Maceta cerámica de 20cm",
  "stock": 25,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 2
}
```


---

### Paso 6: Crear Producto #16 (Hogar)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Cortina",
  "precio": 45000,
  "descripcion": "Cortina para ventana",
  "stock": 10,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 2
}
```

---

### Paso 7: Crear Producto #17 (Deportes)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Botas",
  "precio": 150000,
  "descripcion": "Botas de senderismo impermeables",
  "stock": 8,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 3
}
```

---

### Paso 8: Crear Producto #18 (Deportes)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Botas",
  "precio": 150000,
  "descripcion": "Botas de senderismo impermeables",
  "stock": 8,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 3
}
```

---

### Paso 9: Crear Producto #19 (Deportes)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Gorra",
  "precio": 12000,
  "descripcion": "Gorra deportiva ajustable",
  "stock": 50,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 3
}
```

---

### Paso 10: Crear Producto #20 (Jardín)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | POST |
| **URL completa** | `http://localhost:8080/api/productos` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Regadera",
  "precio": 18000,
  "descripcion": "Regadera de plástico 5L",
  "stock": 20,
  "imagen": "url",
  "disponible": true,
  "idCategoria": 4
}
```

---

### Estado final: 20 productos en la base de datos

**Creé uno repetido, luego me di cuenta. A fines prácticos se comprende.**

![Imagen 20 Productos](docs/images/todos_producto.png)


---

## 5. Actualización de Categoría (PUT /api/categorias/{id})

### Estado antes de la actualización:

| ID | Nombre | Descripción |
|----|--------|-------------|
| 1 | Electrónica | Aparatos electrónicos |
| 2 | Hogar | Elementos para el hogar |
| 3 | Deportes | Artículos deportivos |
| 4 | Jardin | Artículos para jardinería |
| 5 | Oficina | Suministros y mobiliario de oficina |
| 6 | Libros | Libros de diversas categorías |

---

### Actualizar Categoría #1 (Electrónica)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | PUT |
| **URL completa** | `http://localhost:8080/api/categorias/1` |
| **Content-Type** | application/json |

**Body (JSON):**
```json
{
  "nombre": "Electrónica y Tecnología",
  "descripcion": "Dispositivos electrónicos, gadgets y tecnología"
}
```

Imagen con la categoría actualizada:

![Imagen con la categoría actualizada](docs/images/categoria_actualizada.png)


---

### Estado después de la actualización:

| ID | Nombre | Descripción |
|----|--------|-------------|
| 1 | **Electrónica y Tecnología** | **Dispositivos electrónicos, gadgets y tecnología** |
| 2 | Hogar | Elementos para el hogar |
| 3 | Deportes | Artículos deportivos |
| 4 | Jardin | Artículos para jardinería |
| 5 | Oficina | Suministros y mobiliario de oficina |
| 6 | Libros | Libros de diversas categorías |

---

## 6. Buscar Usuario por ID (GET /api/usuarios/{id})

### Endpoint: GET /api/usuarios/{id}

**Nota:** No se devuelve el campo `password` ni `rol` (no están en el DTO).

---

### Buscar Usuario #1 (Juan Pérez)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | GET |
| **URL completa** | `http://localhost:8080/api/usuarios/1` |

**Resultado esperado:** Status **200 OK** con el usuario encontrado.

**Salida por consola (System.out.println en el controlador):**
```
Usuario encontrado con id: 1
```

**Respuesta JSON:**
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "mail": "juan@mail.com",
  "celular": "123456789"
}
```

Imagen con el usuario buscado por ID:

![Imagen con el usuario buscado por ID](docs/images/buscar_usuario_por_id.png)


---

### Buscar Usuario #2 (María Gómez)

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | GET |
| **URL completa** | `http://localhost:8080/api/usuarios/2` |

**Resultado esperado:** Status **200 OK** con el usuario encontrado.

**Salida por consola (System.out.println en el controlador):**
```
Usuario encontrado con id: 2
```

**Respuesta JSON:**
```json
{
  "id": 2,
  "nombre": "María",
  "apellido": "Gómez",
  "mail": "maria@mail.com",
  "celular": "987654321"
}
```

Imagen con el usuario buscado por ID:

![Imagen con el usuario buscado por ID](docs/images/buscar_usuario_por_id_2.png)

---

## 7. Buscar Usuario por Mail (GET /api/usuarios/search?mail={mail})

### Endpoint: GET /api/usuarios/search?mail={mail}

**Nota:** El parámetro `mail` se pasa como query parameter en la URL. No se devuelve el campo `password` ni `rol`.

---

### Buscar Usuario por mail "juan@mail.com"

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | GET |
| **URL completa** | `http://localhost:8080/api/usuarios/search?mail=juan@mail.com` |

**Resultado esperado:** Status **200 OK** con el usuario encontrado.

**Salida por consola (System.out.println en el controlador):**
```
Usuario encontrado con mail: juan@mail.com
```

**Respuesta JSON:**
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "mail": "juan@mail.com",
  "celular": "123456789"
}
```

Imagen con el usuario buscado por mail:

![Imagen con el usuario buscado por mail](docs/images/buscar_usuario_por_mail.png)


---

### Buscar Usuario por mail "maria@mail.com"

| Campo | Valor |
|-------|-------|
| **Base URL** | `http://localhost:8080` |
| **Método** | GET |
| **URL completa** | `http://localhost:8080/api/usuarios/search?mail=maria@mail.com` |

**Salida por consola (System.out.println en el controlador):**
```
Usuario encontrado con mail: maria@mail.com
```

**Respuesta JSON:**
```json
{
  "id": 2,
  "nombre": "María",
  "apellido": "Gómez",
  "mail": "maria@mail.com",
  "celular": "987654321"
}
```

Imagen con el usuario buscado por mail:

![Imagen con el usuario buscado por mail](docs/images/buscar_usuario_por_mail_2.png)

## 8. Mostrar Swagger funcionando

Imagen de Swagger funcionando en [localhost:8080]([http://localhost:8080](http://localhost:8080/swagger-ui/index.html)):

![Imagen Swagger funcionando](docs/images/swagger.png)
