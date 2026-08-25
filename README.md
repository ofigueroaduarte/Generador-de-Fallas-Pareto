# Simulador de Fallas + Análisis de Pareto (Streamlit)

App web para simular un histórico de fallas industriales y construir el
diagrama de Pareto (regla 80/20) por **frecuencia**, **costo de reparación**
o **tiempo de paro**.

## Archivos

- `simulador_fallas.py`: lógica pura (sin UI).
  - `simular_fallas(...)`: genera un DataFrame sintético de fallas.
  - `analisis_pareto(...)`: calcula frecuencia, % y % acumulado.
- `app.py`: interfaz web hecha con Streamlit que usa las funciones anteriores.
- `requirements.txt`: dependencias.

## Cómo correrlo localmente

```bash
# 1. Crear un entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
streamlit run app.py
```

Streamlit abrirá automáticamente el navegador en `http://localhost:8501`.

## Qué puedes hacer en la app

- Ajustar cuántas fallas simular y en qué ventana de tiempo (días).
- Elegir qué tipos de falla incluir en la simulación.
- Elegir la métrica del Pareto: frecuencia, costo o tiempo de paro.
- Agrupar por tipo de falla o por área/línea.
- Ver el diagrama de Pareto (barras + curva de % acumulado con línea del 80%).
- Ver cuántas categorías explican el 80% de los problemas (el "pocos vitales").
- Descargar tanto los datos simulados como la tabla de Pareto en CSV.

## Usar tus propios datos en vez de datos simulados

Si más adelante quieres reemplazar la simulación por datos reales, solo
necesitas un DataFrame de pandas con una columna categórica (ej. `tipo_falla`)
y, opcionalmente, una columna numérica (costo, horas de paro, etc.). Se lo
pasas directamente a `analisis_pareto()`:

```python
import pandas as pd
from simulador_fallas import analisis_pareto

df_real = pd.read_csv("mis_fallas_reales.csv")
tabla = analisis_pareto(df_real, columna_categoria="tipo_falla")
```

También podrías añadir un `st.file_uploader` en `app.py` para permitir subir
un CSV propio en lugar de simular datos.

## Despliegue en la nube (opcional)

Para publicar la app como una página web pública, la forma más simple es
[Streamlit Community Cloud](https://streamlit.io/cloud):
1. Sube esta carpeta a un repositorio de GitHub.
2. En Streamlit Community Cloud, conecta el repo y selecciona `app.py` como
   archivo principal.
3. La plataforma instala `requirements.txt` automáticamente y publica la URL.
