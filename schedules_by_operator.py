# Scheduler interactivo - Seguro y funcional (Ingeniero Senior)
# Ejecutar: streamlit run schedules_by_operator_interactive_safe.py
# Requisitos recomendados: streamlit, pandas, numpy, plotly (opcional), matplotlib (fallback)
# - El script es robusto si faltan plotly/matplotlib (no crashea).
# - Permite añadir temporales (TEMP_{AREA}_{n}), filtrar por área, editar la tabla, validar conflictos y mostrar Gantt.

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Planificador interactivo - Seguro", layout="wide")
st.title("Planificador interactivo — (robusto, con validaciones)")

# --- Detectar librerías gráficas ---
has_plotly = True
try:
    import plotly.express as px
except Exception:
    has_plotly = False

has_matplotlib = True
if not has_plotly:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        has_matplotlib = False

if not has_plotly:
    st.sidebar.warning("plotly no está instalado. La vista Gantt será menos interactiva. Para habilitar plotly: `pip install plotly`.")
if not has_plotly and not has_matplotlib:
    st.sidebar.error("Ni plotly ni matplotlib están disponibles. La app mostrará sólo tablas. Instala plotly o matplotlib.")

# ---------------------------
# Plantilla de operarios (lista provista por el usuario)
# ---------------------------
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
df_ops_default["availability"] = "Mon,Tue,Wed,Thu,Fri,Sat"  # por defecto domingo libre

# Editable plantilla en sidebar (data editor si disponible)
st.sidebar.markdown("Plantilla de operarios (edítala si necesitas cambiar disponibilidad o contract_hours).")
try:
    # experimental_data_editor or data_editor depending on Streamlit version
    if hasattr(st.sidebar, "experimental_data_editor"):
        df_ops = st.sidebar.experimental_data_editor(df_ops_default, num_rows="dynamic")
    elif hasattr(st.sidebar, "data_editor"):
        df_ops = st.sidebar.data_editor(df_ops_default, num_rows="dynamic")
    else:
        df_ops = df_ops_default.copy()
        st.sidebar.dataframe(df_ops)
except Exception:
    df_ops = df_ops_default.copy()
    st.sidebar.dataframe(df_ops)

# ---------------------------
# Parámetros de planificación
# ---------------------------
st.sidebar.header("Parámetros de planificación")
start_date = st.sidebar.date_input("Fecha inicio", value=datetime(2025,12,1).date())
num_days = st.sidebar.number_input("Número de días a planificar", min_value=1, max_value=31, value=14)
days = [(start_date + timedelta(days=i)) for i in range(num_days)]

# Turnos por defecto (soportan cruce de medianoche)
default_shifts = {
    "06-14": {"start":6, "end":14},
    "07-15": {"start":7, "end":15},
    "08-16": {"start":8, "end":16},
    "09-17": {"start":9, "end":17},
    "14-21": {"start":14, "end":21},
    "18-00": {"start":18, "end":0},
    "21-06": {"start":21, "end":6},
    # especiales
    "AR_06-14": {"start":6, "end":14},
    "AR_14-22": {"start":14, "end":22},
    "AR_22-06": {"start":22, "end":6},
    "SURF_06-21": {"start":6, "end":21},
    "06-12": {"start":6, "end":12},
}

# Areas iniciales (tomadas de plantilla)
unique_areas = sorted(set(df_ops["areas"].dropna().unique()))
areas_text = st.sidebar.text_area("Áreas (edita / agrega si hace falta)", value=",".join(unique_areas))
areas = [a.strip() for a in areas_text.split(",") if a.strip()]

# Requerimiento por área y turno
st.sidebar.header("Requerimiento por área y turno")
req_matrix = {}
for a in areas:
    st.sidebar.markdown(f"Área: {a}")
    # por defecto sugerimos los turnos diurnos; usuario puede seleccionar otros
    suggested = ["06-14","07-15","08-16","09-17"]
    chosen = st.sidebar.multiselect(f"Turnos para {a}", options=list(default_shifts.keys()), default=suggested, key=f"sh_{a}")
    for sh in chosen:
        key = f"req_{sh}_{a}"
        req = st.sidebar.number_input(f"{a} - {sh}", min_value=0, max_value=20, value=1, key=key)
        req_matrix[(sh,a)] = int(req)

# Añadir temporales interactivamente
st.sidebar.header("Temporales - añadir")
temp_surf = st.sidebar.number_input("Temporales SURF", min_value=0, max_value=50, value=2)
temp_bodega = st.sidebar.number_input("Temporales BODEGA", min_value=0, max_value=50, value=1)
temp_em = st.sidebar.number_input("Temporales E&M", min_value=0, max_value=50, value=1)
temp_calidad = st.sidebar.number_input("Temporales CALIDAD", min_value=0, max_value=50, value=1)

if st.sidebar.button("Añadir temporales"):
    def append_temps(df_ops_local, count, area):
        if count <= 0: return df_ops_local
        rows = []
        base = len(df_ops_local)
        for i in range(int(count)):
            rows.append({"name": f"TEMP_{area}_{base+i+1}", "areas": area, "contract_hours":48, "availability":"Mon,Tue,Wed,Thu,Fri,Sat,Sun"})
        return pd.concat([df_ops_local, pd.DataFrame(rows)], ignore_index=True)
    df_ops = append_temps(df_ops, temp_surf, "SURF")
    df_ops = append_temps(df_ops, temp_bodega, "BODEGA")
    df_ops = append_temps(df_ops, temp_em, "E&M")
    df_ops = append_temps(df_ops, temp_calidad, "CALIDAD")
    st.sidebar.success("Temporales añadidos. Pulsa 'Generar horario' para asignarlos.")

# Restricciones globales
max_hours_per_day = st.sidebar.number_input("Horas máximas por día por operario", min_value=1, max_value=24, value=12)
max_consec_days = st.sidebar.number_input("Máx. días consecutivos permitidos", min_value=1, max_value=7, value=6)

# ---------------------------
# Helpers: parse availability/areas
# ---------------------------
def parse_avail(av_str):
    if pd.isna(av_str) or str(av_str).strip()=="":
        return set(["Mon","Tue","Wed","Thu","Fri","Sat"])
    tokens = [t.strip() for t in str(av_str).replace(";",",").split(",") if t.strip()]
    return set([tok[:3].title() for tok in tokens])

def parse_areas(a_str):
    if pd.isna(a_str) or str(a_str).strip()=="":
        return []
    return [x.strip() for x in str(a_str).replace(";",",").split(",") if x.strip()]

# Build ops internal list
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
        "daily_hours": {},   # map date -> hours assigned that date
        "assigned_dates": set()
    })

if len(ops) == 0:
    st.warning("No hay operarios definidos. Carga la plantilla o pega CSV.")
    st.stop()

st.write(f"Operarios totales (incluye temporales si se añadieron): {len(ops)}")
st.dataframe(pd.DataFrame([{"name":o["name"], "areas":",".join(o["areas"]), "contract_hours":o["contract_hours"]} for o in ops]))

# ---------------------------
# Asignación heurística (greedy) con reglas reales
# ---------------------------
st.header("Generar horario propuesto (interactivo y validado)")
if st.button("Generar horario"):
    schedule = []
    # reset counters
    for o in ops:
        o["assigned_hours"]=0.0
        o["daily_hours"]={}
        o["assigned_dates"]=set()

    # index por área
    ops_by_area = {}
    for a in areas:
        ops_by_area[a] = [o for o in ops if (a in o["areas"]) or (len(o["areas"])==0)]

    # iterar días y requisitos
    for d in days:
        dow = d.strftime("%a")[:3]
        for (sh,a), needed in req_matrix.items():
            if needed <= 0:
                continue
            # obtener definición del turno
            sh_def = default_shifts.get(sh, {"start":6, "end":14})
            s_start = sh_def["start"]
            s_end = sh_def["end"]
            start_dt = datetime.combine(d, datetime.min.time()) + timedelta(hours=s_start)
            end_dt = datetime.combine(d, datetime.min.time()) + timedelta(hours=s_end)
            if s_end <= s_start:
                end_dt += timedelta(days=1)
            shift_hours = (end_dt - start_dt).total_seconds() / 3600.0

            # completar plazas requeridas
            for slot in range(int(needed)):
                candidates = []
                for o in ops_by_area.get(a, []):
                    # disponibilidad por día
                    if dow not in o["availability"]:
                        continue
                    # no asignar doble turno el mismo día
                    if d in o["assigned_dates"]:
                        continue
                    # no superar horas diarias
                    daily_h = o["daily_hours"].get(d, 0.0)
                    if daily_h + shift_hours > max_hours_per_day:
                        continue
                    # verificar dias consecutivos
                    consec = 0
                    for k in range(1, max_consec_days+1):
                        if (d - timedelta(days=k)) in o["assigned_dates"]:
                            consec += 1
                        else:
                            break
                    if consec >= max_consec_days:
                        continue
                    # preferir asignaciones dentro de contract_hours (prioridad)
                    if o["assigned_hours"] + shift_hours <= o["contract_hours"]:
                        candidates.append((0, o))
                    else:
                        candidates.append((1, o))
                if not candidates:
                    # relajamos reglas si no hay candidatos: permitir asignación aunque supere contract_hours (pero evitar doble turno)
                    relaxed = []
                    for o in ops_by_area.get(a, []):
                        dow_ok = d.strftime("%a")[:3] in o["availability"]
                        if not dow_ok:
                            continue
                        if d in o["assigned_dates"]:
                            continue
                        # allow if not exceeding daily max
                        daily_h = o["daily_hours"].get(d, 0.0)
                        if daily_h + shift_hours <= max_hours_per_day:
                            relaxed.append((2, o))
                    candidates = relaxed

                if not candidates:
                    # sin candidatos posibles -> hueco
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

                chosen = sorted(candidates, key=lambda x: (x[0], x[1]["assigned_hours"]))[0][1]
                # asignar
                chosen["assigned_hours"] += shift_hours
                chosen["daily_hours"][d] = chosen["daily_hours"].get(d, 0.0) + shift_hours
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

    # Mostrar editable (si es posible)
    st.subheader("Horario propuesto (editable)")
    try:
        # experimental_data_editor / data_editor availability varies by streamlit version
        if hasattr(st, "experimental_data_editor"):
            edited = st.experimental_data_editor(df_schedule, num_rows="dynamic")
        elif hasattr(st, "data_editor"):
            edited = st.data_editor(df_schedule, num_rows="dynamic")
        else:
            edited = None
            st.dataframe(df_schedule)
    except Exception:
        edited = None
        st.dataframe(df_schedule)

    if edited is not None:
        # use edited table as final schedule (but validate)
        df_schedule = edited.copy()

    # ---------- VALIDACIONES ----------
    def validate_schedule(df_sch, max_hours_day, max_consec):
        issues = []
        # check double shift same day and daily hours > limit and consec days per operator
        by_op = {}
        for idx, r in df_sch.iterrows():
            op = r.get("Operario")
            if pd.isna(op) or op is None:
                continue
            name = str(op)
            fecha = pd.to_datetime(r["Fecha"]).date() if not pd.isna(r["Fecha"]) else None
            hrs = float(r.get("Horas", 0))
            by_op.setdefault(name, []).append((fecha, hrs, idx))
        # checks
        for name, entries in by_op.items():
            # daily hours
            daily = {}
            dates = set()
            for fecha, hrs, idx in entries:
                daily[fecha] = daily.get(fecha, 0.0) + hrs
                dates.add(fecha)
            for d, hsum in daily.items():
                if hsum > max_hours_day + 1e-6:
                    issues.append({"type":"daily_hours", "operario":name, "fecha":d, "horas":hsum})
            # double shift is implicit if multiple entries same fecha
            for d in daily:
                count = sum(1 for (f,_,_) in entries if f==d)
                if count > 1:
                    issues.append({"type":"double_shift", "operario":name, "fecha":d, "count":count})
            # consecutive days
            date_list = sorted([d for d in dates if d is not None])
            if date_list:
                consec = 1
                for i in range(1, len(date_list)):
                    if (date_list[i] - date_list[i-1]).days == 1:
                        consec += 1
                        if consec > max_consec:
                            issues.append({"type":"consec_days", "operario":name, "hasta_fecha":date_list[i], "consec":consec})
                    else:
                        consec = 1
        return issues

    issues = validate_schedule(df_schedule, max_hours_per_day, max_consec_days)

    if issues:
        st.error("Se detectaron conflictos/validaciones en el horario. Revisa la lista abajo y corrige en la tabla (o ajusta parámetros).")
        for it in issues:
            if it["type"] == "daily_hours":
                st.warning(f"Operario {it['operario']} tiene {it['horas']:.1f} h el día {it['fecha']} (máx {max_hours_per_day})")
            elif it["type"] == "double_shift":
                st.warning(f"Operario {it['operario']} tiene {it['count']} asignaciones el día {it['fecha']} (posible doble turno).")
            elif it["type"] == "consec_days":
                st.warning(f"Operario {it['operario']} excede días consecutivos ({it['consec']}) hasta {it['hasta_fecha']}.")
    else:
        st.success("Horario validado: no se detectaron conflictos críticos.")

    # ----------------------------
    # Vista filtrada y Gantt
    # ----------------------------
    st.sidebar.header("Filtrar vista")
    if not df_schedule.empty:
        areas_available = sorted(df_schedule["Área"].dropna().unique())
        filter_areas = st.sidebar.multiselect("Mostrar áreas", options=areas_available, default=areas_available)
        search_text = st.sidebar.text_input("Buscar texto (p.ej. TEMP o nombre)", value="")
        df_view = df_schedule[df_schedule["Área"].isin(filter_areas)].copy()
        if search_text.strip():
            mask = df_view["Operario"].fillna("").str.contains(search_text, case=False, na=False) | df_view["Área"].str.contains(search_text, case=False, na=False)
            df_view = df_view[mask]
        st.subheader("Vista filtrada")
        st.dataframe(df_view.sort_values(["Fecha","Start"]))

        # Gantt / timeline
        if not df_view.empty:
            if has_plotly:
                # ensure datetime dtypes
                df_view["Start"] = pd.to_datetime(df_view["Start"])
                df_view["End"] = pd.to_datetime(df_view["End"])
                fig = px.timeline(df_view, x_start="Start", x_end="End", y="Área", color="Operario", hover_data=["Turno","Horas"])
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(height=600, title="Gantt / Timeline (plotly)")
                st.plotly_chart(fig, use_container_width=True)
            elif has_matplotlib:
                import matplotlib.pyplot as plt
                st.subheader("Gantt (matplotlib fallback)")
                df_plot = df_view.copy()
                df_plot["Start_num"] = pd.to_datetime(df_plot["Start"]).astype('int64')//10**9
                df_plot["End_num"] = pd.to_datetime(df_plot["End"]).astype('int64')//10**9
                areas_plot = list(df_plot["Área"].unique())
                y_pos = {a:i for i,a in enumerate(areas_plot)}
                fig, ax = plt.subplots(figsize=(12, max(4, len(areas_plot)*0.4)))
                for _, row in df_plot.iterrows():
                    ax.barh(y_pos[row["Área"]], (row["End_num"]-row["Start_num"])/3600.0, left=pd.to_datetime(row["Start"]), height=0.4)
                ax.set_yticks(list(y_pos.values()))
                ax.set_yticklabels(list(y_pos.keys()))
                ax.set_xlabel("Fecha / Hora")
                fig.autofmt_xdate()
                st.pyplot(fig)
            else:
                st.info("No hay librería gráfica instalada; se muestra sólo la tabla.")
    else:
        st.info("No hay asignaciones para mostrar.")

    # ----------------------------
    # Descarga CSV
    # ----------------------------
    if not df_schedule.empty:
        csv = df_schedule.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar asignaciones (CSV)", data=csv, file_name="horario_propuesto.csv", mime="text/csv")

else:
    st.info("Configura parámetros (temporales / requerimientos) y pulsa 'Generar horario' para obtener la propuesta interactiva.")

# ---------------------------
# Fin del archivo
# ---------------------------
