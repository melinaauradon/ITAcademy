import pandas as pd
import streamlit as st
import plotly.express as px

# =====================
# CARGA DE DATOS
# =====================

df_full = pd.read_csv("sprint 9 - streamlit/df_full.csv")

# =====================
# TÍTULO
# =====================

st.title("Dashboard Comercial")

# =====================
# FILTROS
# =====================

pais = st.sidebar.selectbox(
    "País usuario",
    sorted(df_full["country_user"].unique())
)

# =====================
# DATAFRAME FILTRADO
# =====================

df_filtrado = df_full[
    df_full["country_user"] == pais
]

# =====================
# KPIs
# =====================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Facturación Total",
        f"{df_filtrado['amount'].sum():,.0f} €"
    )

with col2:
    st.metric(
        "Transacciones",
        df_filtrado["id_tx"].nunique()
    )

with col3:
    st.metric(
        "Ticket Medio",
        f"{df_filtrado['amount'].mean():.2f} €"
    )

# =====================
# GRÁFICO 1
# Facturación por segmento
