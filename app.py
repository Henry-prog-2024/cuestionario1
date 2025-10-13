import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Cuestionario Interactivo", page_icon="🧠", layout="centered")

# --- CARGAR PREGUNTAS ---
with open("preguntas.json", "r", encoding="utf-8") as f:
    preguntas = json.load(f)

# --- FUNCIÓN PARA GUARDAR RESPUESTAS ---
def guardar_respuestas(usuario, respuestas, resultado):
    df = pd.DataFrame([{
        "usuario": usuario,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **respuestas,
        "resultado": resultado
    }])
    archivo = "respuestas.csv"
    df.to_csv(archivo, mode="a", header=not os.path.exists(archivo), index=False, encoding="utf-8-sig")

# --- FUNCIÓN PARA LEER RESPUESTAS ---
def cargar_respuestas():
    if os.path.exists("respuestas.csv"):
        return pd.read_csv("respuestas.csv", encoding="utf-8-sig")
    else:
        return pd.DataFrame()

# --- INTERFAZ PRINCIPAL ---
st.title("🧠 Cuestionario Interactivo")

# Crear pestañas
tab1, tab2 = st.tabs(["📋 Cuestionario", "📊 Resultados"])

# --- TAB 1: CUESTIONARIO ---
with tab1:
    st.subheader("Responde las siguientes preguntas:")

    usuario = st.text_input("👤 Ingrese su nombre de usuario")

    if usuario:
        st.success(f"Bienvenido, {usuario}")

        respuestas = {}
        for i, p in enumerate(preguntas):
            respuesta = st.radio(p["pregunta"], p["opciones"], key=f"q{i}")
            respuestas[p["pregunta"]] = respuesta

        if st.button("📤 Enviar respuestas"):
            # Ejemplo simple de cálculo de resultado
            puntaje = sum([1 for r in respuestas.values() if r == "Sí"])
            resultado = f"Tu resultado es {puntaje} puntos"
            st.success(resultado)
            guardar_respuestas(usuario, respuestas, resultado)
            st.balloons()
            st.markdown(f"### 🏁 {resultado}")
    else:
        st.warning("Por favor, ingrese su nombre de usuario para comenzar.")

# --- TAB 2: RESULTADOS ---
with tab2:
    st.subheader("📊 Resultados de todos los participantes")
    df = cargar_respuestas()

    if not df.empty:
        st.dataframe(df)

        # Mostrar estadísticas simples
        st.markdown("### 📈 Estadísticas generales")
        st.write(f"Total de participantes: **{len(df)}**")

        # Gráfico de resultados
        conteo = df["resultado"].value_counts()
        st.bar_chart(conteo)

        # Opción de descarga
        csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇️ Descargar resultados (CSV)", data=csv, file_name="respuestas.csv", mime="text/csv")
    else:
        st.info("Aún no hay respuestas registradas.")
