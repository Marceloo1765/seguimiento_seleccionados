"""
filtrado.py
-----------
A partir del DataFrame ya normalizado (ver limpieza.py), separa a los
postulantes que quedaron "seleccionados" segun la columna de estado,
usando la lista configurable de valores positivos en config/columnas.json
(ej. seleccionado, admitido, ingresante, apto, aceptado, matriculado).

Es tolerante a variaciones de redaccion porque compara contra 'estado_norm'
(ya sin tildes, en minuscula) con coincidencia parcial, no exacta.
"""

from __future__ import annotations

import re

import pandas as pd

# Prefijos que niegan la palabra que sigue (ej. "no seleccionado", "sin admitir").
# Sin esto, "NO SELECCIONADO" haria match con el valor positivo "seleccionado"
# porque lo contiene como subcadena.
_PREFIJOS_NEGACION = ("no ", "sin ", "non ")


def filtrar_seleccionados(df_normalizado: pd.DataFrame, valores_seleccionado: list[str]) -> pd.DataFrame:
    if "estado_norm" not in df_normalizado.columns:
        raise ValueError("El DataFrame debe pasar primero por limpieza.normalizar_dataframe")

    valores_norm = [v.lower() for v in valores_seleccionado]

    def es_seleccionado(estado_valor: str) -> bool:
        estado_valor = estado_valor.strip()
        for valor in valores_norm:
            # Busca la palabra/frase como token completo (no como subcadena de otra palabra)
            patron = r"(?<!\w)" + re.escape(valor) + r"(?!\w)"
            for match in re.finditer(patron, estado_valor):
                inicio = match.start()
                # Si justo antes del match hay un prefijo de negacion, no cuenta como seleccionado
                fragmento_previo = estado_valor[max(0, inicio - 5):inicio]
                if any(fragmento_previo.endswith(neg) for neg in _PREFIJOS_NEGACION):
                    continue
                return True
        return False

    mascara = df_normalizado["estado_norm"].map(es_seleccionado)
    return df_normalizado[mascara].reset_index(drop=True)


def resumen_conteo(df_normalizado: pd.DataFrame, df_seleccionados: pd.DataFrame) -> dict:
    return {
        "registros_totales": len(df_normalizado),
        "seleccionados": len(df_seleccionados),
        "no_seleccionados": len(df_normalizado) - len(df_seleccionados),
    }
