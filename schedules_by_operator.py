# Scheduler por operario y área - Incluye lista de operarios proporcionada
# Ejecutar: streamlit run schedules_by_operator_with_staff.py
# Requisitos: streamlit, pandas, numpy
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Planificador por Operario y Área (Con plantilla)", layout="wide")
st.title("Generador de Horarios por Operario y Área — Plantilla cargada")

st.markdown("""
Se ha cargado la lista de operarios que proporcionaste. Puedes:
- Revisar/editar la plantilla.
- Ajustar turnos y requerimientos por área.
- Generar un horario propuesto que respeta reglas (06:00–06:00, turnos definidos, max 6 días consecutivos).
""")

# -----------------------------
# Plantilla de operarios (lista que enviaste)
# -----------------------------
st.sidebar.header("Operarios: plantilla precargada (editar/descargar)")
ops_data = [
    {"name":"MORAGA MORENO ANA ISABEL", "areas":"ANTI-REFLEJO"},
    {"name":"CUBILLO GUTIERREZ JINNETTE LUCIA", "areas":"BISEL Y MONTAJE"},
    {"name":"VILLAFUERTE OBANDO AURELIA", "areas":"BISEL Y MONTAJE"},
    {"name":"OSORIO CONTRERAS MIREYA", "areas":"CONTROL DE CALIDAD"},
    {"name":"CISNEROS CALVO KAROL VANESSA", "areas":"BISEL Y MONTAJE"},
    {"name":"GUERRERO ARTAVIA ANA LORENA", "areas":"BISEL Y MONTAJE"},
    {"name":"QUESADA JIMENEZ RONALD", "areas":"CAPA DURA"},
    {"name":"TENORIO LANZA MARIBELL", "areas":"BISEL Y MONTAJE"},
    {"name":"GUEVARA MENDEZ ROSIBEL", "areas":"COLORACION"},
    {"name":"CHANTO BARAHONA KATHERINE", "areas":"CONTROL DE CALIDAD"},
    {"name":"HERNANDEZ GONZALEZ JEANNETTE", "areas":"TALLA DIGITAL"},
    {"name":"RETANA MORA KATTIA VANESSA", "areas":"BISEL Y MONTAJE"},
    {"name":"FERNANDEZ MORA EMILETH", "areas":"BISEL Y MONTAJE"},
    {"name":"CHACON CHAVERRI YOSELYN", "areas":"CONTROL DE CALIDAD"},
    {"name":"SOLANO SANCHEZ JAIRO", "areas":"BISEL Y MONTAJE"},
    {"name":"CACERES MONTIEL EDWIN LEONARDO", "areas":"BISEL Y MONTAJE"},
    {"name":"MENA MENA HENRY", "areas":"CAPA DURA"},
    {"name":"CHAVES RAMIREZ CARLOS MANUEL", "areas":"CAPA DURA"},
    {"name":"JIMENEZ GONZALEZ DAYANA FRANCELA", "areas":"BISEL Y MONTAJE"},
    {"name":"GUILLEN VEGA KATTIA MARIA", "areas":"ANTI-REFLEJO"},
    {"name":"GOMEZ RODRIGUEZ YITZA VIVIANA", "areas":"ANTI-REFLEJO"},
    {"name":"FONSECA MORA VERONICA", "areas":"TALLA DIGITAL"},
    {"name":"ARAYA LOPEZ DILAN", "areas":"TALLA DIGITAL"},
    {"name":"FLORES MEJIA MARISOL", "areas":"CONTROL DE CALIDAD"},
    {"name":"MEGRET ELEJALDE ODALYS", "areas":"TALLA DIGITAL"},
    {"name":"GUZMAN QUESADA CECILIA", "areas":"CONTROL DE CALIDAD"},
    {"name":"ZUÑIGA GARCIA JAHAIRA VANESSA", "areas":"CONTROL DE CALIDAD"},
    {"name":"PEREIRA RIVERA JUAN DIEGO", "areas":"CONTROL DE CALIDAD"},
    {"name":"GARITA MIRANDA KAROLAYN PAOLA", "areas":"ANTI-REFLEJO"},
    {"name":"CHAVES ARAYA RACHELL FRANCINY", "areas":"BISEL Y MONTAJE"},
    {"name":"SANCHEZ MASIS FABIOLA MARIA", "areas":"ANTI-REFLEJO"},
    {"name":"NAVAS CHAVES KATTIA SIRLEY", "areas":"ANTI-REFLEJO"},
    {"name":"CHAVARRIA ARRIETA ASHLY ANDREA", "areas":"CONTROL DE CALIDAD"},
    {"name":"ROMERO CHACON HILDA VERANIA", "areas":"BISEL Y MONTAJE"},
    {"name":"SIRIAS ARAGON ADRIANA LUCIA", "areas":"TALLA DIGITAL"},
    {"name":"SANABRIA AGUILAR SHARON ROXANA", "areas":"TALLA DIGITAL"},
    {"name":"CALDERON DIAZ CARLOS DAVID", "areas":"ANTI-REFLEJO"},
    {"name":"ICABALCETA AGUILAR DYLAN ALI", "areas":"CAPA DURA"},
    {"name":"PAVON RUIZ SINDY PAOLA", "areas":"BISEL Y MONTAJE"},
    {"name":"CORRALES GARCIA ALLAN STEVE", "areas":"TALLA DIGITAL"},
    {"name":"MORA MORA TAYLOR ENRIQUE", "areas":"TALLA DIGITAL"},
    {"name":"BEJARANO BENAVIDES YURIDIA YOLETTE", "areas":"CAPA DURA"},
    {"name":"MORALES SANCHEZ JOSEPH OLDEMAR", "areas":"BISEL Y MONTAJE"},
    {"name":"MORALES VINDAS JOSHUA ANDREY", "areas":"BISEL Y MONTAJE"},
    {"name":"MENDEZ HERRERA BRANDON JOSUE", "areas":"BISEL Y MONTAJE"},
    {"name":"LEITON CHAVES GABRIEL", "areas":"BISEL Y MONTAJE"},
    {"name":"MENDOZA MONTERO JOSE NARCISO", "areas":"BISEL Y MONTAJE"},
    {"name":"MARIN SALAZAR FANNY GISELLE", "areas":"TALLA DIGITAL"},
    {"name":"HIDALGO NAJERA JAICK MATTHEW", "areas":"BISEL Y MONTAJE"},
    {"name":"RIOS GONZALEZ JOHEL", "areas":"BISEL Y MONTAJE"},
    {"name":"DELGADO AMADOR GEMA DE LOS ANGELES", "areas":"TALLA DIGITAL"},
    {"name":"MURCIA FAJARDO RANDALL", "areas":"BODEGA"},
    {"name":"MONGE GUTIERREZ MARVIN ANTONIO", "areas":"BODEGA"},
    {"name":"BONILLA VALVERDE GLADYS", "areas":"BODEGA"},
    {"name":"CHAVERRI SOLIS WILLIAM ARMANDO", "areas":"BODEGA"},
    {"name":"QUIROS ARAYA JOSEPH ANDRES", "areas":"BODEGA"},
    {"name":"GARCIA LOPEZ WENDY TATIANA", "areas":"BODEGA"},
    {"name":"SARAVIA GAMBOA HILARY NICOLE", "areas":"BODEGA"},
]

# Create default DataFrame and let user edit or upload their own
df_ops_default = pd.DataFrame(ops_data)
# Add default contract_hours and availability (Mon-Sat by default; users who work Sunday can be edited)
df_ops_default["contract_hours"] = 48
df_ops_default["availability"] = "Mon,Tue,Wed,Thu,Fri,Sat"  # default day off = Sunday

st.sidebar.markdown("Si quieres reemplazar la plantilla, sube un CSV con columnas: name,areas,contract_hours,availability")
uploaded = st.sidebar.file_uploader("CSV (opcional) para reemplazar plantilla", type=["csv"])
if uploaded:
    try:
        df_ops = pd.read_csv(uploaded)
        st.success("Plantilla cargada desde CSV")
    except Exception as e:
        st.error("Error leyendo CSV: " + str(e))
        df_ops = df_ops_default.copy()
else:
    # show editable table in main page so user can tweak if needed
    st.subheader("Plantilla de operarios (puedes editar en la tabla abajo)")
    df_ops = st.data_editor(df_ops_default, num_rows="dynamic")

# -----------------------------
# Parámetros de planificación (sidebar)
# -----------------------------
st.sidebar.header("Parámetros de planificación")
start_date = st.sidebar.date_input("Fecha inicio", value=datetime(2025,12,1).date())
num_days = st.sidebar.number_input("Número de días a planificar", min_value=1, max_value=31, value=28)
days = [(start_date + timedelta(days=i)) for i in range(num_days)]

# Turnos por defecto y reglas 06:00–06:00
default_shifts = [
    {"id":"06-14", "start":6, "end":14},
    {"id":"07-15", "start":7, "end":15},
    {"id":"08-16", "start":8, "end":16},
    {"id":"09-17", "start":9, "end":17},
    {"id":"14-21", "start":14, "end":21},  # intermedio 7h
    {"id":"18-00", "start":18, "end":0},   # nocturno 6h
    {"id":"21-06", "start":21, "end":6},   # nocturno largo 9h (cruza medianoche)
]
shift_ids = [s["id"] for s in default_shifts]
selected_shift_ids = st.sidebar.multiselect("Selecciona turnos a usar", options=shift_ids, default=shift_ids)
shifts = []
for s in default_shifts:
    if s["id"] in selected_shift_ids:
        hours = (s["end'] - s['start']) % 24 if False else None  # placeholder handled below
        start = s["start"]
        end = s["end"]
        hours = (end - start) % 24
        if hours == 0:
            hours = 24
        shifts.append({"id": s["id"], "start": start, "end": end, "hours": hours})

# Areas derived from plantilla + allow adding
st.sidebar.header("Áreas (extra si necesitas)")
# build unique area list from df_ops
unique_areas = sorted(set(df_ops["areas"].fillna("").unique()))
areas_text = st.sidebar.text_area("Lista de áreas (separadas por coma)", value=",".join(unique_areas))
areas = [a.strip() for a in areas_text.split(",") if a.strip()]

# Requerimiento por área y turno
st.sidebar.header("Requerimiento por área y turno (n° operarios)")
req_matrix = {}
for s in shifts:
    st.sidebar.markdown(f"Turno: {s['id']}")
    for a in areas:
        key = f"req_{s['id']}_{a}"
        req = st.sidebar.number_input(f"{a} - {s['id']}", min_value=0, max_value=20, value=1, key=key)
        req_matrix[(s["id"], a)] = int(req)

# Temporales entrantes (según tu mensaje prev.)
st.sidebar.header("Temporales entrantes")
temp_surf = st.sidebar.number_input("Temporales SURF", min_value=0, max_value=50, value=2)
temp_bodega = st.sidebar.number_input("Temporales Bodega", min_value=0, max_value=50, value=1)
temp_em = st.sidebar.number_input("Temporales E&M", min_value=0, max_value=50, value=1)
temp_calidad = st.sidebar.number_input("Temporales Calidad", min_value=0, max_value=50, value=1)

# Global constraints
max_hours_per_day = st.sidebar.number_input("Horas máximas por día por operario", min_value=1, max_value=24, value=12)
max_consec_days = st.sidebar.number_input("Máx. días consecutivos permitidos (descanso mínimo 1 día)", min_value=1, max_value=7, value=6)
max_shifts_per_week = st.sidebar.number_input("Máx. turnos por semana (aprox.)", min_value=1, max_value=7, value=6)

# -----------------------------
# Preprocesamiento
# -----------------------------
def parse_avail(av_str):
    if pd.isna(av_str) or str(av_str).strip()=="":
        return set(["Mon","Tue","Wed","Thu","Fri","Sat"])
    tokens = [t.strip() for t in str(av_str).replace(";",",").split(",") if t.strip()]
    norm = set()
    for t in tokens:
        norm.add(t[:3].title())
    return norm

def parse_areas(a_str):
    if pd.isna(a_str) or str(a_str).strip()=="":
        return []
    return [x.strip() for x in str(a_str).replace(";",",").split(",") if x.strip()]

# Build ops list from df_ops
ops = []
for _, row in df_ops.iterrows():
    name = row.get("name")
    if pd.isna(name) or not str(name).strip():
        continue
    op_areas = parse_areas(row.get("areas",""))
    contract_hours = float(row.get("contract_hours", 48))
    availability = parse_avail(row.get("availability","Mon,Tue,Wed,Thu,Fri,Sat"))
    ops.append({
        "name": name,
        "areas": op_areas,
        "contract_hours": contract_hours,
        "availability": availability,
        "assigned_hours": 0.0,
        "assigned_shifts": 0,
        "assigned_dates": set(),
    })

# Add temporales
temp_id = 1
def add_temps(count, area_name):
    global temp_id
    for i in range(int(count)):
        ops.append({
            "name": f"TEMP_{area_name}_{temp_id}",
            "areas": [area_name],
            "contract_hours": 48.0,
            "availability": set(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]),
            "assigned_hours": 0.0,
            "assigned_shifts": 0,
            "assigned_dates": set(),
        })
        temp_id += 1

add_temps(temp_surf, "SURF")
add_temps(temp_bodega, "BODEGA")
add_temps(temp_em, "E&M")
add_temps(temp_calidad, "CALIDAD")

if len(ops) == 0:
    st.warning("No hay operarios definidos. Carga la plantilla o pega CSV.")
    st.stop()

st.write(f"Operarios totales (incluye temporales): {len(ops)}")
st.dataframe(pd.DataFrame(ops)[["name","areas","contract_hours"]])

# -----------------------------
# Reglas de asignación
# -----------------------------
def can_assign(op, date, shift_hours):
    dow = date.strftime("%a")[:3]
    if dow not in op["availability"]:
        return False
    if op["assigned_hours"] + shift_hours > op["contract_hours"]:
        return False
    # check consecutive days
    consec = 0
    for d in range(1, max_consec_days+1):
        if (date - timedelta(days=d)) in op["assigned_dates"]:
            consec += 1
        else:
            break
    if consec >= max_consec_days:
        return False
    if shift_hours > max_hours_per_day:
        return False
    if op["assigned_shifts"] >= max_shifts_per_week:
        return False
    return True

# -----------------------------
# Generador heurístico (greedy)
# -----------------------------
st.header("Generar horario propuesto")
if st.button("Generar horario"):
    schedule = []
    # reset counters
    for o in ops:
        o["assigned_hours"] = 0.0
        o["assigned_shifts"] = 0
        o["assigned_dates"] = set()

    # index by area
    ops_by_area = {}
    for a in areas:
        ops_by_area[a] = [o for o in ops if (a in o["areas"]) or (len(o["areas"])==0)]

    for current_day in days:
        for s in shifts:
            shift_hours = s["hours"]
            for a in areas:
                needed = req_matrix.get((s["id"], a), 0)
                for seat in range(needed):
                    candidates = []
                    for o in ops_by_area.get(a, []):
                        if can_assign(o, current_day, shift_hours):
                            candidates.append(o)
                    # relax rules if no candidates
                    if not candidates:
                        for o in ops_by_area.get(a, []):
                            dow_ok = current_day.strftime("%a")[:3] in o["availability"]
                            if dow_ok:
                                # allow even if near contract or shifts/week limit, but respect consecutive days
                                consec = 0
                                for d in range(1, max_consec_days+1):
                                    if (current_day - timedelta(days=d)) in o["assigned_dates"]:
                                        consec += 1
                                    else:
                                        break
                                if consec < max_consec_days:
                                    candidates.append(o)
                    if not candidates:
                        schedule.append({
                            "Fecha": current_day,
                            "Día": current_day.strftime("%a %d-%b"),
                            "Turno": s["id"],
                            "Área": a,
                            "Operario": None,
                            "Horas": shift_hours
                        })
                        continue
                    chosen = sorted(candidates, key=lambda x: (x["assigned_hours"], x["assigned_shifts"]))[0]
                    chosen["assigned_hours"] += shift_hours
                    chosen["assigned_shifts"] += 1
                    chosen["assigned_dates"].add(current_day)
                    schedule.append({
                        "Fecha": current_day,
                        "Día": current_day.strftime("%a %d-%b"),
                        "Turno": s["id"],
                        "Área": a,
                        "Operario": chosen["name"],
                        "Horas": shift_hours
                    })

    df_schedule = pd.DataFrame(schedule)
    summary_hours = df_schedule.groupby("Operario")["Horas"].sum().reset_index().sort_values("Horas", ascending=False)
    summary_shifts = df_schedule.groupby("Operario")["Turno"].count().reset_index().rename(columns={"Turno":"Turnos"})
    summary = summary_hours.merge(summary_shifts, on="Operario", how="outer").fillna(0)

    st.subheader("Horario propuesto (detalle)")
    st.dataframe(df_schedule)
    st.download_button("Descargar horario (CSV)", data=df_schedule.to_csv(index=False).encode("utf-8"), file_name="horario_propuesto.csv", mime="text/csv")

    st.subheader("Resumen por operario")
    st.dataframe(summary)

    st.success("Horario generado con heurístico. Revisa huecos (Operario=None) y ajusta parámetros si hace falta.")
else:
    st.info("Pulsa 'Generar horario' para obtener la propuesta con la plantilla actual.")
