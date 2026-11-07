"""Sistema de inventario por consola para una tienda.

Maneja tres sectores (mascotas, fincas, medicamentos), guarda el inventario
en un CSV por mes y registra ventas y distribuciones a tiendas anexas.
"""

import glob
import os
from datetime import datetime

import pandas as pd

# Directorios y constantes
DIRECTORIO_INVENTARIO = "inventarios_mensuales"
DIRECTORIO_DISTRIBUCION = "distribuciones_anexas"
DIRECTORIO_VENTAS = "ventas_registradas"
SECTORES = ("mascotas", "fincas", "medicamentos")
COLUMNAS = ["nombre", "cantidad", "sector", "ultima_actualizacion"]

for directorio in (DIRECTORIO_INVENTARIO, DIRECTORIO_DISTRIBUCION, DIRECTORIO_VENTAS):
    os.makedirs(directorio, exist_ok=True)


# ---------- Utilidades ----------

def ahora():
    """Fecha y hora actual como texto."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def mes_actual():
    """Mes actual con formato AAAA-MM."""
    return datetime.now().strftime("%Y-%m")


def pedir_entero(mensaje):
    """Pide un número entero mayor que cero y repite hasta que sea válido."""
    while True:
        try:
            valor = int(input(mensaje))
            if valor > 0:
                return valor
            print("Ingrese un número entero mayor que cero.")
        except ValueError:
            print("Valor no válido. Ingrese un número entero.")


def pedir_sector():
    """Pide el sector y repite hasta que sea uno de los permitidos."""
    while True:
        sector = input(f"Sector ({'/'.join(SECTORES)}): ").strip().lower()
        if sector in SECTORES:
            return sector
        print("Sector no válido.")


def buscar_indice(df, nombre):
    """Devuelve el índice del producto (sin distinguir mayúsculas) o None."""
    nombres = df["nombre"].astype(str).str.strip().str.lower()
    coincidencias = df.index[nombres == nombre.strip().lower()]
    return coincidencias[0] if len(coincidencias) else None


def agregar_registro_csv(archivo, registro):
    """Agrega una fila a un CSV, creándolo si no existe."""
    nuevo = pd.DataFrame([registro])
    if os.path.exists(archivo):
        nuevo = pd.concat([pd.read_csv(archivo), nuevo], ignore_index=True)
    nuevo.to_csv(archivo, index=False)


# ---------- Inventario ----------

def obtener_archivo_mensual():
    """Obtiene el nombre del archivo CSV del inventario del mes."""
    return os.path.join(DIRECTORIO_INVENTARIO, f"inventario_{mes_actual()}.csv")


def cargar_inventario_mensual():
    """Carga el inventario del mes.

    Si el mes todavía no tiene archivo, parte del inventario del último mes
    guardado para no perder las existencias.
    """
    archivo = obtener_archivo_mensual()
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
    else:
        anteriores = sorted(glob.glob(os.path.join(
            DIRECTORIO_INVENTARIO, "inventario_*.csv")))
        if anteriores:
            print(
                f"Mes nuevo: se parte del inventario de {os.path.basename(anteriores[-1])}.")
            df = pd.read_csv(anteriores[-1])
        else:
            df = pd.DataFrame(columns=COLUMNAS)
    df["cantidad"] = df["cantidad"].astype(int)
    return df


def guardar_inventario_mensual(df):
    """Guarda el inventario en el archivo CSV del mes."""
    df.to_csv(obtener_archivo_mensual(), index=False)


def agregar_producto(df):
    """Agrega un producto nuevo o suma unidades si ya existe."""
    nombre = input("Nombre del producto: ").strip()
    if not nombre:
        print("El nombre no puede estar vacío.")
        return df
    cantidad = pedir_entero("Cantidad ingresada: ")
    idx = buscar_indice(df, nombre)
    if idx is not None:
        df.at[idx, "cantidad"] += cantidad
        df.at[idx, "ultima_actualizacion"] = ahora()
        print(f"El producto ya existía: se sumaron {cantidad} unidades.")
    else:
        sector = pedir_sector()
        nuevo = pd.DataFrame({
            "nombre": [nombre],
            "cantidad": [cantidad],
            "sector": [sector],
            "ultima_actualizacion": [ahora()],
        })
        df = nuevo if df.empty else pd.concat([df, nuevo], ignore_index=True)
        print("Producto agregado exitosamente.")
    guardar_inventario_mensual(df)
    return df


def retirar_stock(df, nombre, cantidad):
    """Resta unidades del inventario si el producto existe y alcanza el stock.

    Devuelve el nombre registrado del producto, o None si no se pudo retirar.
    """
    idx = buscar_indice(df, nombre)
    if idx is None:
        print("Producto no encontrado.")
        return None
    disponible = df.at[idx, "cantidad"]
    if cantidad > disponible:
        print(
            f"Cantidad insuficiente en inventario. Disponible: {disponible}.")
        return None
    df.at[idx, "cantidad"] -= cantidad
    df.at[idx, "ultima_actualizacion"] = ahora()
    guardar_inventario_mensual(df)
    return df.at[idx, "nombre"]


def descontar_producto(df):
    """Descuenta unidades de un producto (por ejemplo, por daño o pérdida)."""
    nombre = input("Nombre del producto a descontar: ")
    cantidad = pedir_entero("Cantidad a descontar: ")
    if retirar_stock(df, nombre, cantidad):
        print("Producto descontado exitosamente.")
    return df


def ver_inventario(df):
    """Muestra el inventario actual."""
    print("\nInventario actual:")
    if df.empty:
        print("No hay productos en el inventario.")
    else:
        print(df.to_string(index=False))


# ---------- Ventas y distribución ----------

def registrar_venta(df):
    """Registra una venta y la guarda en el CSV de ventas del mes."""
    nombre = input("Nombre del producto vendido: ")
    cantidad = pedir_entero("Cantidad vendida: ")
    producto = retirar_stock(df, nombre, cantidad)
    if producto:
        archivo = os.path.join(DIRECTORIO_VENTAS, f"ventas_{mes_actual()}.csv")
        agregar_registro_csv(
            archivo, {"fecha": ahora(), "producto": producto, "cantidad": cantidad})
        print("Venta registrada exitosamente.")
    return df


def sumar_ventas_mensuales():
    """Suma las ventas del mes actual, total y por producto."""
    archivo = os.path.join(DIRECTORIO_VENTAS, f"ventas_{mes_actual()}.csv")
    if not os.path.exists(archivo):
        print("No hay registros de ventas este mes.")
        return
    ventas = pd.read_csv(archivo)
    print(
        f"Total de ventas de {mes_actual()}: {ventas['cantidad'].sum()} unidades")
    por_producto = ventas.groupby(
        "producto")["cantidad"].sum().sort_values(ascending=False)
    print(por_producto.to_string())


def distribuir_a_tiendas_anexas(df):
    """Distribuye productos a tiendas anexas y guarda el registro del mes."""
    if df.empty:
        print("No hay productos en el inventario.")
        return df
    print("\nProductos disponibles para distribución:")
    print(df[["nombre", "cantidad"]].to_string(index=False))
    nombre = input("Nombre del producto a distribuir: ")
    cantidad = pedir_entero("Cantidad a distribuir: ")
    producto = retirar_stock(df, nombre, cantidad)
    if producto:
        archivo = os.path.join(DIRECTORIO_DISTRIBUCION,
                               f"distribucion_{mes_actual()}.csv")
        agregar_registro_csv(
            archivo, {"fecha": ahora(), "producto": producto, "cantidad": cantidad})
        print("Distribución registrada exitosamente.")
    return df


# ---------- Menú ----------

def menu():
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Agregar producto")
    print("2. Descontar producto")
    print("3. Ver inventario")
    print("4. Registrar venta")
    print("5. Sumar ventas mensuales")
    print("6. Distribuir a tiendas anexas")
    print("7. Salir")


def main():
    df = cargar_inventario_mensual()
    while True:
        menu()
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            df = agregar_producto(df)
        elif opcion == "2":
            df = descontar_producto(df)
        elif opcion == "3":
            ver_inventario(df)
        elif opcion == "4":
            df = registrar_venta(df)
        elif opcion == "5":
            sumar_ventas_mensuales()
        elif opcion == "6":
            df = distribuir_a_tiendas_anexas(df)
        elif opcion == "7":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
