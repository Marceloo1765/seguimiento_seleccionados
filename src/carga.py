"""
carga.py
--------
Responsable de:
  1. Leer el Excel subido (cualquier anio) hacia un DataFrame de pandas.
  2. Intentar detectar el "ciclo" (anio + semestre) a partir del nombre del archivo,
     para poder nombrar el resultado y el ID historico sin pedirselo siempre al usuario.

No asume nada sobre los nombres de columnas: eso lo hace deteccion_columnas.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Ciclo:
    anio: int | None
    semestre: str | None  # "I", "II" o None si no se pudo determinar

    @property
    def etiqueta(self) -> str:
        """Devuelve algo como '2023-I' o solo '2023' si no hay semestre."""
        if self.anio is None:
            return "CICLO_DESCONOCIDO"
        if self.semestre:
            return f"{self.anio}-{self.semestre}"
        return str(self.anio)

    @property
    def slug(self) -> str:
        """Version segura para nombres de archivo: '2023_I'."""
        if self.anio is None:
            return "ciclo_desconocido"
        if self.semestre:
            return f"{self.anio}_{self.semestre}"
        return str(self.anio)


_PATRON_ANIO = re.compile(r"(19|20)\d{2}")
# Semestre: "-1", "-2", "-I", "-II", "I-", "II-", "semestre 1", "S1", "S2", etc.
_PATRON_SEMESTRE_ROMANO = re.compile(r"\b(I{1,2})\b", re.IGNORECASE)
_PATRON_SEMESTRE_NUM = re.compile(r"[-_ ](\d)\b")


def detectar_ciclo(nombre_archivo: str) -> Ciclo:
    """Intenta extraer anio y semestre del nombre de archivo.

    Ejemplos que debe soportar:
      'Admision - Postulantes Pregrado 2023-1.xlsx' -> 2023, I
      'Admision - Postulantes Pregrado 2018-2.xlsx' -> 2018, II
      'Base postulantes 2010.xlsx' -> 2010, None
      '2023-II.xlsx' -> 2023, II
    """
    nombre = Path(nombre_archivo).stem

    anio = None
    m_anio = _PATRON_ANIO.search(nombre)
    if m_anio:
        anio = int(m_anio.group(0))

    semestre = None

    # 1) Buscar numero pegado al anio: "2023-1", "2023_2"
    m_num = re.search(r"(19|20)\d{2}[-_ ]?(1|2)\b", nombre)
    if m_num:
        semestre = "I" if m_num.group(2) == "1" else "II"

    # 2) Buscar numeral romano cerca del anio: "2023-I", "2023 II"
    if semestre is None:
        m_rom = re.search(r"(19|20)\d{2}[-_ ]?(I{1,2})\b", nombre, re.IGNORECASE)
        if m_rom:
            semestre = m_rom.group(2).upper()

    # 3) Ultimo recurso: cualquier "I" o "II" aislado en el nombre
    if semestre is None:
        m_rom2 = _PATRON_SEMESTRE_ROMANO.search(nombre)
        if m_rom2:
            semestre = m_rom2.group(1).upper()

    return Ciclo(anio=anio, semestre=semestre)


def cargar_excel(ruta_o_buffer, hoja: int | str = 0) -> pd.DataFrame:
    """Carga un Excel a DataFrame. Acepta ruta en disco o un buffer (p.ej. desde
    st.file_uploader). No modifica los datos, solo los lee.
    """
    df = pd.read_excel(ruta_o_buffer, sheet_name=hoja, dtype=str)
    # Quita filas y columnas completamente vacias que a veces quedan de plantillas
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    # Limpia espacios en los encabezados (comunes en exports de sistemas academicos)
    df.columns = [str(c).strip() for c in df.columns]
    return df.reset_index(drop=True)
