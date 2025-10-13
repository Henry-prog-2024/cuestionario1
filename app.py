import streamlit as st
import pandas as pd
import json
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
    df.to_csv("respuestas.csv", mode="a", header=not os.path.exists("respuestas.csv"), index=False, encoding="utf-8-sig")

# --- INTERFAZ ---
st.title("🧠 Cuestionario Interactivo")
st.write("Responde las siguientes preguntas y descubre tu resultado al final.")

# --- LOGIN BÁSICO ---
usuario = st.text_input("👤 Ingrese su nombre de usuario")

if usuario:
    st.success(f"Bienvenido, {usuario}")

    # Diccionario para almacenar respuestas
    respuestas = {}

    # --- MOSTRAR PREGUNTAS ---
    for i, p in enumerate(preguntas):
        respuesta = st.radio(p["pregunta"], p["opciones"], key=i)
        respuestas[p["pregunta"]] = respuesta

    # --- BOTÓN PARA ENVIAR ---
    if st.button("📤 Enviar respuestas"):
        # Ejemplo simple: contar cuántos "Sí"
        puntaje = sum([1 for r in respuestas.values() if r == "Sí"])
        resultado = f"Tu resultado es {puntaje} puntos"
        st.success(resultado)

        guardar_respuestas(usuario, respuestas, resultado)
        st.balloons()

        # --- MOSTRAR RESULTADO ---
        st.markdown(f"### 🏁 {resultado}")

        # Mostrar todas las respuestas del usuario
        st.dataframe(pd.DataFrame([respuestas]))

else:
    st.warning("Por favor, ingrese su nombre de usuario para comenzar.")
