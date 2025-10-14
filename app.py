import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Test de Wonderlic", page_icon="🧠", layout="centered")

# --- CARGAR PREGUNTAS ---
with open("preguntas_wonderlic.json", "r", encoding="utf-8") as f:
    preguntas = json.load(f)

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
        return pd.read_csv("respuestas.csv", encoding="utf-8-sig")
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
            tiempo_restante = 12 * 60 - tiempo_transcurrido  # 12 minutos

            if tiempo_restante <= 0:
                st.warning("⏰ ¡Tiempo agotado! No puedes seguir respondiendo.")
                st.session_state.en_progreso = False
            else:
                minutos = tiempo_restante // 60
                segundos = tiempo_restante % 60
                st.info(f"Tiempo restante: {minutos:02d}:{segundos:02d}")

                respuestas = st.session_state.respuestas

                # Mostrar las preguntas
                for p in preguntas:
                    respuestas[p["pregunta"]] = st.radio(
                        p["pregunta"],
                        p["opciones"],
                        key=f"preg_{p['id']}",
                        index=None
                    )

                # Botón para finalizar
                if st.button("📤 Enviar respuestas"):
                    correctas = 0
                    for p in preguntas:
                        if respuestas.get(p["pregunta"]) == p["respuesta_correcta"]:
                            correctas += 1

                    puntaje = correctas
                    tiempo_usado = f"{tiempo_transcurrido//60}:{tiempo_transcurrido%60:02d}"

                    # Evaluación de nivel
                    if puntaje >= 40:
                        nivel = "🔥 Rendimiento Alto"
                    elif puntaje >= 25:
                        nivel = "⚖️ Rendimiento Medio"
                    else:
                        nivel = "🧩 Rendimiento Bajo"

                    guardar_respuestas(usuario, respuestas, puntaje, tiempo_usado)

                    st.success(f"✅ Has obtenido **{puntaje}** de **{len(preguntas)}** respuestas correctas.")
                    st.info(f"Tu nivel es: **{nivel}**")
                    st.write(f"⏱️ Tiempo usado: {tiempo_usado} minutos")
                    st.balloons()

                    st.session_state.en_progreso = False

    else:
        st.warning("Por favor, ingrese su nombre de usuario para comenzar.")

# --- TAB 2: RESULTADOS ---
with tab2:
    st.subheader("📊 Resultados generales")
    df = cargar_respuestas()

    if not df.empty:
        st.dataframe(df)
        st.write(f"👥 Total de participantes: {len(df)}")
        st.bar_chart(df["puntaje"])
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Descargar resultados (CSV)", csv, "resultados.csv")
    else:
        st.info("Aún no hay resultados registrados.")

