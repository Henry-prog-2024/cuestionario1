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
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "puntaje": puntaje,
        "tiempo_usado": tiempo_usado,
        **respuestas
    }])
    archivo = "respuestas.csv"
    df.to_csv(archivo, mode="a", header=not os.path.exists(archivo),
              index=False, encoding="utf-8-sig")

def cargar_respuestas():
    """Lee las respuestas almacenadas"""
    if os.path.exists("respuestas.csv"):
        try:
            return
