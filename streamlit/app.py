import streamlit as st
import plotly.express as px

st.title("Prueba Plotly")

fig = px.bar(
    x=["A", "B", "C"],
    y=[10, 20, 30]
)

st.plotly_chart(fig)
