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
# --- 2. FILTRO GLOBAL (SIDEBAR) ---
st.sidebar.header("Filtros")
proyectos = ["Todos"] + sorted(df_dashboard['proyecto'].unique().tolist())
proyecto_sel = st.sidebar.selectbox("Selecciona un Proyecto:", proyectos)

# Aplicamos el filtro
if proyecto_sel != "Todos":
    df_filtrado = df_dashboard[df_dashboard['proyecto'] == proyecto_sel]
else:
    df_filtrado = df_dashboard.copy()

# --- SECCIÓN 1: PANORAMA GENERAL ---
st.header("1. Panorama General de Inscritos")

# KPIs principales (Filtrados por proyecto seleccionado)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Inscritos", f"{len(df_filtrado):,}")
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

# Gráfico 1: Distribución por Ciudad (SÍ depende del filtro)
with c1:
    fig_ciudad = px.histogram(
        df_filtrado, 
        x='ciudad', 
        title="Distribución por Ciudad (Proyecto Seleccionado)", 
        color_discrete_sequence=['#636EFA']
    )
    fig_ciudad.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_ciudad, use_container_width=True)

# Gráfico 2: Distribución por Proyecto (NO depende del filtro - Vista Global)
with c2:
    # Usamos df_dashboard completo para este gráfico
    fig_proy_global = px.histogram(
        df_dashboard, 
        x='proyecto', 
        title="Volumen Total por Proyecto (Global)", 
        color_discrete_sequence=['#EF553B']
    )
    fig_proy_global.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_proy_global, use_container_width=True)
    
    
# --- SECCIÓN 2: DESEMPEÑO ACADÉMICO Y GRADUACIÓN ---
st.header("2. Desempeño Académico")

# Sub-sección 2.1: Tabla de Tasas de Graduación Corregidas
st.subheader("2.1. Tasa de Graduación por Proyecto y Canal")

# Filtramos la tabla de tasas si hay un proyecto seleccionado
if proyecto_sel != "Todos":
    df_tasas_view = df_tasas_corregidas[df_tasas_corregidas['proyecto'] == proyecto_sel]
else:
    df_tasas_view = df_tasas_corregidas.copy()

# Mostramos la tabla con los datos clave
st.dataframe(
    df_tasas_view[['proyecto', 'canal_convocatoria', 'total_inscritos', 'graduados_validados', 'tasa_graduacion_real']], 
    hide_index=True,
    use_container_width=True
)

# Sub-sección 2.2: Distribución de Estados y Avance
c3, c4 = st.columns(2)

with c3:
    # Gráfico de dona para ver el estado actual de los estudiantes filtrados
    fig_estado = px.pie(
        df_filtrado, 
        names='estado', 
        title="Distribución de Estados Actuales",
        hole=0.4, # Hace que sea una dona en lugar de un pastel completo
        color_discrete_map={'Activo': '#636EFA', 'Desertor': '#EF553B', 'Graduado': '#00CC96'}
    )
    st.plotly_chart(fig_estado, use_container_width=True)

with c4:
    # Boxplot para ver la dispersión del avance porcentual
    fig_avance = px.box(
        df_filtrado, 
        x='proyecto', 
        y='porcentaje_avance', 
        title="Distribución del % de Avance",
        color='proyecto'
    )
    st.plotly_chart(fig_avance, use_container_width=True)