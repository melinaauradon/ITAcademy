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

st.title(" Dashboard Comercial")

st.markdown(
    """
    Análisis de ventas por canal, campaña y categoría de producto.
    """
)
# =================================
# FILTROS
# =================================

st.sidebar.header("Filtros")

# 1. Filtro de Tiempo (Rango de fechas)

timestamp_datetime = pd.to_datetime(df_full["timestamp"], errors="coerce")

fecha_minima = timestamp_datetime.min().date()
fecha_maxima = timestamp_datetime.max().date()


rango_fechas = st.sidebar.date_input(
    "Rango de Fechas",
    value=(fecha_minima, fecha_maxima), # Por defecto muestra todo el rango
    min_value=fecha_minima,
    max_value=fecha_maxima,
)

# Filtro de Canal
canales = ["Todos"] + sorted(
    df_full["channel"].dropna().unique().tolist()
)
canal = st.sidebar.selectbox(
    "Canal",
    canales
)

# Filtro de Categoría
categorias = ["Todos"] + sorted(
    df_full["merchant_category"].dropna().unique().tolist()
)
categoria = st.sidebar.selectbox(
    "Categoría",
    categorias
)


# =================================
# APLICACIÓN DE LOS FILTROS
# =================================

# Creamos una copia para no modificar el dataframe original
df_filtrado = df_full.copy()

# A) Aplicar filtro de fechas (solo si el usuario seleccionó inicio y fin)
df_filtrado["timestamp"] = pd.to_datetime(df_filtrado["timestamp"], errors="coerce")
if len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df_filtrado = df_filtrado[
        (df_filtrado["timestamp"].dt.date >= fecha_inicio) & 
        (df_filtrado["timestamp"].dt.date <= fecha_fin)
    ]

# B) Aplicar filtro de Canal
if canal != "Todos":
    df_filtrado = df_filtrado[df_filtrado["channel"] == canal]

# C) Aplicar filtro de Categoría
if categoria != "Todos":
    df_filtrado = df_filtrado[df_filtrado["merchant_category"] == categoria]

# =================================
# KPIS
# =================================

st.subheader("Indicadores principales")

# 1. Calculamos la facturación total primero
facturacion = df_filtrado['amount'].sum()

# --- RENDERIZADO EN COLUMNAS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Facturación Total",
        f"{facturacion:,.0f} €"
    )

with col2:
    # Guardamos el ticket medio en una variable
    ticket_medio = df_filtrado['amount'].sum() / df_filtrado['id_tx'].nunique() if df_filtrado['id_tx'].nunique() > 0 else 0

    st.metric(
        "Ticket Medio",
        f"{ticket_medio:,.2f} €"
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
    .sort_values("amount", ascending=False)
)

fig1 = px.bar(
    ventas_canal,
    x="channel",
    y="amount",
    title="Facturación por canal",
    labels={
        "channel": "Canal",
        "amount": "Facturación (€)"
    }
)

fig1.update_traces(
    texttemplate="%{y:,.0f}",
    textposition="outside"
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
)

# eliminamos campañas nulas
ventas_campania = ventas_campania[
    ventas_campania["campaign_id"] != "NO_CAMPAIGN"
]

ventas_campania = ventas_campania.sort_values(
    "amount",
    ascending=False
)

fig2 = px.bar(
    ventas_campania,
    x="campaign_id",
    y="amount",
    title="Facturación por campaña",
    labels={
        "campaign_id": "Campaña",
        "amount": "Facturación (€)"
    }
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
    title="Facturación por categoría",
    labels={
        "merchant_category": "Categoría",
        "amount": "Facturación (€)"
    }
)

st.plotly_chart(fig3, use_container_width=True)

# =================================
# VISUALIZACIÓN 4
# TICKET MEDIO POR CAMPAÑA
# =================================

ticket_campania = (
    df_filtrado
    .groupby("campaign_id")["amount"]
    .mean()
    .reset_index()
)

ticket_campania = ticket_campania[
    ticket_campania["campaign_id"] != "NO_CAMPAIGN"
]

ticket_campania = ticket_campania.sort_values(
    "amount",
    ascending=False
)

fig4 = px.bar(
    ticket_campania,
    x="campaign_id",
    y="amount",
    title="Ticket medio por campaña",
    labels={
        "campaign_id": "Campaña",
        "amount": "Ticket medio (€)"
    }
)

st.plotly_chart(fig4, use_container_width=True)
