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
