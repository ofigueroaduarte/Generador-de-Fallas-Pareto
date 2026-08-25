"""
app.py
------
App de Streamlit: simula datos de fallas y muestra un diagrama de Pareto
interactivo (frecuencia, costo o tiempo de paro).

Ejecutar con:
    streamlit run app.py
"""

import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from simulador_fallas import CATALOGO_FALLAS_DEFAULT, analisis_pareto, simular_fallas

st.set_page_config(page_title="Análisis de Pareto - Fallas", page_icon="📊", layout="wide")

st.title("📊 Simulador de Fallas y Análisis de Pareto")
st.caption(
    "Genera un histórico sintético de fallas y construye el diagrama de Pareto "
    "(80/20) por frecuencia, costo de reparación o tiempo de paro."
)

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
# Selección de la métrica de Pareto
# ---------------------------------------------------------------------------
col_metric, col_dim = st.columns(2)

with col_metric:
    metrica = st.selectbox(
        "Métrica para el Pareto",
        options=["Frecuencia (conteo de eventos)", "Costo de reparación (USD)", "Tiempo de paro (horas)"],
    )

with col_dim:
    dimension = st.selectbox(
        "Agrupar por",
        options=["tipo_falla", "area"],
        format_func=lambda x: "Tipo de falla" if x == "tipo_falla" else "Área / línea",
    )

columna_valor = None
if metrica.startswith("Costo"):
    columna_valor = "costo_reparacion_usd"
elif metrica.startswith("Tiempo"):
    columna_valor = "tiempo_paro_horas"

tabla_pareto = analisis_pareto(df, columna_categoria=dimension, columna_valor=columna_valor)

# ---------------------------------------------------------------------------
# KPIs rápidos
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total de eventos", f"{len(df):,}")
k2.metric("Categorías distintas", f"{df[dimension].nunique()}")

# Cuántas categorías explican el 80%
n_80 = (tabla_pareto["porcentaje_acumulado"] <= 80).sum() + 1
n_80 = min(n_80, len(tabla_pareto))
k3.metric("Categorías que explican ≥80%", f"{n_80} de {len(tabla_pareto)}")

k4.metric("Costo total simulado", f"${df['costo_reparacion_usd'].sum():,.0f}")

st.markdown("---")

# ---------------------------------------------------------------------------
# Gráfico de Pareto (barras de valor + línea de % acumulado)
# ---------------------------------------------------------------------------
st.subheader("Diagrama de Pareto")

fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.bar(tabla_pareto[dimension], tabla_pareto["valor"], color="#4C72B0")
ax1.set_xlabel("")
ax1.set_ylabel(metrica, color="#4C72B0")
ax1.tick_params(axis="y", labelcolor="#4C72B0")
plt.setp(ax1.get_xticklabels(), rotation=40, ha="right")

ax2 = ax1.twinx()
ax2.plot(
    tabla_pareto[dimension],
    tabla_pareto["porcentaje_acumulado"],
    color="#C44E52",
    marker="o",
    linewidth=2,
)
ax2.axhline(80, color="gray", linestyle="--", linewidth=1)
ax2.set_ylabel("% acumulado", color="#C44E52")
ax2.tick_params(axis="y", labelcolor="#C44E52")
ax2.set_ylim(0, 110)

fig.tight_layout()
st.pyplot(fig)

st.caption("La línea roja punteada marca el umbral del 80 %, referencia clásica del principio de Pareto.")

# ---------------------------------------------------------------------------
# Tabla de Pareto y datos crudos
# ---------------------------------------------------------------------------
st.subheader("Tabla de Pareto")
tabla_mostrar = tabla_pareto.rename(
    columns={
        dimension: "Categoría",
        "valor": metrica,
        "porcentaje": "% del total",
        "porcentaje_acumulado": "% acumulado",
    }
).round(2)
st.dataframe(tabla_mostrar, use_container_width=True, hide_index=True)

with st.expander("Ver datos crudos simulados"):
    st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Descargas
# ---------------------------------------------------------------------------
col_d1, col_d2 = st.columns(2)

csv_datos = df.to_csv(index=False).encode("utf-8")
col_d1.download_button(
    "⬇️ Descargar datos simulados (CSV)",
    data=csv_datos,
    file_name="fallas_simuladas.csv",
    mime="text/csv",
    use_container_width=True,
)

csv_pareto = tabla_mostrar.to_csv(index=False).encode("utf-8")
col_d2.download_button(
    "⬇️ Descargar tabla de Pareto (CSV)",
    data=csv_pareto,
    file_name="tabla_pareto.csv",
    mime="text/csv",
    use_container_width=True,
)
