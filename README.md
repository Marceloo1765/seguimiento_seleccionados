# Sistema de Seguimiento de Seleccionados

Herramienta reutilizable para procesar bases de admisión de **cualquier ciclo (2010–2026)**
con el mismo flujo, sin reescribir código para cada año.

## Cómo correrlo

```bash
cd seguimiento_seleccionados
pip install -r requirements.txt
streamlit run app.py
```

Se abrirá en el navegador. Sube el Excel del ciclo que quieras procesar.

## Qué hace hoy (Fase 1 — completa y funcional)

1. **Detecta el ciclo** (año / semestre) a partir del nombre del archivo, editable a mano.
2. **Detecta las columnas** (nombre, colegio, carrera, modalidad, estado) aunque se llamen
   distinto en cada base, comparando contra los alias de `config/columnas.json`. Si no está
   seguro, te deja corregirlo con un selector antes de continuar.
3. **Normaliza los datos** (nombre completo, colegio, carrera, modalidad y estado sin tildes,
   en minúscula, espacios limpios) para que las mismas personas se puedan comparar entre años
   más adelante.
4. **Filtra a los seleccionados** según los valores configurados en
   `config/columnas.json → valores_seleccionado` (seleccionado, admitido, ingresante, apto,
   aceptado, matriculado — puedes agregar más sin tocar código).
5. Te muestra el conteo (totales / seleccionados / no seleccionados) y una vista previa.
6. **Exporta** `resultado_<ciclo>.xlsx` y, si quieres, lo suma a
   `BASE_HISTORICA_ENRIQUECIDA.xlsx`, usando un ID sin colisiones entre ciclos
   (ej. `2010_I_0001`, `2023_I_0001`).

## Qué falta (Fase 2 — a propósito no implementada todavía)

`src/busquedas.py`, `src/matching.py` y `src/validacion.py` están creados como los módulos
donde irá la búsqueda/cruce contra la fuente externa (para llenar `universidad_posterior`,
`carrera_posterior`, `score`, `confianza`), pero **quedan sin implementar**, tal como se
acordó: primero hay que validar que la detección de columnas y el filtrado funcionan bien con
al menos dos bases de estructura distinta (por ejemplo 2023 y 2010/2015). Recién con eso
probado, tiene sentido construir el matching — de lo contrario se corre el riesgo de construir
algo que funcione solo para 2023-I.

Para construir la Fase 2 hace falta definir:
- Contra qué fuente/base externa se va a buscar a cada seleccionado.
- Cómo se accede a esa fuente (¿otro Excel? ¿un sitio web? ¿una API?).
- Qué campos trae esa fuente para poder cruzarlos.

## Estructura del proyecto

```
seguimiento_seleccionados/
├── app.py                     # Interfaz Streamlit (Fase 1, funcional)
├── config/
│   └── columnas.json          # Alias de columnas + valores de "seleccionado" (editable sin código)
├── src/
│   ├── carga.py                # Lee el Excel y detecta año/semestre por nombre de archivo
│   ├── deteccion_columnas.py   # Motor de detección automática de columnas por similitud
│   ├── limpieza.py             # Normalización de nombre/colegio/carrera/modalidad/estado
│   ├── filtrado.py             # Filtra seleccionados + conteo
│   ├── exportacion.py          # ID histórico + guarda resultado y base histórica
│   ├── busquedas.py             # (Fase 2, pendiente)
│   ├── matching.py              # (Fase 2, pendiente)
│   └── validacion.py            # (Fase 2, pendiente)
├── data/
│   ├── input/                 # (opcional) para dejar excels de prueba
│   ├── processing/            # (reservado para archivos intermedios de Fase 2)
│   └── output/                # resultado_<ciclo>.xlsx y BASE_HISTORICA_ENRIQUECIDA.xlsx
└── ejemplos/
    ├── generar_ejemplos.py    # Genera 2 excels sintéticos con estructuras distintas
    ├── Admision - Postulantes Pregrado 2023-1.xlsx
    └── Base postulantes 2010.xlsx
```

## Cómo agregar/ajustar el reconocimiento de una base nueva

Si subes una base y algún campo no se detecta bien, no hace falta tocar el código:
abre `config/columnas.json` y agrega el nombre exacto de la columna (en minúscula, sin
tildes) a la lista `alias` del campo correspondiente. Por ejemplo, si una base de 2012 usa
`"Colegio procedencia"`, ya está cubierto; si usara `"IE de origen"`, agregarías
`"ie de origen"` a los alias de `"colegio"`.

## Probar que funciona con dos estructuras distintas

En `ejemplos/` hay dos archivos sintéticos con nombres de columna deliberadamente distintos
(uno simula el estilo 2023, el otro un estilo antiguo tipo 2010) para comprobar que el mismo
flujo los detecta a ambos correctamente antes de subir datos reales. Súbelos a la app uno
por uno y compara el mapeo detectado.
