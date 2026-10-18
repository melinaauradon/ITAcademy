import pandas as pd
import streamlit as st
import plotly.express as px

# ==========================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================

st.set_page_config(
    page_title="Dashboard Comercial",
    layout="wide"
)

# ==========================
# CARGA DE DATOS
# ==========================

df_full = pd.read_csv("streamlit/df_full.csv")

# ==========================
# TÍTULO
# ==========================

st.title("📊 Dashboard Comercial")

st.markdown(
    """
    Análisis comercial de ventas, clientes y comportamiento de compra.
    """
)

# ==========================
# FILTROS
# ==========================

st.sidebar.header("Filtros")

pais = st.sidebar.selectbox(
    "País usuario",
    sorted(df_full["country_user"].dropna().unique())
)

segmento = st.sidebar.selectbox(
    "Segmento de usuario",
    sorted(df_full["user_segment"].dropna().unique())
)

# ==========================
# FILTRADO
# ==========================

df_filtrado = df_full[
    (df_full["country_user"] == pais)
    &
    (df_full["user_segment"] == segmento)
]

# ==========================
# KPIs
# ==========================

st.subheader("Indicadores principales")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Facturación Total",
        f"{df_filtrado['amount'].sum():,.0f} €"
    )

with col2:
    st.metric(
        "Nº Transacciones",
        df_filtrado["id_tx"].nunique()
    )

with col3:
    st.metric(
        "Ticket Medio",
        f"{df_filtrado['amount'].mean():.2f} €"
    )

# ================
