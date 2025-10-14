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
def guardar_respuestas(usuario, respuestas_usuario, puntaje, tiempo_usado, nivel):
    """Guarda respuestas completas (usuario, resultados y selección por pregunta)"""
    data = {
        "usuario": usuario,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "puntaje": puntaje,
        "tiempo_usado": tiempo_usado,
        "nivel": nivel
    }

    # Añadir cada pregunta, respuesta del usuario y correcta
    for p in preguntas:
        pregunta_texto = p["pregunta"]
        data[f"{p['id']}_pregunta"] = pregunta_texto
        data[f"{p['id']}_respuesta_usuario"] = respuestas_usuario.get(pregunta_texto, "")
        data[f"{p['id']}_respuesta_correcta"] = p["respuesta_correcta"]

    df = pd.DataFrame([data])
    archivo = os.path.join(os.getcwd(), "respuestas.csv")

    try:
        df.to_csv(
            archivo,
            mode="a",
            header=not os.path.exists(archivo),
            index=False,
            encoding="utf-8-sig"
        )
        st.success("✅ Respuestas y resultados guardados correctamente.")
    except Exception as e:
        st.error(f"❌ Error al guardar respuestas: {e}")

def cargar_respuestas():
    """Lee las respuestas almacenadas"""
    if os.path.exists("respuestas.csv"):
        try:
            return pd.read_csv("respuestas.csv", encoding="utf-8-sig")
        except Exception:
            st.warning("⚠️ No se pudo leer correctamente 'respuestas.csv'. Se omitirá su carga.")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

# --- INTERFAZ PRINCIPAL ---
st.title("🧠 Test de Wonderlic Online")
st.write("Tendrás **12 minutos** para responder tantas preguntas como puedas. ¡Buena suerte!")

tab1, tab2 = st.tabs(["📋 Cuestionario", "📊 Resultados"])

# --- TAB 1: CUESTIONARIO ---
with tab1:
    usuario = st.text_input("👤 Ingrese su nombre de usuario")

    if usuario:
        st.success(f"Bienvenido, {usuario}. Presiona el botón para comenzar el test.")

        if "inicio" not in st.session_state:
            if st.button("🕐 Iniciar Test"):
                st.session_state.inicio = time.time()
                st.session_state.en_progreso = True
                st.session_state.respuestas = {}

        # Mostrar tiempo restante si el test está en progreso
        if st.session_state.get("en_progreso", False):
            tiempo_transcurrido = int(time.time() - st.session_state.inicio)
            tiempo_restante = 2 * 60 - tiempo_transcurrido  # 12 minutos

            if tiempo_restante <= 0:
                st.warning("⏰ ¡Tiempo agotado! No puedes seguir respondiendo.")
                st.session_state.en_progreso = False
            else:
                minutos = tiempo_restante // 60
                segundos = tiempo_restante % 60
                st.info(f"⏱️ Tiempo restante: {minutos:02d}:{segundos:02d}")

                respuestas_usuario = st.session_state.respuestas

                # Mostrar las preguntas
                for p in preguntas:
                    respuestas_usuario[p["pregunta"]] = st.radio(
                        p["pregunta"],
                        p["opciones"],
                        key=f"preg_{p['id']}",
                        index=None
                    )

                #

