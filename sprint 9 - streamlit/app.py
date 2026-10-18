import pandas as pd
import streamlit as st

df_full = pd.read_csv("df_full.csv")

st.title("Dashboard Comercial")

pais = st.sidebar.selectbox(
    "País usuario",
    sorted(df_full["country_user"].unique())
)

st.write(f"País seleccionado: {pais}")

df_filtrado = df_full[
    df_full["country_user"] == pais
]

st.write(df_filtrado.head())