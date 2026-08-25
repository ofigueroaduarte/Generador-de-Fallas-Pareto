"""
simulador_fallas.py
--------------------
Genera un dataset sintético de fallas (equipos, líneas de producción, etc.)
y calcula la tabla de análisis de Pareto (frecuencia, % y % acumulado).

Pensado para ser usado tanto desde una app de Streamlit como desde
cualquier script de Python.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Catálogo por defecto de tipos de falla.
# El "peso" (probabilidad relativa) está pensado para que, al simular,
# el resultado se parezca a una distribución tipo 80/20 (pocas causas
# concentran la mayoría de las fallas), que es justo lo que un análisis
# de Pareto busca evidenciar.
#
# Cada tipo de falla también trae un rango de costo de reparación (USD)
# y de horas de paro, para poder hacer Pareto por frecuencia, por costo
# o por tiempo de paro.
# ---------------------------------------------------------------------------
CATALOGO_FALLAS_DEFAULT: Dict[str, dict] = {
    "Falla eléctrica":        {"peso": 0.30, "costo": (200, 900),  "paro_horas": (1, 6)},
    "Desgaste mecánico":      {"peso": 0.22, "costo": (150, 700),  "paro_horas": (2, 8)},
    "Error de operador":      {"peso": 0.15, "costo": (50, 300),   "paro_horas": (0.5, 3)},
    "Falta de lubricación":   {"peso": 0.10, "costo": (80, 400),   "paro_horas": (1, 4)},
    "Sobrecalentamiento":     {"peso": 0.08, "costo": (300, 1200), "paro_horas": (2, 10)},
    "Falla de sensor":        {"peso": 0.06, "costo": (100, 500),  "paro_horas": (0.5, 3)},
    "Corrosión":              {"peso": 0.04, "costo": (200, 800),  "paro_horas": (1, 5)},
    "Vibración excesiva":     {"peso": 0.03, "costo": (150, 600),  "paro_horas": (1, 4)},
    "Falla de software/PLC":  {"peso": 0.01, "costo": (100, 900),  "paro_horas": (0.5, 6)},
    "Otro":                   {"peso": 0.01, "costo": (50, 300),   "paro_horas": (0.5, 2)},
}


def simular_fallas(
    n_registros: int = 500,
    catalogo: Optional[Dict[str, dict]] = None,
    dias_rango: int = 90,
    fecha_inicio: Optional[datetime] = None,
    seed: Optional[int] = None,
) -> pd.DataFrame:
    """
    Simula un histórico de fallas.

    Parameters
    ----------
    n_registros : int
        Cantidad de eventos de falla a generar.
    catalogo : dict, opcional
        Diccionario {tipo_falla: {"peso":..., "costo":(min,max), "paro_horas":(min,max)}}.
        Si no se pasa, se usa CATALOGO_FALLAS_DEFAULT.
    dias_rango : int
        Ventana de días hacia atrás desde fecha_inicio + dias_rango en la que
        se distribuyen aleatoriamente las fechas de falla.
    fecha_inicio : datetime, opcional
        Fecha inicial del rango simulado. Por defecto, hoy - dias_rango.
    seed : int, opcional
        Semilla para reproducibilidad.

    Returns
    -------
    pd.DataFrame con columnas:
        id, fecha, tipo_falla, area, costo_reparacion_usd, tiempo_paro_horas
    """
    rng = np.random.default_rng(seed)

    catalogo = catalogo or CATALOGO_FALLAS_DEFAULT
    tipos = list(catalogo.keys())
    pesos = np.array([catalogo[t]["peso"] for t in tipos], dtype=float)
    pesos = pesos / pesos.sum()  # normalizar por si no suman 1

    if fecha_inicio is None:
        fecha_inicio = datetime.now() - timedelta(days=dias_rango)

    areas = ["Línea 1", "Línea 2", "Línea 3", "Mantenimiento General"]

    tipos_generados = rng.choice(tipos, size=n_registros, p=pesos)
    fechas = [fecha_inicio + timedelta(days=int(rng.integers(0, dias_rango + 1))) for _ in range(n_registros)]
    areas_generadas = rng.choice(areas, size=n_registros)

    costos = []
    paros = []
    for t in tipos_generados:
        c_min, c_max = catalogo[t]["costo"]
        p_min, p_max = catalogo[t]["paro_horas"]
        costos.append(round(rng.uniform(c_min, c_max), 2))
        paros.append(round(rng.uniform(p_min, p_max), 2))

    df = pd.DataFrame(
        {
            "id": range(1, n_registros + 1),
            "fecha": fechas,
            "tipo_falla": tipos_generados,
            "area": areas_generadas,
            "costo_reparacion_usd": costos,
            "tiempo_paro_horas": paros,
        }
    )

    return df.sort_values("fecha").reset_index(drop=True)


def analisis_pareto(
    df: pd.DataFrame,
    columna_categoria: str = "tipo_falla",
    columna_valor: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calcula la tabla de Pareto a partir de un DataFrame de fallas.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset de fallas (por ejemplo, el que devuelve simular_fallas()).
    columna_categoria : str
        Columna categórica a analizar (ej. "tipo_falla", "area").
    columna_valor : str, opcional
        Si es None, se hace Pareto por FRECUENCIA (conteo de eventos).
        Si se indica una columna numérica (ej. "costo_reparacion_usd" o
        "tiempo_paro_horas"), se hace Pareto por la SUMA de esa columna.

    Returns
    -------
    pd.DataFrame ordenado descendentemente con columnas:
        columna_categoria, valor, porcentaje, porcentaje_acumulado
    """
    if columna_valor is None:
        tabla = df[columna_categoria].value_counts().reset_index()
        tabla.columns = [columna_categoria, "valor"]
    else:
        tabla = (
            df.groupby(columna_categoria)[columna_valor]
            .sum()
            .reset_index()
            .rename(columns={columna_valor: "valor"})
        )

    tabla = tabla.sort_values("valor", ascending=False).reset_index(drop=True)
    total = tabla["valor"].sum()
    tabla["porcentaje"] = 100 * tabla["valor"] / total
    tabla["porcentaje_acumulado"] = tabla["porcentaje"].cumsum()

    return tabla


if __name__ == "__main__":
    # Prueba rápida por consola
    datos = simular_fallas(n_registros=500, seed=42)
    print(datos.head(), "\n")

    pareto_frecuencia = analisis_pareto(datos, "tipo_falla")
    print("=== Pareto por frecuencia ===")
    print(pareto_frecuencia, "\n")

    pareto_costo = analisis_pareto(datos, "tipo_falla", columna_valor="costo_reparacion_usd")
    print("=== Pareto por costo de reparación ===")
    print(pareto_costo)
