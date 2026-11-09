"""Acceso a archivos de datos (Excel y PDF).

Es el único lugar del proyecto que abre archivos externos.
"""

import os
from datetime import datetime
from pathlib import Path

import pdfplumber

# Raíz del proyecto (carpeta que contiene app.py) y carpeta de datos.
# Se calculan desde la ubicación de este archivo para funcionar igual
# en local y en un servidor como Render, sin depender del directorio actual.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Mapeo: etiqueta del PDF -> nombre del campo en el diccionario de salida
CAMPOS = {
    "Numero de poliza": "numero",
    "Ramo": "ramo",
    "Tomador / Asegurado": "nombre",
    "Cedula": "cedula",
    "Vigencia desde": "desde",
    "Vigencia hasta": "hasta",
    "Prima anual": "prima",
    "Forma de pago": "pago",
    "Suma asegurada": "suma",
    "Asesor": "asesor",
}

CAMPOS_FECHA = {"desde", "hasta"}
CAMPOS_MONTO = {"prima", "suma"}


def cargar_clientes():
    """Lee data/Maestro_Clientes.xlsx (hoja Clientes) y devuelve un DataFrame.

    La columna Cedula se lee como texto y se limpian espacios.
    """
    import pandas as pd

    df = pd.read_excel(
        DATA_DIR / "Maestro_Clientes.xlsx",
        sheet_name="Clientes",
        dtype={"Cedula": str},
    )
    df["Cedula"] = df["Cedula"].astype(str).str.strip()
    return df


def _convertir_fecha(valor):
    """Convierte un string dd/mm/aaaa a objeto date. Devuelve None si está vacío."""
    if valor is None:
        return None
    texto = str(valor).strip()
    if texto == "":
        return None
    return datetime.strptime(texto, "%d/%m/%Y").date()


def _convertir_monto(valor):
    """Convierte un monto tipo 'CRC 228,000.00' a número float.

    Devuelve None si está vacío o no se puede convertir.
    """
    if valor is None:
        return None
    texto = str(valor).strip()
    if texto == "":
        return None
    # Quitar prefijo de moneda y comas de miles
    texto = texto.replace("CRC", "").replace(",", "").strip()
    try:
        return float(texto)
    except ValueError:
        return None


def leer_poliza(ruta_pdf):
    """Extrae los datos de un PDF de póliza y devuelve un diccionario.

    La primera línea del texto es la aseguradora. Las demás líneas con ':'
    se mapean usando CAMPOS. Fechas y montos se convierten.
    """
    nombre_archivo = os.path.basename(ruta_pdf)

    resultado = {
        "archivo": nombre_archivo,
        "aseguradora": "",
        "numero": "",
        "ramo": "",
        "nombre": "",
        "cedula": "",
        "desde": None,
        "hasta": None,
        "prima": None,
        "pago": "",
        "suma": None,
        "asesor": "",
    }

    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        texto = pagina.extract_text() or ""

    lineas = texto.split("\n")
    if not lineas:
        return resultado

    # Primera línea: nombre de la aseguradora
    resultado["aseguradora"] = lineas[0].strip()

    # Recorrer el resto de líneas con un bucle
    for linea in lineas[1:]:
        if ":" in linea:
            etiqueta, valor = linea.split(":", 1)
            etiqueta = etiqueta.strip()
            valor = valor.strip()
            if etiqueta in CAMPOS:
                campo = CAMPOS[etiqueta]
                if campo in CAMPOS_FECHA:
                    resultado[campo] = _convertir_fecha(valor)
                elif campo in CAMPOS_MONTO:
                    resultado[campo] = _convertir_monto(valor)
                else:
                    resultado[campo] = valor

    return resultado


def cargar_polizas():
    """Recorre data/polizas en orden alfabético y devuelve una lista de diccionarios."""
    carpeta = DATA_DIR / "polizas"
    archivos = sorted(
        a for a in os.listdir(carpeta) if a.lower().endswith(".pdf")
    )
    polizas = []
    for archivo in archivos:
        ruta = os.path.join(carpeta, archivo)
        polizas.append(leer_poliza(ruta))
    return polizas
