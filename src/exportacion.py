"""
exportacion.py
--------------
Genera el ID historico por postulante (evita colisiones entre ciclos, ej.
'2010_I_0001' vs '2023_I_0001') y guarda/actualiza:
  - el resultado individual del ciclo procesado (data/output/resultado_<ciclo>.xlsx)
  - la base historica consolidada (data/output/BASE_HISTORICA_ENRIQUECIDA.xlsx)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

CAMPOS_HISTORICA = [
    "ciclo",
    "id_postulante",
    "nombre_completo",
    "colegio_norm",
    "carrera_norm",
    "modalidad_norm",
    "estado_norm",
]


def generar_ids_historicos(df_seleccionados: pd.DataFrame, ciclo_slug: str) -> pd.DataFrame:
    df = df_seleccionados.copy()
    df.insert(0, "ciclo", ciclo_slug)
    df.insert(1, "id_postulante", [f"{ciclo_slug}_{i+1:04d}" for i in range(len(df))])
    return df


def exportar_resultado_ciclo(df_con_id: pd.DataFrame, carpeta_output: Path, ciclo_slug: str) -> Path:
    carpeta_output = Path(carpeta_output)
    carpeta_output.mkdir(parents=True, exist_ok=True)
    ruta = carpeta_output / f"resultado_{ciclo_slug}.xlsx"
    df_con_id.to_excel(ruta, index=False)
    return ruta


def actualizar_base_historica(df_con_id: pd.DataFrame, carpeta_output: Path) -> Path:
    """Agrega (o reemplaza si ya existia) el ciclo actual dentro de la base
    historica consolidada, para poder analizar 2010-2026 en conjunto."""
    carpeta_output = Path(carpeta_output)
    carpeta_output.mkdir(parents=True, exist_ok=True)
    ruta_historica = carpeta_output / "BASE_HISTORICA_ENRIQUECIDA.xlsx"

    columnas_presentes = [c for c in CAMPOS_HISTORICA if c in df_con_id.columns]
    df_nuevo = df_con_id[columnas_presentes].copy()

    if ruta_historica.exists():
        df_previo = pd.read_excel(ruta_historica, dtype=str)
        ciclo_actual = df_nuevo["ciclo"].iloc[0] if len(df_nuevo) else None
        if ciclo_actual is not None and "ciclo" in df_previo.columns:
            df_previo = df_previo[df_previo["ciclo"] != ciclo_actual]
        df_final = pd.concat([df_previo, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo

    df_final.to_excel(ruta_historica, index=False)
    return ruta_historica
