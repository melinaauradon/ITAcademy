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

# =================================
# VISUALIZACIÓN 1
# FACTURACIÓN POR PAÍS
# =================================

ventas_pais = (
    df_filtrado
    .groupby("country_user")["amount"]
    .sum()
    .reset_index()
    .sort_values("amount", ascending=False)
)

fig1 = px.bar(
    ventas_pais,
    x="country_user",
    y="amount",
    title="Facturación por país"
)

st.plotly_chart(fig1, use_container_width=True)

# =================================
# VISUALIZACIÓN 2
# FACTURACIÓN POR SEGMENTO
# =================================

ventas_segmento = (
    df_filtrado
    .groupby("user_segment")["amount"]
    .sum()
    .reset_index()
)

fig2 = px.bar(
    ventas_segmento,
    x="user_segment",
    y="amount",
    title="Facturación por segmento"
)

st.plotly_chart(fig2, use_container_width=True)

# =================================
# VISUALIZACIÓN 3
# LOCAL VS INTERNACIONAL
# =================================

compras = (
    df_filtrado["compra_local"]
    .value_counts()
    .reset_index()
)

compras.columns = ["compra_local", "cantidad"]

compras["compra_local"] = compras["compra_local"].map(
    {
        True: "Local",
        False: "Internacional"
    }
)

fig3 = px.pie(
    compras,
    names="compra_local",
    values="cantidad",
    title="Compras locales vs internacionales"
)

st.plotly_chart(fig3, use_container_width=True)

# =================================
# VISUALIZACIÓN 4
# DISTRIBUCIÓN DE IMPORTES
# =================================

fig4 = px.histogram(
    df_filtrado,
    x="amount",
    nbins=30,
    title="Distribución de importes"
)

st.plotly_chart(fig4, use_container_width=True)
