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
            df = pd.read_csv("respuestas.csv", encoding="utf-8-sig")
            st.write("📂 Archivo cargado correctamente. Filas:", len(df))
            st.write(df.head())
            return df
        except Exception as e:
            st.error(f"❌ Error al leer 'respuestas.csv': {e}")
            return pd.DataFrame()
    else:
        st.warning("⚠️ No se encontró el archivo 'respuestas.csv'.")
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
            tiempo_restante = 1 * 60 - tiempo_transcurrido  # 12 minutos

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

                # Botón para finalizar
                if st.button("📤 Enviar respuestas"):
                    correctas = 0
                    for p in preguntas:
                        if respuestas_usuario.get(p["pregunta"]) == p["respuesta_correcta"]:
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

                    # Guardar todo
                    guardar_respuestas(usuario, respuestas_usuario, puntaje, tiempo_usado, nivel)

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
        # Mostrar resumen
        columnas_principales = [col for col in ["usuario", "fecha", "puntaje", "nivel", "tiempo_usado"] if col in df.columns]
        st.dataframe(df[columnas_principales])
        st.write(f"👥 Total de participantes: {len(df)}")

        # Mostrar gráfico si hay puntajes
        if "puntaje" in df.columns:
            st.bar_chart(df["puntaje"])
        else:
            st.info("📊 Aún no hay datos de puntaje para graficar.")

        # Botón de descarga completa
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Descargar respuestas completas (CSV)", csv, "respuestas_completas.csv")
    else:
        st.info("Aún no hay resultados registrados.")
