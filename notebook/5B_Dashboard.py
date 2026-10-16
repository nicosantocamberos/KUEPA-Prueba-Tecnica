from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


ROOT_DIR = Path(__file__).resolve().parent.parent # __file__ asegura que la ruta sea relativa al script
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"


DF_DASHBOARD = PROCESSED_DATA_DIR / "df_dashboard.parquet"
DF_TASAS = PROCESSED_DATA_DIR / "df_tasas_corregidas.parquet"
DF_EMPLEABILIDAD = PROCESSED_DATA_DIR / "df_empleabilidad_resumen.parquet"


df_dashboard = pd.read_parquet(DF_DASHBOARD)
df_tasas_corregidas = pd.read_parquet(DF_TASAS)
df_empleabilidad_resumen = pd.read_parquet(DF_EMPLEABILIDAD)

# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---
st.set_page_config(page_title="Dashboard Kuepa", layout="wide")
st.title("Dashboard de Seguimiento - Kuepa EFE")

# --- 2. FILTRO GLOBAL ---
st.sidebar.header("Filtros de Análisis")
proyectos = ["Todos"] + sorted(df_dashboard['proyecto'].unique().tolist())
proyecto_sel = st.sidebar.selectbox("Selecciona un Proyecto:", proyectos)

if proyecto_sel != "Todos":
    df_filtrado = df_dashboard[df_dashboard['proyecto'] == proyecto_sel]
else:
    df_filtrado = df_dashboard.copy()

# --- SECCIÓN 1: PANORAMA GENERAL (KPIs + Distribución) ---
st.header("1. Estado Actual de la Cartera")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Inscritos", f"{len(df_filtrado):,}")
with col2: 
    activos = len(df_filtrado[df_filtrado['estado'] == 'Activo'])
    st.metric("Estudiantes Activos", f"{activos:,}")
with col3: 
    desertores = len(df_filtrado[df_filtrado['estado'] == 'Desertor'])
    st.metric("Desertores", f"{desertores:,}")
with col4: 
    graduados_val = int(df_filtrado['es_graduado_validado'].sum())
    st.metric("Graduados Validados", f"{graduados_val:,}")

c1, c2 = st.columns(2)
with c1:
    fig_ciudad = px.histogram(df_filtrado, x='ciudad', title="Distribución por Ciudad", color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig_ciudad, use_container_width=True)
with c2:
    fig_proy = px.histogram(df_dashboard, x='proyecto', title="Volumen Total por Proyecto (Global)", color_discrete_sequence=['#EF553B'])
    st.plotly_chart(fig_proy, use_container_width=True)

# --- SECCIÓN 2: ACCIÓN Y RESULTADOS (Riesgo + Graduation Rates) ---
st.header("2. Gestión de Riesgo y Resultados Académicos")

# Sub-sección A: Tabla de Estudiantes en Riesgo (Lo más importante para el gestor)
st.subheader(" Estudiantes en Riesgo de Deserción (Prioridad de Contacto)")

r1, r2 = st.columns(2)
with r1:
    umbral_avance = st.slider("Avance Máximo (%)", 0, 100, 50)
with r2:
    umbral_dias = st.slider("Días sin Conexión Mínimos", 0, 90, 10)

# Lógica de riesgo: Activo + (Bajo avance O muchos días sin conexión)
df_riesgo = df_filtrado[
    (df_filtrado['estado'] == 'Activo') & 
    ((df_filtrado['porcentaje_avance'] < umbral_avance) | (df_filtrado['dias_sin_conexion'] > umbral_dias))
]

st.info(f"Se identificaron **{len(df_riesgo)}** estudiantes que requieren intervención inmediata.")

if not df_riesgo.empty:
    # Mostramos solo las columnas relevantes para la acción
    cols_riesgo = ['nombre', 'proyecto', 'gestor', 'celular', 'porcentaje_avance', 'dias_sin_conexion']
    st.dataframe(df_riesgo.sort_values(by='dias_sin_conexion', ascending=False)[cols_riesgo], hide_index=True, use_container_width=True)
else:
    st.success("No hay estudiantes en riesgo con los filtros actuales.")

# Sub-sección B: Tasas de Graduación Corregidas (Validación de 3 campos)
st.subheader("Tasa de Graduación Real por Canal")
df_tasas_view = df_tasas_corregidas[df_tasas_corregidas['proyecto'].isin(df_filtrado['proyecto'].unique())] if proyecto_sel != "Todos" else df_tasas_corregidas

st.dataframe(
    df_tasas_view[['proyecto', 'canal_convocatoria', 'total_inscritos', 'tasa_graduacion_real']], 
    hide_index=True, 
    use_container_width=True
)