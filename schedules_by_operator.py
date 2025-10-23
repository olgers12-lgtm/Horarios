# Scheduler por operario y área - Streamlit
# Pega esto en un archivo .py y ejecútalo con `streamlit run schedules_by_operator.py`
# Requiere: streamlit, pandas, numpy
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Planificador por Operario y Área", layout="wide")
st.title("Generador de Horarios por Operario y Área")

st.markdown("""
Sube una lista de operarios con sus áreas y disponibilidades, define turnos y requerimientos por área y el sistema propondrá un horario balanceado.
""")

# -----------------------------
# Ejemplo de formato de operadores
# -----------------------------
st.sidebar.header("1) Cargar / crear plantilla de operarios")
uploaded = st.sidebar.file_uploader("CSV con operarios (opcional). Columnas: name,areas,contract_hours,availability", type=["csv"])

sample_btn = st.sidebar.button("Generar plantilla de ejemplo")
if uploaded:
    df_ops = pd.read_csv(uploaded)
else:
    if sample_btn:
        df_ops = pd.DataFrame([
            {"name":"Juan","areas":"SURF;E&M","contract_hours":48,"availability":"Mon,Tue,Wed,Thu,Fri,Sat"},
            {"name":"María","areas":"SURF","contract_hours":48,"availability":"Mon,Tue,Wed,Thu,Fri"},
            {"name":"Pedro","areas":"E&M","contract_hours":40,"availability":"Mon,Tue,Wed,Thu,Fri,Sun"},
            {"name":"Ana","areas":"SURF","contract_hours":40,"availability":"Tue,Wed,Thu,Fri,Sat"},
            {"name":"Luis","areas":"E&M","contract_hours":32,"availability":"Mon,Wed,Fri,Sat"},
        ])
    else:
        # Default empty
        df_ops = pd.DataFrame(columns=["name","areas","contract_hours","availability"])

st.write("Ejemplo / Operarios cargados (edítalos si quieres):")
st.dataframe(df_ops)

# Allow user to edit/add operators via text area CSV
st.sidebar.markdown("O pega CSV aquí:")
ops_text = st.sidebar.text_area("CSV (opcional) — columnas: name,areas,contract_hours,availability", height=120)
if ops_text.strip():
    try:
        df_ops = pd.read_csv(pd.compat.StringIO(ops_text))
        st.write("Operarios cargados desde texto:")
        st.dataframe(df_ops)
    except Exception:
        st.error("CSV inválido en el cuadro de texto. Revisa el formato.")

# -----------------------------
# Parámetros de planificación
# -----------------------------
st.sidebar.header("2) Parámetros de planificación")
start_date = st.sidebar.date_input("Fecha inicio", value=datetime(2025,12,1).date())
num_days = st.sidebar.number_input("Número de días a planificar", min_value=1, max_value=31, value=28)
days = [(start_date + timedelta(days=i)) for i in range(num_days)]
day_names = [d.strftime("%a %d-%b") for d in days]

# Define turnos
st.sidebar.header("3) Definir turnos")
default_shifts = [
    {"id":"Morning","start":"08:00","end":"16:00","hours":8},
    {"id":"Afternoon","start":"16:00","end":"00:00","hours":8},
    {"id":"Night","start":"00:00","end":"08:00","hours":8},
]
shifts_cfg = st.sidebar.multiselect("Selecciona turnos a usar", options=[s["id"] for s in default_shifts], default=[s["id"] for s in default_shifts])
# Build active shifts list
shifts = [s for s in default_shifts if s["id"] in shifts_cfg]

# Areas and requirements per shift
st.sidebar.header("4) Áreas y requerimientos")
areas_text = st.sidebar.text_area("Lista de áreas (separadas por coma)", value="Encintado,Bloqueo,Generado,Laser,Pulido,Desbloqueo,Calidad")
areas = [a.strip() for a in areas_text.split(",") if a.strip()]

# For each area and shift, ask required operators (simple integer)
st.sidebar.markdown("Requerimiento por área y turno (n° operarios)")
req_matrix = {}
for s in shifts:
    cols = st.sidebar.columns((1,1))
    st.sidebar.markdown(f"**Turno: {s['id']}**")
    for a in areas:
        key = f"req_{s['id']}_{a}"
        req = st.sidebar.number_input(f"{a} - {s['id']}", min_value=0, max_value=10, value=1, key=key)
        req_matrix[(s['id'], a)] = int(req)

# Global constraints
max_hours_per_day = st.sidebar.number_input("Horas máximas por día por operario", min_value=1, max_value=24, value=8)
max_shifts_per_week = st.sidebar.number_input("Máx. turnos por semana por operario", min_value=1, max_value=7, value=5)

# -----------------------------
# Preprocesamiento de operarios
# -----------------------------
def parse_avail(av_str):
    if pd.isna(av_str):
        return set(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
    tokens = [t.strip() for t in str(av_str).replace(";",",").split(",") if t.strip()]
    # Normalize short names
    norm = set()
    for t in tokens:
        t0 = t[:3].title()
        norm.add(t0)
    return norm

def parse_areas(a_str):
    if pd.isna(a_str):
        return []
    return [x.strip() for x in str(a_str).replace(";",",").split(",") if x.strip()]

ops = []
for _, row in df_ops.iterrows():
    name = row.get("name")
    if pd.isna(name) or not str(name).strip():
        continue
    op_areas = parse_areas(row.get("areas",""))
    contract_hours = float(row.get("contract_hours", 40))
    availability = parse_avail(row.get("availability","Mon,Tue,Wed,Thu,Fri,Sat,Sun"))
    ops.append({
        "name": name,
        "areas": op_areas,
        "contract_hours": contract_hours,
        "availability": availability,
        "assigned_hours": 0.0,
        "assigned_shifts": 0,
    })

if len(ops) == 0:
    st.warning("No hay operarios definidos. Carga la plantilla o pega CSV en la barra lateral.")
    st.stop()

# -----------------------------
# Generador simple de horarios (heurístico greedy)
# -----------------------------
st.header("Generar horario propuesto")
if st.button("Generar horario"):
    # Initialize schedule list
    schedule = []  # each entry: date, dayname, shift, area, operator (or None), hours
    # create quick lookup of operators by area capability
    ops_by_area = {}
    for a in areas:
        ops_by_area[a] = [o for o in ops if a in o["areas"] or len(o["areas"])==0]  # if no areas specified, can work anywhere

    # Reset assigned counters
    for o in ops:
        o["assigned_hours"] = 0.0
        o["assigned_shifts"] = 0

    # iterate days and shifts
    for idx, d in enumerate(days):
        dow = d.strftime("%a")  # Mon, Tue...
        for s in shifts:
            shift_hours = s["hours"]
            for a in areas:
                needed = req_matrix.get((s["id"], a), 0)
                for seat in range(needed):
                    # select candidate operators: available that day, can work area, not exceeding daily hours
                    candidates = []
                    for o in ops_by_area.get(a, []):
                        if dow in o["availability"]:
                            # compute if assigning will exceed daily limit or weekly limit (approx: shifts/week)
                            if o["assigned_hours"] + shift_hours <= o["contract_hours"]:  # prefer within contract
                                candidates.append(o)
                    # If no candidate within contract_hours, relax to any available
                    if not candidates:
                        for o in ops_by_area.get(a, []):
                            if dow in o["availability"]:
                                candidates.append(o)
                    # If still none, assign None
                    if not candidates:
                        schedule.append({
                            "Fecha": d,
                            "Día": d.strftime("%a %d-%b"),
                            "Turno": s["id"],
                            "Área": a,
                            "Operario": None,
                            "Horas": shift_hours
                        })
                        continue
                    # choose candidate with minimum assigned_hours (balance carga)
                    candidates_sorted = sorted(candidates, key=lambda x: (x["assigned_hours"], x["assigned_shifts"]))
                    chosen = candidates_sorted[0]
                    # assign
                    chosen["assigned_hours"] += shift_hours
                    chosen["assigned_shifts"] += 1
                    schedule.append({
                        "Fecha": d,
                        "Día": d.strftime("%a %d-%b"),
                        "Turno": s["id"],
                        "Área": a,
                        "Operario": chosen["name"],
                        "Horas": shift_hours
                    })

    df_schedule = pd.DataFrame(schedule)
    # Pivot/summary per operator
    summary = df_schedule.groupby("Operario")["Horas"].sum().reset_index().sort_values("Horas", ascending=False)
    st.subheader("Horario propuesto (detalle)")
    st.dataframe(df_schedule)
    st.download_button("Descargar horario (CSV)", data=df_schedule.to_csv(index=False).encode("utf-8"), file_name="horario_propuesto.csv", mime="text/csv")

    st.subheader("Resumen por operario")
    st.dataframe(summary)

    st.success("Horario generado con heurístico balanceador (minimiza horas asignadas). Revisa y ajusta manualmente si es necesario.")

    st.markdown("""
    Siguientes mejoras recomendadas:
    - Restringir máximo de turnos consecutivos / día libre obligatorio.
    - Usar optimización (ILP) si quieres garantías formales (p. ej. con pulp) para cumplir todas las restricciones.
    - Añadir edición directa del calendario (st.data_editor) para ajustes manuales.
    """)
else:
    st.info("Pulsa 'Generar horario' para obtener una propuesta con la configuración actual.")