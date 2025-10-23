# Debug wrapper para Streamlit — muestra errores/estado del entorno cuando la app queda en blanco.
# Coloca este archivo en el mismo directorio que tu schedules_by_operator.py y ejecuta:
# streamlit run schedules_debug_wrapper.py
import streamlit as st
import sys, os, traceback, importlib.util, importlib.machinery

st.set_page_config(page_title="DEBUG: wrapper schedules_by_operator", layout="wide")
st.title("DEBUG: wrapper — Mostrar errores y estado del entorno")

st.markdown("Esta página captura errores al importar/ejecutar tu app principal (schedules_by_operator.py) y muestra información útil para depuración.")

# 1) Mostrar info básica de entorno
st.subheader("Info del entorno")
st.write("Python:", sys.version.replace("\n", " "))
st.write("Working dir:", os.getcwd())
st.write("Archivo app esperado:", os.path.join(os.getcwd(), "schedules_by_operator.py"))
st.write("Streamlit argv:", sys.argv)

# 2) Chequeo rápido de paquetes relevantes
st.subheader("Disponibilidad de paquetes clave")
import importlib.util
packages = ["streamlit","pandas","numpy","plotly","matplotlib","xlsxwriter","openpyxl"]
pkg_status = {}
for p in packages:
    spec = importlib.util.find_spec(p)
    pkg_status[p] = "INSTALLED" if spec is not None else "missing"
st.table(pd.DataFrame(list(pkg_status.items()), columns=["package","status"]))

# 3) Intentar importar (ejecutar) tu app principal de forma segura
st.subheader("Intentando importar y ejecutar schedules_by_operator.py")
app_path = os.path.join(os.getcwd(), "schedules_by_operator.py")
if not os.path.exists(app_path):
    st.error(f"No se encontró schedules_by_operator.py en: {app_path}")
    st.stop()

try:
    # Import module from file path without caching previous imports
    spec = importlib.util.spec_from_file_location("schedules_by_operator_for_debug", app_path)
    module = importlib.util.module_from_spec(spec)
    # Ejecutar el módulo (esto ejecutará top-level code de tu app)
    loader = spec.loader
    assert loader is not None
    loader.exec_module(module)
    st.success("La importación/ejecución de schedules_by_operator.py finalizó sin lanzar excepciones visibles.")
    st.info("Si la pantalla principal sigue en blanco en tu app original, revisa la forma en que Streamlit muestra tu UI (posibles condiciones de flujo que no renderizan nada).")
except Exception as e:
    st.error("Se ha producido una excepción al importar/ejecutar schedules_by_operator.py")
    st.exception(e)
    # Mostrar traceback completo en texto
    tb = traceback.format_exc()
    st.text_area("Traceback completo", tb, height=400)

    # Extra: mostrar contenido de las primeras 120 líneas del archivo para revisión rápida
    try:
        with open(app_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        preview = "".join(lines[:120])
        st.subheader("Preview (primeras 120 líneas) de schedules_by_operator.py")
        st.code(preview, language="python")
    except Exception as ex2:
        st.write("No se pudo leer el archivo para mostrar preview:", ex2)

st.markdown("---")
st.info("Después de lanzar este wrapper, copia aquí el traceback que aparece (si lo hubiera). Yo lo reviso y te doy la solución exacta (parche o cambio de código).")
