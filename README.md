# Simulador de Fallas (Streamlit)

App web que **genera datos sintéticos** de fallas industriales (tipo de
falla, área, costo de reparación, tiempo de paro) para que los estudiantes
descarguen el archivo y construyan **ellos mismos** el diagrama de Pareto
en Excel (tabla dinámica, % y % acumulado, gráfico combinado).

La app deliberadamente **no calcula ni grafica el Pareto** — solo entrega
la materia prima (los datos).

## Archivos

- `simulador_fallas.py`: lógica pura (sin UI).
  - `simular_fallas(...)`: genera un DataFrame sintético de fallas.
  - `analisis_pareto(...)`: función de referencia para calcular frecuencia,
    % y % acumulado en Python — útil si el profesor quiere validar el
    resultado esperado, pero **no se usa dentro de `app.py`**.
- `app.py`: interfaz web hecha con Streamlit. Permite configurar la
  simulación y descargar los datos en CSV o Excel.
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
- Fijar una semilla (seed) para que el mismo grupo de estudiantes pueda
  reproducir exactamente el mismo dataset si es necesario.
- Ver una vista previa de los datos generados (tipo de falla, área, fecha,
  costo de reparación, tiempo de paro).
- Descargar los datos en **CSV** o **Excel (.xlsx)**.

## Ejercicio sugerido para los estudiantes (en Excel)

Con el archivo descargado, los estudiantes pueden:
1. Crear una **tabla dinámica** que cuente la frecuencia de cada `tipo_falla`
   (o sume `costo_reparacion_usd` / `tiempo_paro_horas`).
2. Ordenar de mayor a menor.
3. Calcular el **% del total** y el **% acumulado** con fórmulas.
4. Construir un gráfico combinado (barras + línea) para obtener el
   diagrama de Pareto y identificar los "pocos vitales".

## Validar el resultado esperado (opcional, para el profesor)

`simulador_fallas.py` incluye una función `analisis_pareto(...)` que replica
en Python lo que los estudiantes deben construir en Excel. No se usa dentro
de la app, pero sirve como referencia para verificar respuestas:

```python
import pandas as pd
from simulador_fallas import analisis_pareto

df = pd.read_excel("fallas_simuladas.xlsx")
tabla = analisis_pareto(df, columna_categoria="tipo_falla")
print(tabla)
```

## Despliegue en la nube (opcional)

Para publicar la app como una página web pública, la forma más simple es
[Streamlit Community Cloud](https://streamlit.io/cloud):
1. Sube esta carpeta a un repositorio de GitHub.
2. En Streamlit Community Cloud, conecta el repo y selecciona `app.py` como
   archivo principal.
3. La plataforma instala `requirements.txt` automáticamente y publica la URL.
