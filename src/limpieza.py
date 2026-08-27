"""
limpieza.py
-----------
Normaliza los valores de las columnas ya identificadas (no los encabezados,
eso lo hace deteccion_columnas.py). Esto es lo que permite que "Juan Perez",
"JUAN PEREZ" y "juan   perez" se traten como el mismo texto mas adelante,
sin importar de que anio venga la base.
"""

from __future__ import annotations

import pandas as pd

from .deteccion_columnas import normalizar_texto


def construir_nombre_completo(df: pd.DataFrame, mapping: dict[str, str | None]) -> pd.Series:
    """Arma una columna 'nombre_completo' consistente sin importar si la base
    trae el nombre en una sola columna o separado en nombre/apellidos."""
    col_nombre = mapping.get("nombre")
    col_ap_paterno = mapping.get("apellido_paterno")
    col_ap_materno = mapping.get("apellido_materno")

    partes = []
    if col_nombre:
        partes.append(df[col_nombre].fillna(""))
    if col_ap_paterno:
        partes.append(df[col_ap_paterno].fillna(""))
    if col_ap_materno:
        partes.append(df[col_ap_materno].fillna(""))

    if not partes:
        return pd.Series([""] * len(df), index=df.index)

    nombre_completo = partes[0]
    for parte in partes[1:]:
        nombre_completo = nombre_completo.str.cat(parte, sep=" ")

    return nombre_completo.str.replace(r"\s+", " ", regex=True).str.strip()


def normalizar_dataframe(df: pd.DataFrame, mapping: dict[str, str | None]) -> pd.DataFrame:
    """Devuelve un nuevo DataFrame con columnas canonicas estandarizadas:
    nombre_completo, colegio_norm, carrera_norm, modalidad_norm, estado_norm.
    Las columnas originales se conservan intactas al final.
    """
    df = df.copy()

    df["nombre_completo"] = construir_nombre_completo(df, mapping)

    for campo_origen, columna_destino in [
        ("colegio", "colegio_norm"),
        ("carrera", "carrera_norm"),
        ("modalidad", "modalidad_norm"),
        ("estado", "estado_norm"),
    ]:
        col_real = mapping.get(campo_origen)
        if col_real and col_real in df.columns:
            df[columna_destino] = df[col_real].fillna("").map(normalizar_texto)
        else:
            df[columna_destino] = ""

    return df
