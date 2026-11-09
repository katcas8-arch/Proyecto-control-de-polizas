"""Reglas del negocio para pólizas.

Cruza los datos de models/datos.py y aplica las reglas de estado, conteo,
primas e inconsistencias definidas en AGENTS.md.
"""

from datetime import date

from models.datos import cargar_clientes, cargar_polizas

FECHA_CORTE = date(2026, 11, 2)
DIAS_AVISO = 30


def estado_poliza(hasta, fecha_corte=FECHA_CORTE):
    """Devuelve el estado de una póliza: Vencida, Por vencer, Vigente o Sin fecha.

    Reglas:
    - Sin fecha: hasta es None
    - Vencida: hasta < fecha_corte
    - Por vencer: 0 <= dias hasta vencer <= DIAS_AVISO
    - Vigente: mas de DIAS_AVISO dias
    """
    if hasta is None:
        return "Sin fecha"
    if hasta < fecha_corte:
        return "Vencida"
    dias = (hasta - fecha_corte).days
    if 0 <= dias <= DIAS_AVISO:
        return "Por vencer"
    return "Vigente"


def calcular_resultados(fecha_corte=FECHA_CORTE):
    """Cruza cada póliza con el maestro por cedula y devuelve resultados ordenados.

    Para cada póliza calcula:
    - correo y en_maestro (cruzando con el maestro por cedula)
    - dias hasta vencer (hasta - fecha_corte)
    - estado (Vencida, Por vencer, Vigente o Sin fecha)

    Devuelve una lista de diccionarios ordenada de menos a mas dias
    (lo urgente primero). Las pólizas Sin fecha van al final.
    """
    df_clientes = cargar_clientes()
    polizas = cargar_polizas()

    # Indice del maestro: cedula -> correo
    maestro = {}
    for _, fila in df_clientes.iterrows():
        cedula = str(fila["Cedula"]).strip()
        correo = fila.get("Correo", "")
        maestro[cedula] = correo

    resultados = []
    for p in polizas:
        cedula = p.get("cedula", "")
        hasta = p.get("hasta")
        estado = estado_poliza(hasta, fecha_corte)
        if hasta is not None:
            dias = (hasta - fecha_corte).days
        else:
            dias = None
        en_maestro = cedula in maestro
        correo = maestro.get(cedula, "")
        resultados.append({
            "numero": p.get("numero", ""),
            "aseguradora": p.get("aseguradora", ""),
            "ramo": p.get("ramo", ""),
            "nombre": p.get("nombre", ""),
            "cedula": cedula,
            "correo": correo,
            "en_maestro": en_maestro,
            "desde": p.get("desde"),
            "hasta": hasta,
            "dias": dias,
            "estado": estado,
            "prima": p.get("prima"),
            "pago": p.get("pago", ""),
            "suma": p.get("suma"),
            "asesor": p.get("asesor", ""),
            "archivo": p.get("archivo", ""),
        })

    def clave_orden(r):
        if r["dias"] is None:
            return float("inf")
        return r["dias"]

    resultados.sort(key=clave_orden)
    return resultados


def contar_por_estado(resultados):
    """Devuelve un diccionario con la cantidad de pólizas de cada estado."""
    conteo = {"Vigente": 0, "Por vencer": 0, "Vencida": 0, "Sin fecha": 0}
    for r in resultados:
        estado = r["estado"]
        if estado in conteo:
            conteo[estado] += 1
        else:
            conteo[estado] = 1
    return conteo


def primas_por_aseguradora(resultados):
    """Suma las primas de las pólizas NO vencidas por aseguradora.

    Devuelve un diccionario aseguradora -> suma, ordenado de mayor a menor.
    """
    sumas = {}
    for r in resultados:
        if r["estado"] == "Vencida":
            continue
        aseg = r["aseguradora"]
        prima = r["prima"] if r["prima"] is not None else 0
        sumas[aseg] = sumas.get(aseg, 0) + prima
    ordenado = dict(sorted(sumas.items(), key=lambda item: item[1], reverse=True))
    return ordenado


def buscar_inconsistencias(resultados):
    """Detecta los 3 tipos de inconsistencia y devuelve una lista de textos.

    1. Cliente del maestro sin ninguna póliza.
    2. Póliza cuya cedula no está en el maestro.
    3. Póliza sin prima o con fecha ilegible.
    """
    df_clientes = cargar_clientes()
    clientes_cedula = set()
    for _, fila in df_clientes.iterrows():
        clientes_cedula.add(str(fila["Cedula"]).strip())

    cedulas_en_polizas = {r["cedula"] for r in resultados}

    inconsistencias = []

    # (1) cliente del maestro sin ninguna póliza
    for cedula in clientes_cedula:
        if cedula not in cedulas_en_polizas:
            inconsistencias.append(
                f"Cliente {cedula} del maestro no tiene ninguna póliza."
            )

    # (2) póliza cuya cedula no está en el maestro
    for r in resultados:
        cedula = r["cedula"]
        if cedula != "" and cedula not in clientes_cedula:
            inconsistencias.append(
                f"Póliza {r['numero']} con cedula {cedula} no está en el maestro."
            )

    # (3) póliza sin prima o con fecha ilegible
    for r in resultados:
        problemas = []
        if r["prima"] is None:
            problemas.append("sin prima")
        if r["desde"] is None or r["hasta"] is None:
            problemas.append("fecha ilegible")
        if problemas:
            inconsistencias.append(
                f"Póliza {r['numero']}: {', '.join(problemas)}."
            )

    return inconsistencias


def buscar_por_numero(numero):
    """Busca una póliza por su número entre los resultados calculados.

    Devuelve el diccionario de la póliza o None si no existe.
    """
    resultados = calcular_resultados()
    for r in resultados:
        if r["numero"] == numero:
            return r
    return None
