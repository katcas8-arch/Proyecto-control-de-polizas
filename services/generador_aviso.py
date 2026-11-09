"""Generador de avisos de renovación en PDF (fpdf2).

Crea un aviso de renovación de póliza en formato A4 vertical y lo devuelve
en bytes, listo para ser enviado o guardado en disco.
"""

from datetime import date
from io import BytesIO

from fpdf import FPDF

# Colores definidos en AGENTS.md
ROJO = (174, 24, 0)      # #AE1800
GRIS = (200, 200, 200)   # gris claro para el pie
NEGRO = (0, 0, 0)        # #201E1D


def _latin1(texto):
    """Convierte texto a latin-1 para que tildes y 'ñ' no fallen en Helvetica."""
    if texto is None:
        return ""
    return str(texto).encode("latin-1", errors="replace").decode("latin-1")


class _AvisoPDF(FPDF):
    """PDF con pie de página gris automático."""

    def footer(self):
        self.set_y(-15)
        self.set_fill_color(*GRIS)
        self.set_text_color(80, 80, 80)
        self.set_font("Helvetica", "I", 8)
        self.cell(
            0,
            10,
            _latin1("Documento ficticio con fines académicos."),
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )


def crear_aviso_pdf(poliza):
    """Crea un aviso de renovación de póliza en PDF (A4 vertical) y devuelve bytes.

    Args:
        poliza: diccionario con al menos: nombre, estado, hasta, dias,
                numero, aseguradora, ramo, cedula, desde, prima, pago, asesor.

    Returns:
        bytes: contenido del PDF listo para escribir en archivo o enviar por red.
    """
    pdf = _AvisoPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(*NEGRO)

    # --- Banda superior roja ---
    pdf.set_fill_color(*ROJO)
    pdf.rect(0, 0, pdf.w, 30, style="F")
    pdf.set_xy(0, 6)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(
        0,
        8,
        _latin1("Corredora de Seguros Horizonte"),
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0,
        8,
        _latin1("Aviso de renovación de póliza"),
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_y(40)
    pdf.set_text_color(*NEGRO)
    pdf.set_font("Helvetica", size=12)

    # --- Saludo ---
    nombre = poliza.get("nombre", "cliente")
    pdf.cell(
        0,
        8,
        _latin1(f"Estimado(a) {nombre}:"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    # --- Párrafo condicional ---
    estado = poliza.get("estado", "")
    hasta = poliza.get("hasta")
    dias = poliza.get("dias")
    asesor = poliza.get("asesor", "")

    if estado == "Vencida" and hasta is not None:
        parrafo = f"Su póliza venció el {hasta.strftime('%d/%m/%Y')}. Por favor renueve a la brevedad."
    elif estado == "Por vencer" and hasta is not None and dias is not None:
        parrafo = (
            f"Su póliza vence el {hasta.strftime('%d/%m/%Y')} en {dias} días. "
            f"Su asesor {asesor} se comunicará con usted."
        )
    else:
        parrafo = "Su póliza se encuentra vigente."

    pdf.multi_cell(0, 7, _latin1(parrafo))
    pdf.ln(4)

    # --- Tabla de detalle ---
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(
        0,
        8,
        _latin1("Detalle de la póliza"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    desde = poliza.get("desde")
    hasta_dt = poliza.get("hasta")
    prima = poliza.get("prima")

    if desde is not None and hasta_dt is not None:
        vigencia = f"{desde.strftime('%d/%m/%Y')} al {hasta_dt.strftime('%d/%m/%Y')}"
    else:
        vigencia = "No registrada"

    if prima is not None:
        prima_texto = f"CRC {prima:,.2f}"
    else:
        prima_texto = "No registrada"

    filas = [
        ("Número de póliza", poliza.get("numero", "")),
        ("Aseguradora", poliza.get("aseguradora", "")),
        ("Ramo", poliza.get("ramo", "")),
        ("Cédula", poliza.get("cedula", "")),
        ("Vigencia", vigencia),
        ("Prima anual", prima_texto),
        ("Forma de pago", poliza.get("pago", "")),
    ]

    ancho_etiqueta = 45
    ancho_valor = pdf.w - 2 * pdf.l_margin - ancho_etiqueta

    pdf.set_font("Helvetica", size=11)
    for etiqueta, valor in filas:
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(
            ancho_etiqueta,
            8,
            _latin1(etiqueta),
            border=1,
            fill=True,
        )
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(
            ancho_valor,
            8,
            _latin1(valor),
            border=1,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(6)

    # Salida a bytes
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
