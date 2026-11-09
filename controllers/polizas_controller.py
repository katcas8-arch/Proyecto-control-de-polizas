"""Rutas de Flask para el módulo de pólizas.

El controlador NO calcula nada: solo llama a models/ y services/ y
devuelve las vistas o archivos correspondientes.
"""

import io
import zipfile

from flask import Blueprint, render_template, send_file, abort

from models.polizas import (
    calcular_resultados,
    contar_por_estado,
    primas_por_aseguradora,
    buscar_inconsistencias,
    buscar_por_numero,
    FECHA_CORTE,
)
from services.generador_aviso import crear_aviso_pdf

polizas_bp = Blueprint("polizas", __name__)


@polizas_bp.route("/")
def inicio():
    """Tablero principal: contadores, primas, inconsistencias y tabla de pólizas."""
    resultados = calcular_resultados()
    conteo = contar_por_estado(resultados)
    primas = primas_por_aseguradora(resultados)
    inconsistencias = buscar_inconsistencias(resultados)
    return render_template(
        "inicio.html",
        resultados=resultados,
        conteo=conteo,
        primas=primas,
        inconsistencias=inconsistencias,
        fecha_corte=FECHA_CORTE,
    )


@polizas_bp.route("/aviso/<numero>")
def aviso(numero):
    """Devuelve el aviso de renovación en PDF para ver en el navegador.

    404 si la póliza no existe o está Vigente.
    """
    poliza = buscar_por_numero(numero)
    if poliza is None:
        abort(404)
    if poliza["estado"] == "Vigente":
        abort(404)

    pdf_bytes = crear_aviso_pdf(poliza)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        download_name=f"aviso_{numero}.pdf",
    )


@polizas_bp.route("/descargar-avisos")
def descargar_avisos():
    """Arma en memoria un .zip con los avisos de pólizas Por vencer y Vencidas."""
    resultados = calcular_resultados()

    buffer_zip = io.BytesIO()
    with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in resultados:
            if r["estado"] in ("Por vencer", "Vencida"):
                pdf_bytes = crear_aviso_pdf(r)
                zf.writestr(f"aviso_{r['numero']}.pdf", pdf_bytes)

    buffer_zip.seek(0)
    return send_file(
        buffer_zip,
        mimetype="application/zip",
        download_name="avisos.zip",
        as_attachment=True,
    )
