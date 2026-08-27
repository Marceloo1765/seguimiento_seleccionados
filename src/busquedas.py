"""
busquedas.py  (FASE 2 - todavia no implementado)
-------------------------------------------------
Este modulo generara, para cada seleccionado, los terminos/queries de
busqueda que luego usara matching.py para encontrarlo en una fuente externa
(por ejemplo un registro de matriculados de otra universidad o padron
publico). Se deja preparado como "siguiente paso" tal como se acordo:

  1) Primero validar que la deteccion de columnas y el filtrado funcionan
     bien con al menos dos bases de estructura distinta (ej. 2023 y 2010).
  2) Recien despues construir busquedas + matching, porque su diseno
     depende de CONTRA QUE FUENTE se va a buscar (que hoy no esta
     definida) y de que tan limpios llegan nombre_completo/colegio/carrera.

Cuando se defina la fuente de matching, esta funcion debera:
  - recibir el DataFrame de seleccionados ya normalizado
  - devolver, por fila, una o mas queries candidatas (ej. nombre + colegio,
    nombre + carrera, variantes sin segundo apellido, etc.)
"""

from __future__ import annotations

import pandas as pd


def generar_queries(df_seleccionados: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError(
        "Fase 2 pendiente: definir primero contra que fuente se hara el matching "
        "(nombre del sistema/base externa, formato de acceso, campos disponibles)."
    )
