"""
app.py
------
App de Streamlit: simula un histórico de fallas y lo deja disponible para
descargar (CSV / Excel). Esta app NO calcula ni grafica el Pareto: esa parte
la hacen los estudiantes en Excel a partir de los datos generados aquí.

Ejecutar con:
    streamlit run app.py
"""

import io

import pandas as pd
import streamlit as st

from simulador_fallas import CATALOGO_FALLAS_DEFAULT, simular_fallas

st.set_page_config(page_title="Simulador de Fallas", page_icon="🛠️", layout="wide")

# ---------------------------------------------------------------------------
# Barra lateral: parámetros de la simulación
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Parámetros de simulación")

n_registros = st.sidebar.slider("Cantidad de fallas a simular", 50, 5000, 500, step=50)
dias_rango = st.sidebar.slider("Ventana de tiempo (días)", 7, 365, 90, step=7)
seed = st.sidebar.number_input("Semilla aleatoria (seed)", min_value=0, value=42, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Tipos de falla incluidos")
tipos_disponibles = list(CATALOGO_FALLAS_DEFAULT.keys())
tipos_seleccionados = st.sidebar.multiselect(
    "Selecciona qué tipos de falla simular",
    options=tipos_disponibles,
    default=tipos_disponibles,
)

if not tipos_seleccionados:
    st.sidebar.warning("Selecciona al menos un tipo de falla.")
    st.stop()

catalogo_filtrado = {k: v for k, v in CATALOGO_FALLAS_DEFAULT.items() if k in tipos_seleccionados}

st.sidebar.markdown("---")
regenerar = st.sidebar.button("🔄 Regenerar datos", use_container_width=True)

# ---------------------------------------------------------------------------
# Generar (o regenerar) los datos y guardarlos en session_state para que
# no se recalculen en cada interacción de la UI que no sea "Regenerar".
# ---------------------------------------------------------------------------
if "df_fallas" not in st.session_state or regenerar:
    st.session_state.df_fallas = simular_fallas(
        n_registros=n_registros,
        catalogo=catalogo_filtrado,
        dias_rango=dias_rango,
        seed=int(seed),
    )

df = st.session_state.df_fallas

# ---------------------------------------------------------------------------
# Resumen básico de lo generado (sin adelantar ningún resultado de Pareto)
# ---------------------------------------------------------------------------
k1, k2, k3 = st.columns(3)
k1.metric("Registros generados", f"{len(df):,}")
k2.metric("Tipos de falla incluidos", f"{df['tipo_falla'].nunique()}")
k3.metric("Rango de fechas", f"{df['fecha'].min().date()} → {df['fecha'].max().date()}")

st.markdown("---")

# ---------------------------------------------------------------------------
# Datos crudos generados
# ---------------------------------------------------------------------------
st.subheader("Datos de fallas simulados")
st.caption(
    "Estos son los datos crudos. Descárgalos y usa tablas dinámicas / fórmulas "
    "en Excel para construir tu propio diagrama de Pareto (frecuencia, % y % acumulado)."
)
st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Descargas
# ---------------------------------------------------------------------------
st.subheader("Descargar")

col_d1, col_d2 = st.columns(2)

csv_datos = df.to_csv(index=False).encode("utf-8")
col_d1.download_button(
    "⬇️ Descargar como CSV",
    data=csv_datos,
    file_name="fallas_simuladas.csv",
    mime="text/csv",
    use_container_width=True,
)

buffer_excel = io.BytesIO()
with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="fallas_simuladas")
buffer_excel.seek(0)

col_d2.download_button(
    "⬇️ Descargar como Excel (.xlsx)",
    data=buffer_excel,
    file_name="fallas_simuladas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
