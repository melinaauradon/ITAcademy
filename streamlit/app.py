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
    """
    Análisis de canales de venta, campañas y categorías de producto.
    """
)

# =================================
# FILTROS
# =================================

st.sidebar.header("Filtros")

canales = ["Todos"] + sorted(
    df_full["channel"].dropna().unique().tolist()
)

categorias = ["Todos"] + sorted(
    df_full["merchant_category"].dropna().unique().tolist()
)

canal = st.sidebar.selectbox(
    "Canal",
    canales
)

categoria = st.sidebar.selectbox(
    "Categoría",
    categorias
)

# =================================
# FILTRADO
# =================================

df_filtrado = df_full.copy()

if canal != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["channel"] == canal
    ]

if categoria != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["merchant_category"] == categoria
    ]

# =================================
# KPIs
# =================================

st.subheader("Indicadores principales")

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
        "Descuento Medio",
        f"{df_filtrado['discount_amount'].mean():.2f} €"
    )

# =================================
# VISUALIZACIÓN 1
# FACTURACIÓN POR CANAL
# =================================

ventas_canal = (
    df_filtrado
    .groupby("channel")["amount"]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    ventas_canal,
    x="channel",
    y="amount",
    title="Facturación por canal"
)

st.plotly_chart(fig1, use_container_width=True)

# =================================
# VISUALIZACIÓN 2
# FACTURACIÓN POR CAMPAÑA
# =================================

ventas_campania = (
    df_filtrado
    .groupby("campaign_id")["amount"]
    .sum()
    .reset_index()
    .sort_values("amount", ascending=False)
)

fig2 = px.bar(
    ventas_campania,
    x="campaign_id",
    y="amount",
    title="Facturación por campaña"
)

st.plotly_chart(fig2, use_container_width=True)

# =================================
# VISUALIZACIÓN 3
# FACTURACIÓN POR CATEGORÍA
# =================================

ventas_categoria = (
    df_filtrado
    .groupby("merchant_category")["amount"]
    .sum()
    .reset_index()
    .sort_values("amount", ascending=False)
)

fig3 = px.bar(
    ventas_categoria,
    x="merchant_category",
    y="amount",
    title="Facturación por categoría"
)

st.plotly_chart(fig3, use_container_width=True)

# =================================
# VISUALIZACIÓN 4
# POSICIONAMIENTO DE PRECIO
# =================================

fig4 = px.box(
    df_filtrado,
    x="merchant_price_position",
    y="amount",
    title="Distribución de ventas por posicionamiento de precio"
)

st.plotly_chart(fig4, use_container_width=True)
