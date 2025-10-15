import streamlit as st
import pandas as pd
import json
import os
import time
import tempfile
from datetime import datetime
import io
import csv

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
    """Guarda respuestas completas en carpeta temporal (compatible con Streamlit Cloud)"""
    data = {
        "usuario": usuario,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "puntaje": puntaje,
        "tiempo_usado": tiempo_usado,
        "nivel": nivel
    }

    # Agregar cada pregunta y sus respuestas
    for p in preguntas:
        pregunta_texto = p["pregunta"]
        data[f"{p['id']}_pregunta"] = pregunta_texto
        data[f"{p['id']}_respuesta_usuario"] = respuestas_usuario.get(pregunta_texto, "")
        data[f"{p['id']}_respuesta_correcta"] = p["respuesta_correcta"]

    df = pd.DataFrame([data])

    # 📂 Guardar en carpeta temporal (permite escritura en Streamlit Cloud)
    archivo = os.path.join(tempfile.gettempdir(), "respuestas.csv")

    df.to_csv(
        archivo,
        mode="a",
        header=not os.path.exists(archivo),
        index=False,
        encoding="utf-8-sig",
        quoting=csv.QUOTE_ALL
    )

    st.success("✅ Respuestas y resultados guardados correctamente.")
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
        except Exception as e:
            st.error(f"❌ Error al leer 'respuestas.csv': {e}")
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
    duracion_total = 12 * 60  # ⏱️ 12 minutos en segundos
    tiempo_restante = duracion_total - tiempo_transcurrido

    # --- AUTO-GUARDADO CUANDO EL TIEMPO SE ACABA ---
    if tiempo_restante <= 0:
        st.warning("⏰ ¡Tiempo agotado! Tus respuestas se guardarán automáticamente.")
        st.session_state.en_progreso = False

        respuestas_usuario = st.session_state.respuestas
        correctas = 0
        for p in preguntas:
            if respuestas_usuario.get(p["pregunta"]) == p["respuesta_correcta"]:
                correctas += 1

        puntaje = correctas
        tiempo_usado = "12:00"
        if puntaje >= 40:
            nivel = "🔥 Rendimiento Alto"
        elif puntaje >= 25:
            nivel = "⚖️ Rendimiento Medio"
        else:
            nivel = "🧩 Rendimiento Bajo"

        guardar_respuestas(usuario, respuestas_usuario, puntaje, tiempo_usado, nivel)
        st.success(f"✅ Test guardado automáticamente. Puntaje: {puntaje} de {len(preguntas)}")
        st.balloons()

    else:
        minutos = tiempo_restante // 60
        segundos = tiempo_restante % 60
        progreso = tiempo_restante / duracion_total

        # ⏳ Barra de progreso visual
        st.info(f"⏱️ Tiempo restante: {minutos:02d}:{segundos:02d}")
        st.progress(progreso)

        respuestas_usuario = st.session_state.respuestas

        # Mostrar las preguntas
        for p in preguntas:
            respuestas_usuario[p["pregunta"]] = st.radio(
                p["pregunta"],
                p["opciones"],
                key=f"preg_{p['id']}",
                index=None
            )

        # Botón manual para enviar
        if st.button("📤 Enviar respuestas"):
            correctas = 0
            for p in preguntas:
                if respuestas_usuario.get(p["pregunta"]) == p["respuesta_correcta"]:
                    correctas += 1

            puntaje = correctas
            tiempo_usado = f"{tiempo_transcurrido//60}:{tiempo_transcurrido%60:02d}"
            if puntaje >= 40:
                nivel = "🔥 Rendimiento Alto"
            elif puntaje >= 25:
                nivel = "⚖️ Rendimiento Medio"
            else:
                nivel = "🧩 Rendimiento Bajo"

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
        st.success(f"📂 Archivo cargado correctamente ({len(df)} registros).")

        columnas_principales = [c for c in ["usuario", "fecha", "puntaje", "nivel", "tiempo_usado"] if c in df.columns]
        st.write("### 🧾 Resumen general de participantes")
        st.dataframe(df[columnas_principales])

        usuarios = df["usuario"].unique().tolist() if "usuario" in df.columns else []
        if usuarios:
            seleccionado = st.selectbox("👤 Ver respuestas de:", usuarios)
            df_user = df[df["usuario"] == seleccionado]

            if not df_user.empty:
                st.write(f"### 📋 Respuestas de {seleccionado}")
                ultima = df_user.iloc[-1]
                if "puntaje" in df.columns:
                    st.write(f"**Puntaje:** {ultima.get('puntaje', 'N/A')} / {len(preguntas)}")
                if "nivel" in df.columns:
                    st.write(f"**Nivel:** {ultima.get('nivel', 'N/A')}")
                if "tiempo_usado" in df.columns:
                    st.write(f"**Tiempo usado:** {ultima.get('tiempo_usado', 'N/A')}")

                respuestas_tabla = []
                for p in preguntas:
                    pid = p["id"]
                    r_usuario = ultima.get(f"{pid}_respuesta_usuario", "")
                    r_correcta = ultima.get(f"{pid}_respuesta_correcta", "")
                    correcto = "✅" if r_usuario == r_correcta else "❌"
                    respuestas_tabla.append({
                        "N°": pid,
                        "Pregunta": p["pregunta"],
                        "Tu respuesta": r_usuario,
                        "Respuesta correcta": r_correcta,
                        "Resultado": correcto
                    })

                st.write("### 📘 Detalle de respuestas")
                st.dataframe(pd.DataFrame(respuestas_tabla))
        else:
            st.info("No hay usuarios registrados aún.")

        # Botón de descarga
        archivo_temp = st.session_state.get("archivo_guardado", None)
        if archivo_temp and os.path.exists(archivo_temp):
            with open(archivo_temp, "rb") as f:
                st.download_button("⬇️ Descargar respuestas (CSV)", f, "respuestas.csv")

        # Gráfico de puntajes
        if "puntaje" in df.columns:
            st.write("### 📈 Distribución de puntajes")
            st.bar_chart(df["puntaje"])
    else:
        st.info("Aún no hay resultados registrados.")