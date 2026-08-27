"""
app.py
------
Interfaz Streamlit del sistema de seguimiento de seleccionados.

Flujo (Fase 1, la que se acordo construir primero):
  1. Subir cualquier Excel de admision (2010-2026).
  2. Detectar automaticamente el ciclo (anio/semestre) desde el nombre del
     archivo, editable a mano.
  3. Detectar automaticamente las columnas (nombre, colegio, carrera,
     modalidad, estado) con similitud de texto; si hay dudas, mostrar
     selectbox para que el usuario corrija.
  4. Normalizar los datos y filtrar seleccionados.
  5. Mostrar el conteo (totales / seleccionados / pendientes) y una vista
     previa.
  6. Exportar resultado_<ciclo>.xlsx y, opcionalmente, sumarlo a la
     BASE_HISTORICA_ENRIQUECIDA.xlsx.

Correr con:  streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.carga import cargar_excel, detectar_ciclo
from src.deteccion_columnas import (
    aplicar_mapeo_manual,
    cargar_config,
    detectar_columnas,
)
from src.limpieza import normalizar_dataframe
from src.filtrado import filtrar_seleccionados, resumen_conteo
from src.exportacion import (
    actualizar_base_historica,
    exportar_resultado_ciclo,
    generar_ids_historicos,
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "data" / "output"

st.set_page_config(page_title="Seguimiento de Seleccionados", layout="wide")

st.title("📊 Sistema de Seguimiento de Seleccionados")
st.caption("Sube la base de cualquier ciclo de admisión (2010–2026) y procésala con el mismo flujo.")

config = cargar_config()
campos_cfg = config["campos"]
etiquetas_campo = {
    "nombre": "Nombre",
    "apellido_paterno": "Apellido paterno",
    "apellido_materno": "Apellido materno",
    "colegio": "Colegio",
    "carrera": "Carrera",
    "modalidad": "Modalidad",
    "estado": "Estado / resultado",
}

archivo = st.file_uploader("Arrastra tu archivo Excel aquí", type=["xlsx", "xls"])

if archivo is not None:
    ciclo = detectar_ciclo(archivo.name)

    col_a, col_b = st.columns(2)
    with col_a:
        anio_input = st.number_input(
            "Año detectado", value=ciclo.anio if ciclo.anio else 2023, step=1, min_value=1990, max_value=2100
        )
    with col_b:
        semestre_opciones = ["I", "II", "(sin semestre)"]
        semestre_default = ciclo.semestre if ciclo.semestre in ("I", "II") else "(sin semestre)"
        semestre_input = st.selectbox(
            "Semestre detectado", semestre_opciones, index=semestre_opciones.index(semestre_default)
        )

    semestre_final = None if semestre_input == "(sin semestre)" else semestre_input
    ciclo_slug = f"{int(anio_input)}_{semestre_final}" if semestre_final else str(int(anio_input))
    ciclo_etiqueta = f"{int(anio_input)}-{semestre_final}" if semestre_final else str(int(anio_input))

    df = cargar_excel(archivo)
    st.success(f"Archivo leído: {len(df)} filas, {len(df.columns)} columnas. Ciclo: **{ciclo_etiqueta}**")

    with st.expander("Ver columnas originales del archivo"):
        st.write(list(df.columns))

    # --- Deteccion automatica de columnas ---
    deteccion = detectar_columnas(df, config)

    st.subheader("Mapeo de columnas")
    st.caption(
        "El sistema intenta detectar automáticamente cada campo. Revisa y corrige "
        "los que tengan baja confianza (⚠️) antes de continuar."
    )

    opciones_columnas = ["(ninguna)"] + list(df.columns)
    correcciones = {}

    for campo in campos_cfg.keys():
        columna_detectada = deteccion.mapping.get(campo)
        confianza = deteccion.confianza.get(campo, 0.0)
        requerido = campos_cfg[campo].get("requerido", False)

        icono = "✅" if confianza >= 0.85 else ("⚠️" if confianza >= config.get("umbral_similitud", 0.6) else "❌")
        etiqueta = etiquetas_campo.get(campo, campo)
        etiqueta_mostrar = f"{icono} {etiqueta}" + (" *" if requerido else "")

        valor_default = columna_detectada if columna_detectada in df.columns else "(ninguna)"
        seleccion = st.selectbox(
            etiqueta_mostrar,
            opciones_columnas,
            index=opciones_columnas.index(valor_default),
            key=f"map_{campo}",
        )
        correcciones[campo] = None if seleccion == "(ninguna)" else seleccion

    deteccion = aplicar_mapeo_manual(deteccion, correcciones)

    campos_faltantes_requeridos = [
        c for c in deteccion.campos_faltantes
        if campos_cfg[c].get("requerido", False) and c != "apellido_paterno" and c != "apellido_materno"
    ]
    # nombre puede venir de apellidos+nombre o de nombre completo; solo bloquear si NINGUNO de nombre/apellidos esta mapeado
    tiene_algo_de_nombre = any(deteccion.mapping.get(c) for c in ("nombre", "apellido_paterno", "apellido_materno"))
    if not tiene_algo_de_nombre and "nombre" in campos_faltantes_requeridos:
        pass  # se queda en la lista, es un bloqueo real
    elif "nombre" in campos_faltantes_requeridos:
        campos_faltantes_requeridos.remove("nombre")

    if campos_faltantes_requeridos:
        st.error(
            "Faltan campos obligatorios por mapear: "
            + ", ".join(etiquetas_campo.get(c, c) for c in campos_faltantes_requeridos)
        )
        st.stop()

    st.divider()

    if st.button("🚀 Procesar base", type="primary"):
        df_norm = normalizar_dataframe(df, deteccion.mapping)

        valores_seleccionado = config.get("valores_seleccionado", [])
        df_seleccionados = filtrar_seleccionados(df_norm, valores_seleccionado)
        conteo = resumen_conteo(df_norm, df_seleccionados)

        st.subheader(f"Base procesada: {ciclo_etiqueta}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Registros totales", conteo["registros_totales"])
        c2.metric("Seleccionados", conteo["seleccionados"])
        c3.metric("No seleccionados", conteo["no_seleccionados"])

        if len(df_seleccionados) == 0:
            st.warning(
                "No se encontró ningún registro con estado de 'seleccionado'. "
                "Revisa el mapeo del campo Estado o los valores configurados en "
                "config/columnas.json → 'valores_seleccionado'."
            )
        else:
            df_con_id = generar_ids_historicos(df_seleccionados, ciclo_slug)

            columnas_preview = ["id_postulante", "nombre_completo", "colegio_norm", "carrera_norm", "modalidad_norm"]
            columnas_preview = [c for c in columnas_preview if c in df_con_id.columns]
            st.dataframe(df_con_id[columnas_preview], use_container_width=True)

            ruta_resultado = exportar_resultado_ciclo(df_con_id, OUTPUT_DIR, ciclo_slug)

            with open(ruta_resultado, "rb") as f:
                st.download_button(
                    "⬇️ Descargar resultado de este ciclo",
                    data=f.read(),
                    file_name=ruta_resultado.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            if st.button("➕ Agregar a la base histórica consolidada"):
                ruta_historica = actualizar_base_historica(df_con_id, OUTPUT_DIR)
                st.success(f"Base histórica actualizada: {ruta_historica.name}")
else:
    st.info("Sube un archivo Excel para comenzar.")
