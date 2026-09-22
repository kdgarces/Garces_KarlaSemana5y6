from typing import Literal

import flet as ft
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


Categoria = Literal["Congelados", "Refrigerados", "Secos"]


class Producto(BaseModel):
    """Representa un producto almacenado en el restaurante."""

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    codigo: str = Field(min_length=3, max_length=12)
    nombre: str = Field(min_length=2, max_length=60)
    categoria: Categoria
    cantidad: float = Field(ge=0)
    unidad: str = Field(min_length=1, max_length=20)
    costo_unitario: float = Field(gt=0)
    stock_minimo: float = Field(ge=0)

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, codigo: str) -> str:
        codigo = codigo.upper()
        if not codigo.isalnum():
            raise ValueError("El código solo debe contener letras y números.")
        return codigo

    @field_validator("nombre", "unidad")
    @classmethod
    def validar_texto(cls, texto: str) -> str:
        if not any(caracter.isalpha() for caracter in texto):
            raise ValueError("El campo debe contener letras.")
        return texto.title()

    @property
    def valor_total(self) -> float:
        return self.cantidad * self.costo_unitario

    @property
    def tiene_stock_bajo(self) -> bool:
        return self.cantidad <= self.stock_minimo


class InventarioRestaurante:
    """Administra los productos mediante list, dict y set."""

    def __init__(self) -> None:
        # list: conserva el orden en el que se registraron los productos.
        self.productos: list[Producto] = []

        # dict: permite buscar un producto rápidamente usando su código.
        self.productos_por_codigo: dict[str, Producto] = {}

        # set: evita que se registren códigos duplicados.
        self.codigos_registrados: set[str] = set()

    @staticmethod
    def preparar_codigo(codigo: str) -> str:
        return codigo.strip().upper()

    def agregar_producto(self, producto: Producto) -> None:
        codigo = self.preparar_codigo(producto.codigo)
        if codigo in self.codigos_registrados:
            raise ValueError(f"Ya existe un producto con el código {codigo}.")

        self.productos.append(producto)
        self.productos_por_codigo[codigo] = producto
        self.codigos_registrados.add(codigo)

    def buscar_producto(self, codigo: str) -> Producto:
        codigo = self.preparar_codigo(codigo)
        if codigo not in self.productos_por_codigo:
            raise KeyError(f"No existe un producto con el código {codigo}.")
        return self.productos_por_codigo[codigo]

    def listar_productos(self, categoria: str = "Todos") -> list[Producto]:
        if categoria == "Todos":
            return list(self.productos)
        if categoria == "Stock bajo":
            return [producto for producto in self.productos if producto.tiene_stock_bajo]
        return [producto for producto in self.productos if producto.categoria == categoria]

    def actualizar_producto(
        self,
        codigo: str,
        nombre: str,
        categoria: Categoria,
        cantidad: float,
        unidad: str,
        costo_unitario: float,
        stock_minimo: float,
    ) -> Producto:
        producto = self.buscar_producto(codigo)

        # Se construye un producto nuevo para validar todos los cambios antes
        # de modificar el objeto almacenado. El código es inmutable.
        datos_validados = Producto(
            codigo=producto.codigo,
            nombre=nombre,
            categoria=categoria,
            cantidad=cantidad,
            unidad=unidad,
            costo_unitario=costo_unitario,
            stock_minimo=stock_minimo,
        )

        producto.nombre = datos_validados.nombre
        producto.categoria = datos_validados.categoria
        producto.cantidad = datos_validados.cantidad
        producto.unidad = datos_validados.unidad
        producto.costo_unitario = datos_validados.costo_unitario
        producto.stock_minimo = datos_validados.stock_minimo
        return producto

    def eliminar_producto(self, codigo: str) -> Producto:
        producto = self.buscar_producto(codigo)
        self.productos.remove(producto)
        del self.productos_por_codigo[producto.codigo]
        self.codigos_registrados.remove(producto.codigo)
        return producto

    def valor_total_inventario(self) -> float:
        return sum(producto.valor_total for producto in self.productos)

    def cantidad_stock_bajo(self) -> int:
        return sum(producto.tiene_stock_bajo for producto in self.productos)


DATOS_PRUEBA = [
    ("CON001", "Chicken tenders", "Congelados", 8, "Cajas", 32.50, 5),
    ("CON002", "Pescado", "Congelados", 4, "Cajas", 48.00, 5),
    ("CON003", "Camarones", "Congelados", 6, "Bolsas", 38.75, 4),
    ("CON004", "Papas fritas", "Congelados", 12, "Cajas", 29.90, 6),
    ("CON005", "Onion rings", "Congelados", 3, "Cajas", 26.50, 4),
    ("REF001", "Carne molida", "Refrigerados", 25, "Libras", 4.80, 10),
    ("REF002", "Huevos", "Refrigerados", 90, "Unidades", 0.32, 30),
    ("REF003", "Lechuga", "Refrigerados", 14, "Unidades", 1.75, 8),
    ("REF004", "Queso", "Refrigerados", 18, "Libras", 5.60, 8),
    ("REF005", "Bacon", "Refrigerados", 9, "Libras", 6.90, 5),
    ("SEC001", "Sal", "Secos", 10, "Bolsas", 3.25, 3),
    ("SEC002", "Pimienta", "Secos", 6, "Frascos", 5.40, 2),
    ("SEC003", "Azúcar", "Secos", 20, "Libras", 1.20, 8),
    ("SEC004", "Kétchup", "Secos", 7, "Cajas", 24.50, 4),
    ("SEC005", "Sirope para soda", "Secos", 2, "Cajas", 79.00, 3),
]


def mensaje_error_pydantic(error: ValidationError) -> str:
    primer_error = error.errors()[0]
    campo = str(primer_error["loc"][0]).replace("_", " ").capitalize()
    mensaje = primer_error["msg"].replace("Value error, ", "")
    return f"{campo}: {mensaje}"


def main(page: ft.Page) -> None:
    page.title = "Inventario de restaurante"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO

    inventario = InventarioRestaurante()

    codigo = ft.TextField(label="Código", hint_text="Ejemplo: CON001")
    nombre = ft.TextField(label="Nombre del producto")
    categoria = ft.Dropdown(
        label="Categoría",
        value="Congelados",
        options=[
            ft.DropdownOption(key="Congelados", text="Congelados"),
            ft.DropdownOption(key="Refrigerados", text="Refrigerados"),
            ft.DropdownOption(key="Secos", text="Secos"),
        ],
    )
    cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)
    unidad = ft.Dropdown(
        label="Unidad",
        value="Unidades",
        options=[
            ft.DropdownOption(key=valor, text=valor)
            for valor in (
                "Unidades",
                "Libras",
                "Kilogramos",
                "Bolsas",
                "Cajas",
                "Galones",
                "Botellas",
                "Frascos",
            )
        ],
    )
    costo = ft.TextField(label="Costo unitario ($)", keyboard_type=ft.KeyboardType.NUMBER)
    stock_minimo = ft.TextField(label="Stock mínimo", keyboard_type=ft.KeyboardType.NUMBER)

    filtro = ft.Dropdown(
        label="Filtrar productos",
        value="Todos",
        width=230,
        options=[
            ft.DropdownOption(key=valor, text=valor)
            for valor in ("Todos", "Congelados", "Refrigerados", "Secos", "Stock bajo")
        ],
    )

    mensaje = ft.Text("Complete el formulario para comenzar.", color=ft.Colors.BLUE_700)
    resumen = ft.Text(weight=ft.FontWeight.BOLD)
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Código")),
            ft.DataColumn(label=ft.Text("Producto")),
            ft.DataColumn(label=ft.Text("Categoría")),
            ft.DataColumn(label=ft.Text("Cantidad")),
            ft.DataColumn(label=ft.Text("Unidad")),
            ft.DataColumn(label=ft.Text("Costo")),
            ft.DataColumn(label=ft.Text("Estado")),
        ],
        rows=[],
        border=ft.Border.all(1, ft.Colors.GREY_300),
        heading_row_color=ft.Colors.BLUE_GREY_50,
    )

    def mostrar_mensaje(texto: str, es_error: bool = False) -> None:
        mensaje.value = texto
        mensaje.color = ft.Colors.RED_700 if es_error else ft.Colors.GREEN_700

    def convertir_numero(valor: str, nombre_campo: str) -> float:
        try:
            return float(valor.strip().replace(",", "."))
        except (AttributeError, ValueError):
            raise ValueError(f"{nombre_campo} debe ser un número válido.")

    def crear_desde_formulario() -> Producto:
        return Producto(
            codigo=codigo.value or "",
            nombre=nombre.value or "",
            categoria=categoria.value,
            cantidad=convertir_numero(cantidad.value, "La cantidad"),
            unidad=unidad.value,
            costo_unitario=convertir_numero(costo.value, "El costo unitario"),
            stock_minimo=convertir_numero(stock_minimo.value, "El stock mínimo"),
        )

    def limpiar_formulario(evento=None) -> None:
        codigo.value = ""
        codigo.disabled = False
        nombre.value = ""
        categoria.value = "Congelados"
        cantidad.value = ""
        unidad.value = "Unidades"
        costo.value = ""
        stock_minimo.value = ""
        if evento is not None:
            mostrar_mensaje("Formulario limpio.")
            page.update()

    def cargar_en_formulario(producto: Producto) -> None:
        codigo.value = producto.codigo
        codigo.disabled = True
        nombre.value = producto.nombre
        categoria.value = producto.categoria
        cantidad.value = f"{producto.cantidad:g}"
        unidad.value = producto.unidad
        costo.value = f"{producto.costo_unitario:.2f}"
        stock_minimo.value = f"{producto.stock_minimo:g}"

    def actualizar_tabla() -> None:
        tabla.rows.clear()
        for producto in inventario.listar_productos(filtro.value or "Todos"):
            estado = "Stock bajo" if producto.tiene_stock_bajo else "Disponible"
            color_estado = ft.Colors.RED_700 if producto.tiene_stock_bajo else ft.Colors.GREEN_700
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(producto.codigo)),
                        ft.DataCell(ft.Text(producto.nombre)),
                        ft.DataCell(ft.Text(producto.categoria)),
                        ft.DataCell(ft.Text(f"{producto.cantidad:g}")),
                        ft.DataCell(ft.Text(producto.unidad)),
                        ft.DataCell(ft.Text(f"${producto.costo_unitario:.2f}")),
                        ft.DataCell(ft.Text(estado, color=color_estado)),
                    ],
                    on_select_change=lambda evento, p=producto: cargar_y_actualizar(p),
                )
            )

        resumen.value = (
            f"Productos: {len(inventario.productos)}   |   "
            f"Stock bajo: {inventario.cantidad_stock_bajo()}   |   "
            f"Valor total: ${inventario.valor_total_inventario():,.2f}"
        )

    def cargar_y_actualizar(producto: Producto) -> None:
        cargar_en_formulario(producto)
        mostrar_mensaje(f"Producto {producto.codigo} seleccionado.")
        page.update()

    def agregar_click(evento) -> None:
        try:
            producto = crear_desde_formulario()
            inventario.agregar_producto(producto)
            mostrar_mensaje(f"Producto {producto.codigo} agregado correctamente.")
            limpiar_formulario()
            actualizar_tabla()
        except ValidationError as error:
            mostrar_mensaje(mensaje_error_pydantic(error), True)
        except ValueError as error:
            mostrar_mensaje(str(error), True)
        page.update()

    def buscar_click(evento) -> None:
        try:
            if not (codigo.value or "").strip():
                raise ValueError("Ingrese el código que desea buscar.")
            producto = inventario.buscar_producto(codigo.value)
            cargar_en_formulario(producto)
            mostrar_mensaje(f"Producto {producto.codigo} encontrado.")
        except (KeyError, ValueError) as error:
            mostrar_mensaje(str(error).strip("'"), True)
        page.update()

    def actualizar_click(evento) -> None:
        try:
            if not (codigo.value or "").strip():
                raise ValueError("Busque o seleccione un producto antes de actualizarlo.")
            producto = inventario.actualizar_producto(
                codigo=codigo.value,
                nombre=nombre.value or "",
                categoria=categoria.value,
                cantidad=convertir_numero(cantidad.value, "La cantidad"),
                unidad=unidad.value,
                costo_unitario=convertir_numero(costo.value, "El costo unitario"),
                stock_minimo=convertir_numero(stock_minimo.value, "El stock mínimo"),
            )
            mostrar_mensaje(f"Producto {producto.codigo} actualizado correctamente.")
            limpiar_formulario()
            actualizar_tabla()
        except ValidationError as error:
            mostrar_mensaje(mensaje_error_pydantic(error), True)
        except (KeyError, ValueError) as error:
            mostrar_mensaje(str(error).strip("'"), True)
        page.update()

    def eliminar_click(evento) -> None:
        try:
            if not (codigo.value or "").strip():
                raise ValueError("Busque o seleccione un producto antes de eliminarlo.")
            eliminado = inventario.eliminar_producto(codigo.value)
            mostrar_mensaje(f"Producto {eliminado.codigo} eliminado correctamente.")
            limpiar_formulario()
            actualizar_tabla()
        except (KeyError, ValueError) as error:
            mostrar_mensaje(str(error).strip("'"), True)
        page.update()

    def cargar_datos_click(evento) -> None:
        agregados = 0
        for datos in DATOS_PRUEBA:
            producto = Producto(
                codigo=datos[0],
                nombre=datos[1],
                categoria=datos[2],
                cantidad=datos[3],
                unidad=datos[4],
                costo_unitario=datos[5],
                stock_minimo=datos[6],
            )
            if producto.codigo not in inventario.codigos_registrados:
                inventario.agregar_producto(producto)
                agregados += 1
        mostrar_mensaje(f"Se cargaron {agregados} productos de prueba.")
        actualizar_tabla()
        page.update()

    def cambiar_filtro(evento) -> None:
        actualizar_tabla()
        page.update()

    filtro.on_select = cambiar_filtro

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Datos del producto", size=20, weight=ft.FontWeight.BOLD),
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(codigo, col={"sm": 12, "md": 4}),
                        ft.Container(nombre, col={"sm": 12, "md": 8}),
                        ft.Container(categoria, col={"sm": 12, "md": 4}),
                        ft.Container(cantidad, col={"sm": 12, "md": 4}),
                        ft.Container(unidad, col={"sm": 12, "md": 4}),
                        ft.Container(costo, col={"sm": 12, "md": 6}),
                        ft.Container(stock_minimo, col={"sm": 12, "md": 6}),
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Button("Agregar", icon=ft.Icons.ADD, on_click=agregar_click),
                        ft.Button("Buscar", icon=ft.Icons.SEARCH, on_click=buscar_click),
                        ft.Button("Actualizar", icon=ft.Icons.EDIT, on_click=actualizar_click),
                        ft.Button("Eliminar", icon=ft.Icons.DELETE, on_click=eliminar_click),
                        ft.OutlinedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=limpiar_formulario),
                        ft.OutlinedButton(
                            "Cargar datos de prueba",
                            icon=ft.Icons.INVENTORY_2,
                            on_click=cargar_datos_click,
                        ),
                    ],
                    wrap=True,
                    spacing=10,
                    run_spacing=10,
                ),
                mensaje,
            ],
            spacing=14,
        ),
        padding=18,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
    )

    page.add(
        ft.Text("Inventario de restaurante de comida rápida", size=28, weight=ft.FontWeight.BOLD),
        ft.Text(
            "Administración de productos congelados, refrigerados y secos",
            color=ft.Colors.BLUE_GREY_700,
        ),
        formulario,
        ft.Divider(),
        ft.ResponsiveRow(
            controls=[
                ft.Container(
                    ft.Text("Productos registrados", size=20, weight=ft.FontWeight.BOLD),
                    col={"sm": 12, "md": 8},
                ),
                ft.Container(filtro, col={"sm": 12, "md": 4}),
            ]
        ),
        resumen,
        ft.Row([tabla], scroll=ft.ScrollMode.AUTO),
    )

    actualizar_tabla()


if __name__ == "__main__":
    ft.run(main)
