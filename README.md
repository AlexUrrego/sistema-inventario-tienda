# Sistema de inventario para tienda (consola)

Aplicación de consola en Python para controlar el inventario de una tienda con tres sectores: **mascotas, fincas y medicamentos**. Guarda la información en archivos CSV, registra las ventas y las distribuciones a tiendas anexas, y resume las ventas del mes.

## Qué problema resuelve
Llevar el control de existencias, ventas y traslados de productos sin hojas de cálculo manuales, con datos organizados por mes y listos para analizar.

## Funciones
1. Agregar producto (si ya existe, suma las unidades).
2. Descontar producto, por ejemplo por daño o pérdida.
3. Ver el inventario actual.
4. Registrar venta.
5. Sumar las ventas del mes, en total y por producto.
6. Distribuir productos a tiendas anexas.

## Cómo funciona
- El inventario se guarda en un CSV por mes: `inventarios_mensuales/inventario_AAAA-MM.csv`.
- Si empieza un mes nuevo, el programa parte del inventario del último mes guardado.
- Las ventas y las distribuciones se guardan en CSV mensuales: `ventas_registradas/` y `distribuciones_anexas/`.
- Valida las entradas: cantidades enteras mayores que cero, sectores permitidos y stock suficiente antes de vender, descontar o distribuir.
- Las búsquedas de productos no distinguen mayúsculas de minúsculas.

## Herramientas
Python 3 y Pandas.

## Cómo ejecutarlo
```bash
pip install pandas
python tienda.py
```
Los archivos CSV se crean solos al usar el programa.

## Estructura
```
tienda.py
inventarios_mensuales/     # se crea al ejecutar
ventas_registradas/        # se crea al ejecutar
distribuciones_anexas/     # se crea al ejecutar
```
