"""
matching.py  (FASE 2 - todavia no implementado)
-------------------------------------------------
Tomara las queries generadas en busquedas.py, las cruzara contra la fuente
externa definida y calculara un score/confianza de coincidencia por
postulante (para poblar 'universidad_posterior', 'carrera_posterior',
'score', 'confianza' en la base historica).

Ver la nota en busquedas.py: se construye recien cuando la Fase 1
(deteccion de columnas + filtrado) este validada con al menos 2 ciclos
de estructura distinta.
"""

from __future__ import annotations

import pandas as pd


def ejecutar_matching(df_queries: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError(
        "Fase 2 pendiente: depende de busquedas.generar_queries y de la fuente "
        "externa contra la que se va a comparar."
    )
