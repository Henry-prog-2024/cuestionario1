import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Test de Wonderlic", page_icon="🧠", layout="centered")

# --- CARGAR PREGUNTAS ---
try:
    with open("preguntas_wonderlic.json", "r", encoding="utf-8") as f:
        preguntas = json.load(f)
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'preguntas_wonderlic.json'. "
             "Asegúrate de colocarlo en la misma carpeta que este archivo app.py.")
    st.stop()

# --- FUNCIONES AUXILIARES ---
def guardar_respuestas(usuario, respuestas, puntaje, tiempo_usado):
    """Guarda las respuestas en un archivo CSV"""
    df = pd.DataFrame([{
        "usuario": usuario,
        "fecha": datetime.now().strftime("%Y
