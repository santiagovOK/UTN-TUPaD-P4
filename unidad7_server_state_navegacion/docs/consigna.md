Desarrollar una aplicación Full Stack conectando un frontend React + TypeScript con un backend FastAPI.

El estudiante implementará el CRUD completo de Categorías desde la interfaz de usuario, integrando el backend mediante TanStack Query. Los CRUDS de Producto y ProductoCategoria serán construidos en el backend.

📥 Modalidad de Entrega
Proyecto dividido en dos partes:
Proyecto Frontend comprimido en un archivo .zip
Proyecto Backend comprimido en un archivo .zip
El proyecto frontend debe demostrar:
Integración Full Stack: El frontend React consume la API FastAPI mediante TanStack Query (useQuery / useMutation), con invalidación de la caché luego de cada operación.
El CRUD de Categorías funciona de extremo a extremo.
Tipado TypeScript: Interfaces Categoria y Producto definidas. Props tipados en todos los componentes.tsx.
El proyecto backend debe demostrar:
Backend REST documentado: Endpoints de Producto y Producto Categoria funcionando y demostrados.
CORS configurado: El backend permite peticiones desde el origen del frontend.
Importante: Eliminar la carpeta node_modules antes de comprimir.
⚡ Conclusiones Esperadas: Al finalizar el trabajo práctico, asegúrate de contar con las carpetas components/, types/ y services/, tener Tailwind CSS aplicado y no presentar errores de TS en consola. Recuerda que App.tsx ya no tiene lógica de negocio; solo debe encargarse de definir rutas y renderizar el Navbar.

🚀 Trabajo Práctico - Unidad 7
En este trabajo práctico vas a desarrollar una aplicación Full Stack conectando un frontend React + TypeScript (inicializado con Vite) con un backend FastAPI.

El objetivo principal es implementar el CRUD completo de Categorías desde la interfaz de usuario, integrando el backend mediante TanStack Query. Por otro lado, los CRUDs de Producto y ProductoCategoria serán construidos en el backend.

A lo largo del desarrollo vas a aplicar requerimientos clave como:

Organización en páginas separadas (CategoriasPage y ProductsPage) utilizando React Router.
Formulario de alta y edición dentro de un Modal controlado con estado booleano mediante useState.
Manejo del estado del servidor con useQuery y useMutation, invalidando la caché luego de cada operación.
Tipado estricto definiendo Interfaces en TypeScript para Categoría y Producto.
Estilizado de componentes mediante clases predefinidas de Tailwind CSS.
En el backend, deberás seguir la arquitectura Models-Schemas-Service-Router, validar datos con Pydantic y asegurarte de configurar CORS para permitir la comunicación desde el dominio del frontend.

💡 Recuerda el cambio clave: App.tsx ya no debe tener lógica de negocio. Solo debe encargarse de definir rutas y renderizar el Navbar. ¡Si tu CRUD de Categorías funciona de extremo a extremo, habrás cumplido el objetivo principal!