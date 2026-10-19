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
    Análisis de ventas por campaña y categoría de producto.
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

# Filtro de Campaña
campanas = ["Todos"] + sorted(
    df_full["campaign_id"].dropna().unique().tolist()
)
campana = st.sidebar.selectbox(
    "Campaña",
    campanas
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

# B) Aplicar filtro de Campaña
if campana != "Todos":
    df_filtrado = df_filtrado[df_filtrado["campaign_id"] == campana]

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

# Agrupamos por campaña y canal simultáneamente
ventas_canal_campania = (
    df_filtrado[df_filtrado["campaign_id"] != "NO_CAMPAIGN"]
    .groupby(["campaign_id", "channel"])["amount"]
    .sum()
    .reset_index()
    .sort_values("amount", ascending=False)
)

fig1 = px.bar(
    ventas_canal_campania,
    x="campaign_id",
    y="amount",
    color="channel",  # segmenta la barra por colores de canal
    title="Análisis Omnicanal: Distribución de Campañas por Canal de Venta",
    labels={
        "campaign_id": "Campaña",
        "amount": "Facturación (€)",
        "channel": "Canal de Venta"
    },
    barmode="relative" # Permite ver el total de la campaña y su composición interna
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

ticket_categoria = (
    df_filtrado
    .groupby('merchant_category')['amount']
    .agg(['min', 'max'])
    .reset_index()
)

fig4 = px.bar(
    ticket_categoria,
    x='merchant_category',
    y=['min', 'max'],
    barmode='group',
    labels={'merchant_category': 'Categoría', 'value': 'Importe ($)', 'variable': 'Métrica'},
    title='Importes por Categoría'
)

st.plotly_chart(fig4, use_container_width=True)


# =================================
# VISUALIZACIÓN 5
# TICKET MEDIO POR CAMPAÑA
# =================================

ticket_campana = (
    df_filtrado
    .groupby("campaign_id")["amount"]
    .mean()
    .reset_index()
)

ticket_campana = ticket_campana[
    ticket_campana["campaign_id"] != "NO_CAMPAIGN"
]

ticket_campana = ticket_campana.sort_values(
    "amount",
    ascending=False
)

fig5 = px.bar(
    ticket_campana,
    x="campaign_id",
    y="amount",
    title="Ticket medio por campaña",
    labels={
        "campaign_id": "Campaña",
        "amount": "Ticket medio (€)"
    }
)

st.plotly_chart(fig5, use_container_width=True)
