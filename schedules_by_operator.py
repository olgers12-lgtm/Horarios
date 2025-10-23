# Planificador pro (sin plotly/matplotlib) — Gantt HTML/CSS, validaciones y edición
# Ejecutar: streamlit run schedules_by_operator_pro.py
# Objetivo: versión "senior" que NO requiere plotly ni matplotlib.
# - Gantt construida con HTML/CSS (responsive, interactiva en navegador).
# - Validaciones automáticas (doble turno, exceso horas, días consecutivos).
# - Añadir temporales, filtro por área, búsqueda, edición y export CSV/Excel.
# - Documentado y modular para fácil extensión a ILP/optimización si se requiere.

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Planificador PRO — Gantt HTML/CSS (sin plotly)", layout="wide")
st.title("Planificador PRO — Gantt en HTML/CSS (sin dependencias)")

# -------------------------
# Helpers y configuración
# -------------------------
def iso_date(d):
    return d.strftime("%Y-%m-%d")

def parse_avail(av_str):
    if pd.isna(av_str) or str(av_str).strip()=="":
        return set(["Mon","Tue","Wed","Thu","Fri","Sat"])
    tokens = [t.strip() for t in str(av_str).replace(";",",").split(",") if t.strip()]
    return set([tok[:3].title() for tok in tokens])

def parse_areas(a_str):
    if pd.isna(a_str) or str(a_str).strip()=="":
        return []
    return [x.strip() for x in str(a_str).replace(";",",").split(",") if x.strip()]

def hours_between(start_dt, end_dt):
    return (end_dt - start_dt).total_seconds() / 3600.0

def datetime_for_day_and_hour(day, hour):
    return datetime.combine(day, datetime.min.time()) + timedelta(hours=hour)

def df_to_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Asignaciones")
        writer.save()
    return output.getvalue()

# -------------------------
# Default operators list (user provided)
# -------------------------
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
df_ops_default["availability"] = "Mon,Tue,Wed,Thu,Fri,Sat"

st.sidebar.header("Plantilla de operarios")
try:
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

# -------------------------
# Plan params + shifts
# -------------------------
st.sidebar.header("Parámetros de planificación")
start_date = st.sidebar.date_input("Fecha inicio", value=datetime(2025,12,1).date())
num_days = st.sidebar.number_input("Número de días a planificar", min_value=1, max_value=31, value=14)
days = [(start_date + timedelta(days=i)) for i in range(num_days)]
date_range_start = datetime.combine(days[0], datetime.min.time()) + timedelta(hours=6)   # 06:00 day 1
date_range_end = datetime.combine(days[-1], datetime.min.time()) + timedelta(days=1, hours=6)  # 06:00 after last day

default_shifts = {
    "06-14": {"start":6, "end":14},
    "07-15": {"start":7, "end":15},
    "08-16": {"start":8, "end":16},
    "09-17": {"start":9, "end":17},
    "14-21": {"start":14, "end":21},
    "18-00": {"start":18, "end":0},
    "21-06": {"start":21, "end":6},
    "AR_06-14": {"start":6, "end":14},
    "AR_14-22": {"start":14, "end":22},
    "AR_22-06": {"start":22, "end":6},
    "SURF_06-21": {"start":6, "end":21},
    "06-12": {"start":6, "end":12},
}

unique_areas = sorted(set(df_ops["areas"].dropna().unique()))
areas_text = st.sidebar.text_area("Áreas (editar/agregar)", value=",".join(unique_areas))
areas = [a.strip() for a in areas_text.split(",") if a.strip()]

st.sidebar.header("Requerimientos por área/turno")
req_matrix = {}
for a in areas:
    st.sidebar.markdown(f"Área: {a}")
    suggested = ["06-14","07-15","08-16","09-17"]
    chosen = st.sidebar.multiselect(f"Turnos para {a}", options=list(default_shifts.keys()), default=suggested, key=f"sh_{a}")
    for sh in chosen:
        key = f"req_{sh}_{a}"
        req = st.sidebar.number_input(f"{a} - {sh}", min_value=0, max_value=20, value=1, key=key)
        req_matrix[(sh,a)] = int(req)

st.sidebar.header("Temporales")
temp_surf = st.sidebar.number_input("Temporales SURF", min_value=0, max_value=50, value=2)
temp_bodega = st.sidebar.number_input("Temporales BODEGA", min_value=0, max_value=50, value=1)
temp_em = st.sidebar.number_input("Temporales E&M", min_value=0, max_value=50, value=1)
temp_calidad = st.sidebar.number_input("Temporales CALIDAD", min_value=0, max_value=50, value=1)
if st.sidebar.button("Añadir temporales"):
    def append_temps(df_ops_local, count, area):
        if count <= 0: return df_ops_local
        rows=[]
        base = len(df_ops_local)
        for i in range(int(count)):
            rows.append({"name":f"TEMP_{area}_{base+i+1}", "areas": area, "contract_hours":48, "availability":"Mon,Tue,Wed,Thu,Fri,Sat,Sun"})
        return pd.concat([df_ops_local, pd.DataFrame(rows)], ignore_index=True)
    df_ops = append_temps(df_ops, temp_surf, "SURF")
    df_ops = append_temps(df_ops, temp_bodega, "BODEGA")
    df_ops = append_temps(df_ops, temp_em, "E&M")
    df_ops = append_temps(df_ops, temp_calidad, "CALIDAD")
    st.sidebar.success("Temporales añadidos. Pulsa Generar.")

# Constraints
max_hours_per_day = st.sidebar.number_input("Horas máximas por día (por operario)", min_value=1, max_value=24, value=12)
max_consec_days = st.sidebar.number_input("Máx. días consecutivos", min_value=1, max_value=7, value=6)

# -------------------------
# Build internal ops list
# -------------------------
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
        "daily_hours": {},
        "assigned_dates": set()
    })

st.write(f"Operarios cargados: {len(ops)}")

# -------------------------
# Assignment (heuristic)
# -------------------------
st.header("Generar horario (propuesta)")
if st.button("Generar horario"):
    schedule = []
    # reset
    for o in ops:
        o["assigned_hours"]=0.0
        o["daily_hours"]={}
        o["assigned_dates"]=set()
    ops_by_area = {}
    for a in areas:
        ops_by_area[a] = [o for o in ops if (a in o["areas"]) or (len(o["areas"])==0)]
    for d in days:
        dow = d.strftime("%a")[:3]
        for (sh,a), needed in req_matrix.items():
            if needed <= 0: 
                continue
            sh_def = default_shifts.get(sh, {"start":6,"end":14})
            s_start = sh_def["start"]
            s_end = sh_def["end"]
            start_dt = datetime.combine(d, datetime.min.time()) + timedelta(hours=s_start)
            end_dt = datetime.combine(d, datetime.min.time()) + timedelta(hours=s_end)
            if s_end <= s_start:
                end_dt += timedelta(days=1)
            shift_hours = hours_between(start_dt, end_dt)
            for slot in range(int(needed)):
                candidates=[]
                for o in ops_by_area.get(a, []):
                    if dow not in o["availability"]:
                        continue
                    if d in o["assigned_dates"]:
                        continue
                    if o["daily_hours"].get(d,0)+shift_hours > max_hours_per_day:
                        continue
                    consec = 0
                    for k in range(1, max_consec_days+1):
                        if (d - timedelta(days=k)) in o["assigned_dates"]:
                            consec += 1
                        else:
                            break
                    if consec >= max_consec_days:
                        continue
                    if o["assigned_hours"] + shift_hours <= o["contract_hours"]:
                        candidates.append((0,o))
                    else:
                        candidates.append((1,o))
                if not candidates:
                    # relax rules
                    for o in ops_by_area.get(a, []):
                        dow_ok = d.strftime("%a")[:3] in o["availability"]
                        if not dow_ok:
                            continue
                        if d in o["assigned_dates"]:
                            continue
                        if o["daily_hours"].get(d,0)+shift_hours <= max_hours_per_day:
                            candidates.append((2,o))
                if not candidates:
                    schedule.append({
                        "Fecha": d, "Start": start_dt, "End": end_dt, "Área": a, "Turno": sh, "Operario": None, "Horas": shift_hours
                    })
                    continue
                chosen = sorted(candidates, key=lambda x:(x[0], x[1]["assigned_hours"]))[0][1]
                chosen["assigned_hours"] += shift_hours
                chosen["daily_hours"][d] = chosen["daily_hours"].get(d,0)+shift_hours
                chosen["assigned_dates"].add(d)
                schedule.append({
                    "Fecha": d, "Start": start_dt, "End": end_dt, "Área": a, "Turno": sh, "Operario": chosen["name"], "Horas": shift_hours
                })
    df_schedule = pd.DataFrame(schedule)
    st.subheader("Horario propuesto (editable si tu Streamlit soporta data_editor)")
    try:
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
        df_schedule = edited.copy()

    # Validations
    def validate(df_sch):
        issues=[]
        by_op={}
        for idx, r in df_sch.iterrows():
            op = r.get("Operario")
            if pd.isna(op) or op is None:
                continue
            name=str(op)
            fecha = pd.to_datetime(r["Fecha"]).date() if not pd.isna(r["Fecha"]) else None
            hrs = float(r.get("Horas",0))
            by_op.setdefault(name, []).append((fecha, hrs))
        for name, rows in by_op.items():
            daily={}
            dates=set()
            for fecha, hrs in rows:
                daily[fecha]=daily.get(fecha,0)+hrs
                dates.add(fecha)
            for d, total in daily.items():
                if total > max_hours_per_day + 1e-9:
                    issues.append(f"{name} tiene {total:.1f}h el día {d} (> {max_hours_per_day}h)")
                count = sum(1 for (f,_) in rows if f==d)
                if count > 1:
                    issues.append(f"{name} tiene {count} asignaciones el día {d} (posible doble turno)")
            date_list = sorted([d for d in dates if d is not None])
            if date_list:
                consec=1
                for i in range(1,len(date_list)):
                    if (date_list[i]-date_list[i-1]).days==1:
                        consec+=1
                        if consec>max_consec_days:
                            issues.append(f"{name} excede {max_consec_days} días consecutivos hasta {date_list[i]}")
                    else:
                        consec=1
        return issues

    issues = validate(df_schedule)
    if issues:
        st.error("Conflictos detectados:")
        for it in issues:
            st.warning(it)
    else:
        st.success("Horario validado: sin conflictos detectados.")

    # Filters & search
    st.sidebar.header("Vista / filtros")
    if not df_schedule.empty:
        areas_available = sorted(df_schedule["Área"].dropna().unique())
        filter_areas = st.sidebar.multiselect("Áreas a mostrar", options=areas_available, default=areas_available)
        search_text = st.sidebar.text_input("Buscar (p. ej. TEMP)", value="")
        df_view = df_schedule[df_schedule["Área"].isin(filter_areas)].copy()
        if search_text.strip():
            mask = df_view["Operario"].fillna("").str.contains(search_text, case=False, na=False) | df_view["Área"].str.contains(search_text, case=False, na=False)
            df_view = df_view[mask]
        st.subheader("Vista filtrada")
        st.dataframe(df_view.sort_values(["Fecha","Start"]))

        # Gantt HTML/CSS build (no dependencies)
        st.subheader("Gantt (HTML/CSS, interactivo en navegador)")
        # Prepare timeline scale (hours) from date_range_start to date_range_end in hours
        total_hours = int((date_range_end - date_range_start).total_seconds() / 3600)
        # Build columns for each day label
        # Group by area, then build row bars
        areas_order = sorted(df_view["Área"].unique())
        # CSS
        gantt_css = f"""
        <style>
        .gantt-wrap {{ width:100%; overflow-x:auto; border:1px solid #ddd; padding:8px; background:#fff; }}
        .gantt-row {{ display:flex; align-items:center; gap:8px; margin-bottom:6px; }}
        .gantt-area {{ width:200px; flex:0 0 200px; font-weight:600; }}
        .gantt-bar-area {{ position:relative; height:36px; flex:1 1 auto; background:#f6f6f6; border-radius:4px; border:1px solid #eee; }}
        .gantt-item {{ position:absolute; height:28px; top:4px; border-radius:4px; padding:2px 6px; color:#fff; font-size:12px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; box-shadow: 0 1px 2px rgba(0,0,0,0.1);}}
        .gantt-legend {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px; }}
        .gantt-legend div {{ padding:4px 8px; border-radius:4px; background:#efefef; font-size:12px; }}
        </style>
        """
        # Colors map per operator (hash)
        def color_for(text):
            h = abs(hash(text)) % 360
            return f"hsl({h},65%,40%)"
        # Build HTML
        html = gantt_css + "<div class='gantt-wrap'>"
        # legend
        unique_ops = df_view["Operario"].dropna().unique().tolist()
        if unique_ops:
            html += "<div class='gantt-legend'><div><b>Legend</b></div>"
            for op in unique_ops[:30]:
                col = color_for(op)
                html += f"<div style='background:{col};color:white'>{op}</div>"
            html += "</div>"
        # rows
        for a in areas_order:
            html += "<div class='gantt-row'>"
            html += f"<div class='gantt-area'>{a}</div>"
            html += "<div class='gantt-bar-area'>"
            rows_a = df_view[df_view["Área"]==a]
            for _, r in rows_a.iterrows():
                s = pd.to_datetime(r["Start"])
                e = pd.to_datetime(r["End"])
                # clamp to date_range
                if e <= date_range_start or s >= date_range_end:
                    continue
                s2 = max(s, date_range_start)
                e2 = min(e, date_range_end)
                left_hours = (s2 - date_range_start).total_seconds()/3600.0
                width_hours = (e2 - s2).total_seconds()/3600.0
                left_pct = 100.0 * left_hours / total_hours
                width_pct = max(0.5, 100.0 * width_hours / total_hours)  # min width for visibility
                op = r.get("Operario") or "VACANTE"
                col = color_for(str(op))
                title = f"{op} | {r.get('Turno')} | {s.strftime('%d-%b %H:%M')} → {e.strftime('%d-%b %H:%M')} | {r.get('Horas')}h"
                html += f"<div class='gantt-item' title='{title}' style='left:{left_pct}%; width:{width_pct}%; background:{col};'>{op}</div>"
            html += "</div></div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

        # Downloads
        csv = df_schedule.to_csv(index=False).encode("utf-8")
        excel_bytes = df_to_excel_bytes(df_schedule)
        st.download_button("Descargar CSV", data=csv, file_name="horario_propuesto.csv", mime="text/csv")
        st.download_button("Descargar Excel", data=excel_bytes, file_name="horario_propuesto.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No hay asignaciones generadas para mostrar.")

else:
    st.info("Ajusta parámetros y pulsa 'Generar horario' para crear la propuesta.")
