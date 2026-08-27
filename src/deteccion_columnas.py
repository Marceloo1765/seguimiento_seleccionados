"""
deteccion_columnas.py
----------------------
El corazon de la reutilizacion entre anios: dado un DataFrame con columnas
desconocidas, intenta mapear cada columna real a un "campo canonico"
(nombre, colegio, carrera, modalidad, estado, etc.) usando la lista de alias
definida en config/columnas.json y similitud de texto (difflib).

Si no logra decidir con confianza, deja el campo sin mapear para que la
interfaz se lo pregunte al usuario (no adivina a ciegas).
"""

from __future__ import annotations

import difflib
import json
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "columnas.json"


def normalizar_texto(texto: str) -> str:
    """minusculas, sin tildes, sin espacios repetidos. Se usa tanto para
    encabezados de columnas como para valores dentro de las celdas."""
    if texto is None:
        return ""
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = " ".join(texto.split())
    return texto


def cargar_config(ruta: Path = CONFIG_PATH) -> dict:
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class ResultadoDeteccion:
    mapping: dict[str, str | None] = field(default_factory=dict)   # campo -> columna real (o None)
    confianza: dict[str, float] = field(default_factory=dict)      # campo -> score 0-1
    columnas_sin_usar: list[str] = field(default_factory=list)
    campos_faltantes: list[str] = field(default_factory=list)      # requeridos que no se detectaron


def _mejor_columna_para_campo(alias: list[str], columnas_normalizadas: dict[str, str]) -> tuple[str | None, float]:
    """columnas_normalizadas: {columna_real: columna_normalizada}
    Devuelve (columna_real_elegida, score) usando el mejor match contra la lista de alias.
    """
    mejor_columna = None
    mejor_score = 0.0
    for columna_real, columna_norm in columnas_normalizadas.items():
        for a in alias:
            a_norm = normalizar_texto(a)
            # 1) match exacto normalizado -> score perfecto
            if columna_norm == a_norm:
                return columna_real, 1.0
            # 2) uno contiene al otro (ej. "colegio" dentro de "colegio de procedencia")
            if a_norm in columna_norm or columna_norm in a_norm:
                score = 0.9
            else:
                score = difflib.SequenceMatcher(None, columna_norm, a_norm).ratio()
            if score > mejor_score:
                mejor_score = score
                mejor_columna = columna_real
    return mejor_columna, mejor_score


def detectar_columnas(df: pd.DataFrame, config: dict | None = None) -> ResultadoDeteccion:
    if config is None:
        config = cargar_config()

    umbral = config.get("umbral_similitud", 0.6)
    campos_cfg = config["campos"]

    columnas_normalizadas = {c: normalizar_texto(c) for c in df.columns}
    columnas_disponibles = dict(columnas_normalizadas)  # copia para ir "consumiendo" columnas ya asignadas

    resultado = ResultadoDeteccion()

    # Se procesan primero los campos requeridos para que se queden con las mejores columnas
    campos_ordenados = sorted(campos_cfg.items(), key=lambda kv: not kv[1].get("requerido", False))

    for campo, cfg_campo in campos_ordenados:
        alias = cfg_campo.get("alias", [])
        columna_elegida, score = _mejor_columna_para_campo(alias, columnas_disponibles)

        if columna_elegida is not None and score >= umbral:
            resultado.mapping[campo] = columna_elegida
            resultado.confianza[campo] = round(score, 2)
            # ya no ofrecer esta columna para otro campo
            columnas_disponibles.pop(columna_elegida, None)
        else:
            resultado.mapping[campo] = None
            resultado.confianza[campo] = round(score, 2)
            if cfg_campo.get("requerido", False):
                resultado.campos_faltantes.append(campo)

    resultado.columnas_sin_usar = list(columnas_disponibles.keys())
    return resultado


def aplicar_mapeo_manual(resultado: ResultadoDeteccion, correcciones: dict[str, str | None]) -> ResultadoDeteccion:
    """Permite que la interfaz (Streamlit) sobreescriba el mapeo automatico
    cuando el usuario corrige algo manualmente en un selectbox."""
    for campo, columna in correcciones.items():
        resultado.mapping[campo] = columna
        resultado.confianza[campo] = 1.0 if columna else 0.0
    # recalcular campos_faltantes tras la correccion
    resultado.campos_faltantes = [
        campo for campo, columna in resultado.mapping.items() if columna is None
    ]
    return resultado
