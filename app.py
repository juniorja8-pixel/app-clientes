import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Registro de Clientes", page_icon="📋", layout="centered")

# --- CONEXIÓN A TU BASE DE DATOS ---
SUPABASE_URL = "https://hpuqwgouerayjuidagtr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhwdXF3Z291ZXJheWp1aWRhZ3RyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTUyODM2ODEsImV4cCI6MjExMDg1OTY4MX0.nJqoww3h8rkiux4DdMsMxwJlRQjXIOkKH84vK9AnrqI"

HEADERS = {
    "apikey": SUPABASE_KEY.strip(),
    "Authorization": f"Bearer {SUPABASE_KEY.strip()}",
    "Content-Type": "application/json"
}

st.title("📋 Registro de Clientes")

tab_nuevo, tab_lista = st.tabs(["➕ Nuevo Cliente", "📂 Ver Lista"])

# --- PESTAÑA 1: GUARDAR CLIENTE ---
with tab_nuevo:
    with st.form("form_cliente", clear_on_submit=True):
        nombre = st.text_input("Nombre completo *")
        telefono = st.text_input("Teléfono / WhatsApp *", placeholder="Ej. 0991234567")
        correo = st.text_input("Correo electrónico")
        servicio = st.selectbox("Servicio", ["Consulta", "Cotización", "Venta", "Soporte", "Otro"])
        notas = st.text_area("Notas adicionales", height=80)
        
        if st.form_submit_button("Guardar Cliente", use_container_width=True):
            if nombre.strip() and telefono.strip():
                datos = {
                    "nombre": nombre.strip(),
                    "telefono": telefono.strip(),
                    "correo": correo.strip(),
                    "servicio": servicio,
                    "notas": notas.strip()
                }
                res = requests.post(f"{SUPABASE_URL}/rest/v1/clientes", json=datos, headers=HEADERS)
                if res.status_code in (200, 201):
                    st.success(f"✅ ¡Cliente '{nombre}' guardado!")
                else:
                    st.error(f"Error al guardar ({res.status_code}): {res.text}")
            else:
                st.error("⚠️ Nombre y teléfono son obligatorios.")

# --- PESTAÑA 2: VER LISTA ---
with tab_lista:
    if st.button("🔄 Actualizar"):
        st.rerun()

    res = requests.get(f"{SUPABASE_URL}/rest/v1/clientes?select=nombre,telefono,correo,servicio,notas&order=id.desc", headers=HEADERS)
    
    if res.status_code == 200:
        df = pd.DataFrame(res.json())

        if df.empty:
            st.info("Aún no hay clientes registrados.")
        else:
            buscar = st.text_input("🔍 Buscar por nombre o teléfono:")
            if buscar:
                df = df[
                    df["nombre"].astype(str).str.contains(buscar, case=False, na=False) |
                    df["telefono"].astype(str).str.contains(buscar, case=False, na=False)
                ]

            st.write(f"**Total:** {len(df)} clientes")
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 Descargar en Excel (CSV)", data=csv, file_name="clientes.csv", mime="text/csv", use_container_width=True)
    else:
        st.error(f"Error de conexión ({res.status_code}): {res.text}")
