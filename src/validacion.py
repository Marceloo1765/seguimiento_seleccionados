"""
validacion.py  (FASE 2 - todavia no implementado)
---------------------------------------------------
Revisara los resultados de matching.py y marcara cada match como
confiable / dudoso / descartado segun el score, para que un humano solo
tenga que revisar los casos dudosos en vez de todos.
"""

from __future__ import annotations

import pandas as pd


def validar_matches(df_matches: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError(
        "Fase 2 pendiente: depende de matching.ejecutar_matching."
    )
