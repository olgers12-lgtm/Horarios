# Scheduler interactivo por operario y área - Streamlit
# - Añade temporales con nombre "TEMP_{AREA}_{n}" desde la interfaz.
# - Permite filtrar por área y buscar por texto (por ejemplo "TEMP") y editar la tabla resultante.
# - Muestra un Gantt/timeline interactivo con las asignaciones (Plotly).
# - Soporta reglas específicas: AR 24h (cobertura por 3 turnos), CAPA DURA y BISEL Y MONTAJE 06:00-12:00,
#   SURF 06:00-21:00 (se usa un turno largo para visualización).
#
# Ejecutar: streamlit run schedules_by_operator_interactive.py
#
# Requiere: streamlit, pandas, numpy, plotly

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Planificador interactivo por Operario y Área", layout="wide")
st.title("Planificador interactivo — temporales, filtro y Gantt")

# ----------------------------
# Plantilla inicial de operarios (lista que enviaste)
# ----------------------------
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
df_ops_default = pd.DataFrame(ops_data)
df_ops_default["contract_hours"] = 48
df_ops_default["availability"] = "Mon,Tue,Wed,Thu,Fri,Sat"  # default: Sunday off

# show editable template (user can tweak availability / contract hours)
st.sidebar.markdown("Plantilla de operarios (edítala si necesitas cambiar disponibilidad o contract_hours).")
try:
    df_ops = st.sidebar.experimental_data_editor(df_ops_default, num_rows="dynamic")
except Exception:
    # older Streamlit fallback
    df_ops = df_ops_default.copy()
    st.sidebar.dataframe(df_ops)

# ----------------------------
# Plan params
# ----------------------------
st.sidebar.header("Parámetros de planificación")
start_date = st.sidebar.date_input("Fecha inicio", value=datetime(2025,12,1).date())
num_days = st.sidebar.number_input("Número de días a planificar", min_value=1, max_value=31, value=14)
days = [(start_date + timedelta(days=i)) for i in range(num_days)]

# Default shifts globally available (we'll allow area-specific overrides)
default_shifts = {
    "06-14": {"start":6, "end":14},
    "07-15": {"start":7, "end":15},
    "08-16": {"start":8, "end":16},
    "09-17": {"start":9, "end":17},
    "14-21": {"start":14, "end":21},   # intermediate 7h
    "18-00": {"start":18, "end":0},    # 6h
    "21-06": {"start":21, "end":6},    # 9h crosses midnight
    # helper 24h split for AR (three 8h segments)
    "AR_06-14": {"start":6, "end":14},
    "AR_14-22": {"start":14, "end":22},
    "AR_22-06": {"start":22, "end":6},
    # SURF long shift
    "SURF_06-21": {"start":6, "end":21},
    # CAPA/Monatge (6-12)
    "06-12": {"start":6, "end":12},
}

# area-specific default shifts map (applies only to requirements builder below)
area_shift_map = {
    "AR": ["AR_06-14","AR_14-22","AR_22-06"],                # 24h coverage
    "CAPA DURA": ["06-12"],
    "CAPA_DURA": ["06-12"],
    "CAPA DURA": ["06-12"],
    "BISEL Y MONTAJE": ["06-12"],                           # montaje 6-12
    "SURF": ["SURF_06-21"],                                 # SURF 6-21
}

# Build area list from template
unique_areas = sorted(set(df_ops["areas"].dropna().unique()))
# allow user to add extra areas
areas_text = st.sidebar.text_area("Áreas separadas por coma (editar si quieres)", value=",".join(unique_areas))
areas = [a.strip() for a in areas_text.split(",") if a.strip()]

# requirements per (area, shift) with defaults (1 per slot)
st.sidebar.header("Requerimiento por área y turno")
req_matrix = {}
# create dynamic selection of shifts per area: use area_shift_map if present else default small set
for a in areas:
    st.sidebar.markdown(f"**Área: {a}**")
    # suggested shifts
    suggested = area_shift_map.get(a.upper(), ["06-14","07-15","08-16","09-17","14-21"])
    # allow selecting which shifts to use for this area
    chosen = st.sidebar.multiselect(f"Turnos para {a}", options=list(default_shifts.keys())+["AR_06-14","AR_14-22","AR_22-06","SURF_06-21","06-12"], default=suggested)
    for sh in chosen:
        key = f"req_{sh}_{a}"
        req = st.sidebar.number_input(f"{a} - {sh}", min_value=0, max_value=20, value=1, key=key)
        req_matrix[(sh,a)] = int(req)

# temporales to add interactively
st.sidebar.header("Temporales (añadir en bloque)")
temp_surf = st.sidebar.number_input("Agregar temporales SURF", min_value=0, max_value=50, value=2)
temp_bodega = st.sidebar.number_input("Agregar temporales BODEGA", min_value=0, max_value=50, value=1)
temp_em = st.sidebar.number_input("Agregar temporales E&M", min_value=0, max_value=50, value=1)
temp_calidad = st.sidebar.number_input("Agregar temporales CALIDAD", min_value=0, max_value=50, value=1)
if st.sidebar.button("Añadir temporales seleccionados"):
    # append temporales to df_ops
    def append_temps_to_df(df_ops, count, area):
        if count <= 0: 
            return df_ops
        current = len(df_ops)
        rows = []
        for i in range(int(count)):
            rows.append({
                "name": f"TEMP_{area}_{i+1+current}",
                "areas": area,
                "contract_hours": 48,
                "availability": "Mon,Tue,Wed,Thu,Fri,Sat,Sun"
            })
        df_ops = pd.concat([df_ops, pd.DataFrame(rows)], ignore_index=True)
        return df_ops
    df_ops = append_temps_to_df(df_ops, temp_surf, "SURF")
    df_ops = append_temps_to_df(df_ops, temp_bodega, "BODEGA")
    df_ops = append_temps_to_df(df_ops, temp_em, "E&M")
    df_ops = append_temps_to_df(df_ops, temp_calidad, "CALIDAD")
    st.sidebar.success("Temporales añadidos. Pulsa 'Generar horario' para ver asignaciones.")

# global constraints
max_hours_per_day = st.sidebar.number_input("Horas máximas por día por operario", min_value=1, max_value=24, value=12)
max_consec_days = st.sidebar.number_input("Máx. días consecutivos permitidos", min_value=1, max_value=7, value=6)

# ----------------------------
# Preprocess ops into internal list
# ----------------------------
def parse_avail(av_str):
    if pd.isna(av_str) or str(av_str).strip()=="":
        return set(["Mon","Tue","Wed","Thu","Fri","Sat"])
    tokens = [t.strip() for t in str(av_str).replace(";",",").split(",") if t.strip()]
    return set([tok[:3].title() for tok in tokens])

def parse_areas(a_str):
    if pd.isna(a_str) or str(a_str).strip()=="":
        return []
    return [x.strip() for x in str(a_str).replace(";",",").split(",") if x.strip()]

ops = []
for _, row in df_ops.iterrows():
    name = row.get("name")
    if pd.isna(name) or not str(name).strip(): 
        continue
    ops.append({
        "name": name,
        "areas": parse_areas(row.get("areas","")),
        "contract_hours": float(row.get("contract_hours",48)),
        "availability": parse_avail(row.get("availability","Mon,Tue,Wed,Thu,Fri,Sat")),
        "assigned_hours": 0.0,
        "assigned_dates": set()
    })

# ----------------------------
# Assignment heuristic (similar greedy) -> produce schedule rows and then allow editing
# ----------------------------
st.header("Generar horario propuesto (interactivo)")
if st.button("Generar horario"):
    schedule = []
    # reset assignments
    for o in ops:
        o["assigned_hours"]=0.0
        o["assigned_dates"]=set()
    # index ops by area
    ops_by_area = {}
    for a in areas:
        ops_by_area[a] = [o for o in ops if (a in o["areas"]) or (len(o["areas"])==0)]
    # iterate days and each requested (area,shift,slots)
    for d in days:
        dow = d.strftime("%a")[:3]
        for (sh,a), needed in req_matrix.items():
            if needed <= 0:
                continue
            # compute shift start/end hours from default_shifts dict
            if sh in default_shifts:
                s_start = default_shifts[sh]["start"]
                s_end = default_shifts[sh]["end"]
            else:
                # special keys (AR_.., SURF_..., 06-12)
                s_start = default_shifts.get(sh, {"start":6})["start"]
                s_end = default_shifts.get(sh, {"end":14})["end"]
            # compute start datetime and end datetime (handle crossing midnight)
            start_dt = datetime.combine(d, datetime.min.time()) + timedelta(hours=s_start)
            end_dt = datetime.combine(d, datetime.min.time()) + timedelta(hours=s_end)
            if s_end <= s_start:
                end_dt += timedelta(days=1)
            shift_hours = (end_dt - start_dt).total_seconds()/3600.0
            # fill needed slots
            for slot in range(needed):
                # find candidates available that day and not exceeding consecutive rule
                candidates = []
                for o in ops_by_area.get(a, []):
                    if dow not in o["availability"]:
                        continue
                    # consecutive days check
                    consec = 0
                    for k in range(1, max_consec_days+1):
                        if (d - timedelta(days=k)) in o["assigned_dates"]:
                            consec += 1
                        else:
                            break
                    if consec >= max_consec_days:
                        continue
                    # basic hours check (we allow exceeding contract_hours for flexibility but deprioritize)
                    if o["assigned_hours"] + shift_hours <= o["contract_hours"]:
                        candidates.append((0,o))  # priority 0
                    else:
                        candidates.append((1,o))  # deprioritize
                if not candidates:
                    # unfilled slot
                    schedule.append({
                        "Fecha": d,
                        "Start": start_dt,
                        "End": end_dt,
                        "Área": a,
                        "Turno": sh,
                        "Operario": None,
                        "Horas": shift_hours
                    })
                    continue
                # choose best candidate with min (priority, assigned_hours)
                candidates_sorted = sorted(candidates, key=lambda x: (x[0], x[1]["assigned_hours"]))
                chosen = candidates_sorted[0][1]
                chosen["assigned_hours"] += shift_hours
                chosen["assigned_dates"].add(d)
                schedule.append({
                    "Fecha": d,
                    "Start": start_dt,
                    "End": end_dt,
                    "Área": a,
                    "Turno": sh,
                    "Operario": chosen["name"],
                    "Horas": shift_hours
                })
    df_schedule = pd.DataFrame(schedule)
    # Show editable table
    st.subheader("Horario propuesto (edítalo si necesitas) — pulsa enter para aplicar cambios")
    try:
        edited = st.data_editor(df_schedule, num_rows="dynamic")
        # If edited, use edited as df_schedule for chart/export
        df_schedule = edited.copy()
    except Exception:
        st.dataframe(df_schedule)

    # Simple filters and search
    st.sidebar.header("Filtrar vista")
    filter_areas = st.sidebar.multiselect("Mostrar áreas", options=sorted(df_schedule["Área"].unique()), default=sorted(df_schedule["Área"].unique()))
    search_text = st.sidebar.text_input("Buscar texto (p.ej. TEMP)", value="TEMP")

    df_view = df_schedule[df_schedule["Área"].isin(filter_areas)].copy()
    if search_text.strip():
        df_view = df_view[df_view["Operario"].fillna("").str.contains(search_text, case=False, na=False) | df_view["Área"].str.contains(search_text, case=False, na=False)]

    st.subheader("Vista filtrada (tabla)")
    st.dataframe(df_view.sort_values(["Fecha","Start"]))

    # Gantt / timeline using plotly
    import plotly.express as px
    if not df_view.empty:
        # prepare strings for hover and convert to local display
        df_view["Start_str"] = df_view["Start"].dt.strftime("%Y-%m-%d %H:%M")
        df_view["End_str"] = df_view["End"].dt.strftime("%Y-%m-%d %H:%M")
        fig = px.timeline(df_view, x_start="Start", x_end="End", y="Área", color="Operario", hover_data=["Turno","Horas","Start_str","End_str"])
        fig.update_yaxes(autorange="reversed")  # so earlier areas are top
        fig.update_layout(height=600, title="Gantt / Timeline de asignaciones")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay filas en la vista filtrada.")

    # Download
    csv = df_schedule.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar asignaciones (CSV)", data=csv, file_name="horario_propuesto.csv", mime="text/csv")

else:
    st.info("Configura parámetros y pulsa 'Generar horario' para ver la propuesta interactiva.")
