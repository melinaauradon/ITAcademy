import pandas as pd
import streamlit as st
import plotly.express as px

# =================================
# CONFIGURACIÓN
# =================================

st.set_page_config(
    page_title="Dashboard Comercial",
    layout="wide"
)

# =================================
# CARGA DE DATOS
# =================================

df_full = pd.read_csv("streamlit/df_full.csv")

# =================================
# TÍTULO
# =================================

st.title("📊 Dashboard Comercial")

st.markdown(
    "Análisis comercial de ventas, clientes y comportamiento de compra."
)

# =================================
# FILTROS
# =================================

st.sidebar.header("Filtros")

paises = ["Todos"] + sorted(
    df_full["country_user"].dropna().unique().tolist()
)

segmentos = ["Todos"] + sorted(
    df_full["user_segment"].dropna().unique().tolist()
)

pais = st.sidebar.selectbox(
    "País usuario",
    paises
)

segmento = st.sidebar.selectbox(
    "Segmento usuario",
    segmentos
)

# =================================
# FILTRADO
# =================================

df_filtrado = df_full.copy()

if pais != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["country_user"] == pais
    ]

if segmento != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["user_segment"] == segmento
    ]

# =================================
# KPIs
# =================================

st.subheader("Indicadores principales")

col1, col2, col3 = st.columns(3)
