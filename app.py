import streamlit as st
import pandas as pd
import json
import os
import time
import tempfile
import csv
from datetime import datetime
import io

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Test de Wonderlic", page_icon="🧠", layout="centered")

# --- CARGAR PREGUNTAS ---
try:
    with open("preguntas_wonderlic.json", "r", encoding="utf-8") as f:
        preguntas = json.load(f)
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'preguntas_wonderlic.json'.")
    st.stop()

# --- FUNCIONES AUXILIARES ---
def guardar_respuestas(usuario, respuestas_usuario, puntaje, tiempo_usado, nivel):
    """Guarda respuestas completas en carpeta temporal (compatible con Streamlit Cloud)"""
    data = {
        "usuario": usuario,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "puntaje": puntaje,
        "tiempo_usado": tiempo_usado,
        "nivel": nivel
    }
    for p in preguntas:
        pregunta_texto = p["pregunta"]
        data[f"{p['id']}_pregunta"] = pregunta_texto
        data[f"{p['id']}_respuesta_usuario"] = respuestas_usuario.get(pregunta_texto, "")
        data[f"{p['id']}_respuesta_correcta"] = p["respuesta_correcta"]

    df = pd.DataFrame([data])
    archivo = os.path.join(tempfile.gettempdir(), "respuestas.csv")

    df.to_csv(
        archivo,
        mode="a",
        header=not os.path.exists(archivo),
        index=False,
        encoding="utf-8-sig",
        quoting=csv.QUOTE_ALL
    )
    st.session_state["archivo_guardado"] = archivo


def cargar_respuestas():
    """Lee las respuestas almacenadas desde carpeta temporal"""
    archivo = st.session_state.get("archivo_guardado", os.path.join(tempfile.gettempdir(), "respuestas.csv"))
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8-sig") as f:
                contenido = f.read()
            df = pd.read_csv(io.StringIO(contenido), sep=",", quotechar='"', on_bad_lines="skip")
            return df
        except Exception:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

# --- INTERFAZ ---
st.title("🧠 Test de Wonderlic Online")
st.write("Tendrás **12 minutos** para responder todas las preguntas. ¡Buena suerte!")

tab1, tab2 = st.tabs(["📋 Cuestionario", "📊 Resultados"])

# --- TAB 1: CUESTIONARIO ---
with tab1:
    usuario = st.text_input("👤 Ingrese su nombre de usuario")

    if usuario:
        if "inicio" not in st.session_state:
            if st.button("🕐 Iniciar Test"):
                st.session_state.inicio = time.time()
                st.session_state.en_progreso = True
                st.session_state.respuestas = {}
                st.session_state.pregunta_actual = 0

        # Mostrar solo una pregunta a la vez
        if st.session_state.get("en_progreso", False):
            tiempo_transcurrido = int(time.time() - st.session_state.inicio)
            duracion_total = 12 * 60
            tiempo_restante = duracion_total - tiempo_transcurrido

            if tiempo_restante <= 0:
                st.warning("⏰ ¡Tiempo agotado! Tus respuestas se guardarán automáticamente.")
                st.session_state.en_progreso = False
            else:
                minutos = tiempo_restante // 60
                segundos = tiempo_restante % 60
                progreso = (st.session_state.pregunta_actual + 1) / len(preguntas)
                st.progress(progreso)
                st.info(f"⏱️ Tiempo restante: {minutos:02d}:{segundos:02d}")

                i = st.session_state.pregunta_actual
                p = preguntas[i]

                st.markdown(f"### Pregunta {i+1}/{len(preguntas)}")
                st.markdown(f"**{p['pregunta']}**")

                respuesta = st.radio("Selecciona una opción:", p["opciones"], key=f"resp_{i}", index=None)

                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if i > 0 and st.button("⬅️ Anterior"):
                        st.session_state.pregunta_actual -= 1
                with col2:
                    st.empty()
                with col3:
                    if i < len(preguntas) - 1 and st.button("Siguiente ➡️"):
                        if respuesta:
                            st.session_state.respuestas[p["pregunta"]] = respuesta
                            st.session_state.pregunta_actual += 1
                    elif i == len(preguntas) - 1 and st.button("📤 Enviar"):
                        st.session_state.respuestas[p["pregunta"]] = respuesta
                        correctas = sum(
                            1 for p in preguntas
                            if st.session_state.respuestas.get(p["pregunta"]) == p["respuesta_correcta"]
                        )
                        puntaje = correctas
                        tiempo_usado = f"{tiempo_transcurrido//60}:{tiempo_transcurrido%60:02d}"
                        if puntaje >= 40:
                            nivel = "🔥 Rendimiento Alto"
                        elif puntaje >= 25:
                            nivel = "⚖️ Rendimiento Medio"
                        else:
                            nivel = "🧩 Rendimiento Bajo"
                        guardar_respuestas(usuario, st.session_state.respuestas, puntaje, tiempo_usado, nivel)
                        st.success(f"✅ Test completado. Puntaje: {puntaje}/{len(preguntas)}")
                        st.balloons()
                        st.session_state.en_progreso = False
    else:
        st.warning("Por favor, ingrese su nombre de usuario para comenzar.")

# --- TAB 2: RESULTADOS ---
with tab2:
    st.subheader("📊 Resultados generales")
    df = cargar_respuestas()
    if not df.empty:
        st.success(f"📂 Resultados cargados ({len(df)} registros).")
        columnas_principales = [c for c in ["usuario", "fecha", "puntaje", "nivel", "tiempo_usado"] if c in df.columns]
        st.dataframe(df[columnas_principales])

        archivo_temp = st.session_state.get("archivo_guardado", None)
        if archivo_temp and os.path.exists(archivo_temp):
            with open(archivo_temp, "rb") as f:
                st.download_button("⬇️ Descargar respuestas (CSV)", f, "respuestas.csv")

        if "puntaje" in df.columns:
            st.bar_chart(df["puntaje"])
    else:
        st.info("Aún no hay resultados registrados.")
