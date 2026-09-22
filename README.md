# Inventario de restaurante de comida rápida

## Descripción

Aplicación de escritorio desarrollada en Python para administrar el inventario de un restaurante de comida rápida. Los productos se clasifican en **Congelados**, **Refrigerados** y **Secos**. La interfaz gráfica permite crear, consultar, actualizar y eliminar productos, además de filtrar el inventario y detectar existencias bajas.

## Objetivo

Integrar los conceptos de colecciones, anotaciones de tipos, interfaz gráfica y manejo de eventos mediante un inventario funcional. El programa utiliza `list`, `dict` y `set`, operaciones CRUD, validación de datos con Pydantic e interfaz gráfica con Flet.

## Funcionalidades

- Registrar productos con código, nombre, categoría, cantidad, unidad, costo y stock mínimo.
- Buscar un producto por su código.
- Listar todos los productos registrados.
- Actualizar los datos de un producto sin cambiar su código único.
- Eliminar productos del inventario.
- Evitar códigos duplicados.
- Filtrar por categoría o por stock bajo.
- Calcular el valor total del inventario.
- Cargar productos de prueba de las tres categorías.
- Mostrar mensajes de confirmación y errores de validación.

## Colecciones utilizadas

- `list[Producto]`: conserva los productos en el orden en que fueron registrados.
- `dict[str, Producto]`: relaciona cada código con su producto y permite búsquedas rápidas.
- `set[str]`: guarda los códigos registrados e impide duplicados.

## Operaciones CRUD

| Operación | Función en la aplicación |
|---|---|
| Crear | Agregar un producto |
| Consultar | Buscar y listar productos |
| Actualizar | Modificar los datos de un producto |
| Eliminar | Retirar un producto del inventario |

## Tecnologías

- Python 3.10 o posterior.
- Flet para la interfaz gráfica y el manejo de eventos.
- Pydantic 2 para validar los datos.

## Instalación

1. Descargar o clonar el repositorio.
2. Abrir una terminal en la carpeta del proyecto.
3. Crear un entorno virtual, de manera opcional:

```bash
python -m venv .venv
```

4. Activarlo en Windows:

```bash
.venv\Scripts\activate
```

5. Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

```bash
python Garces_Karla_Semanas5y6.py
```

Al abrirse la aplicación, se puede registrar un producto manualmente o utilizar el botón **Cargar datos de prueba**. Para actualizar o eliminar un producto, primero se debe buscar por su código o seleccionarlo en la tabla.

## Estructura principal

- `Producto`: modelo Pydantic que representa y valida cada producto.
- `InventarioRestaurante`: administra las colecciones y las operaciones CRUD.
- `main(page)`: construye la interfaz Flet y contiene los controladores de eventos.

## Estudiante

Karla D. Garcés  
