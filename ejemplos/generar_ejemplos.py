"""Genera dos Excel de ejemplo con nombres de columna deliberadamente distintos,
para comprobar que la deteccion automatica funciona en ambos casos."""

from pathlib import Path
import pandas as pd

OUT = Path(__file__).resolve().parent

# --- Estilo "2023": columnas como las que aparecen en el documento original ---
df_2023 = pd.DataFrame({
    "Nombres": ["Ana Maria", "Luis", "Carla", "Jose", "Fiorella", "Renato", "Diana", "Marco", "Paola", "Sergio"],
    "Apellido Paterno": ["Torres", "Ramos", "Diaz", "Quispe", "Mendez", "Salas", "Rojas", "Vera", "Castro", "Leon"],
    "Apellido Materno": ["Gomez", "Vega", "Luna", "Rios", "Paredes", "Nunez", "Flores", "Ortiz", "Silva", "Campos"],
    "Colegio (5to de secundaria)": [
        "IE San Martin", "Colegio La Salle", "IE Jose Olaya", "Colegio Santa Rosa",
        "IE Peru Birf", "Colegio Los Andes", "IE Mariscal Caceres", "Colegio San Agustin",
        "IE Ricardo Palma", "Colegio Divino Maestro",
    ],
    "Carrera": [
        "Ingenieria de Sistemas", "Administracion", "Derecho", "Psicologia",
        "Ingenieria Civil", "Contabilidad", "Medicina", "Arquitectura",
        "Comunicaciones", "Economia",
    ],
    "Modalidad": ["Ordinario"] * 10,
    "App status Descripción": [
        "SELECCIONADO", "NO SELECCIONADO", "SELECCIONADO", "NO SELECCIONADO",
        "SELECCIONADO", "SELECCIONADO", "NO SELECCIONADO", "SELECCIONADO",
        "NO SELECCIONADO", "SELECCIONADO",
    ],
})
df_2023.to_excel(OUT / "Admision - Postulantes Pregrado 2023-1.xlsx", index=False)

# --- Estilo "2010": columnas antiguas, nombre en una sola columna ---
df_2010 = pd.DataFrame({
    "Nombre completo": [
        "Pedro Alarcon Vidal", "Maria Fernandez Soto", "Jorge Huaman Rios", "Lucia Ponce Diaz",
        "Cesar Vasquez Leon", "Rosa Chavez Mora", "Victor Aguilar Paz", "Elena Cardenas Ruiz",
        "Miguel Palacios Gil", "Sandra Espinoza Cruz",
    ],
    "Colegio procedencia": [
        "Colegio Nacional Bolivar", "IE Simon Bolivar", "Colegio Fe y Alegria",
        "IE 1234 San Jose", "Colegio Maria Auxiliadora", "IE Peru", "Colegio San Juan",
        "IE Santa Ana", "Colegio Salesiano", "IE Nuestra Senora",
    ],
    "Programa": [
        "Ingenieria Industrial", "Educacion", "Derecho", "Enfermeria",
        "Ingenieria de Sistemas", "Administracion", "Medicina Veterinaria",
        "Contabilidad", "Arquitectura", "Psicologia",
    ],
    "Estado postulante": [
        "Admitido", "No admitido", "Admitido", "No admitido",
        "Admitido", "No admitido", "Admitido", "Admitido",
        "No admitido", "Admitido",
    ],
})
df_2010.to_excel(OUT / "Base postulantes 2010.xlsx", index=False)

print("Generados:")
print(" -", OUT / "Admision - Postulantes Pregrado 2023-1.xlsx")
print(" -", OUT / "Base postulantes 2010.xlsx")
