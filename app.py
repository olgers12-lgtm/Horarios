import streamlit as st
import pandas as pd
from io import BytesIO
from assign_lib import (
    parse_horario,
    aggregate_to_matrix,
    read_jobs_csv_from_filelike,
    assign_jobs_greedy,
    create_report_xlsx,
)

st.set_page_config(page_title="Scheduler - Horario por Área", layout="wide")

st.title("Scheduler: Horario por Área → Resumen y Asignación (Streamlit)")

st.markdown(
    """
Sube tu archivo HorarioArea (CSV separado por `;` o XLSX generado desde Excel).  
Opcionalmente sube un CSV de Jobs (JobID,Area,Day(optional),StartHour,Duration,Quantity).
"""
)

col1, col2 = st.columns(2)
with col1:
    horario_file = st.file_uploader("Sube HorarioArea (CSV ';' o XLSX)", type=["csv", "xlsx"])
with col2:
    jobs_file = st.file_uploader("Sube Jobs CSV (opcional)", type=["csv"])

run_button = st.button("Procesar y Generar Reporte")

if run_button:
    if not horario_file:
        st.error("Sube primero el archivo HorarioArea (CSV o XLSX).")
    else:
        with st.spinner("Parseando Horario..."):
            try:
                caps_df, capjobs_df = parse_horario(horario_file)
            except Exception as e:
                st.exception(f"Error parseando Horario: {e}")
                st.stop()

        merged = aggregate_to_matrix(caps_df, capjobs_df)
        st.success("Horario procesado correctamente.")
        st.subheader("Resumen por Area/Hour")
        # Show dataframe with conditional formatting-like coloring via pandas style
        st.dataframe(merged, height=400)

        st.markdown("### Sobrecargas (Diferencia < 0)")
        sobre = merged[merged["Diferencia"] < 0]
        if sobre.empty:
            st.info("No hay sobrecargas detectadas.")
        else:
            st.dataframe(sobre, height=250)

        # If jobs file present, run assignment option
        assignments_df = pd.DataFrame()
        jobs_result_df = pd.DataFrame()
        caprem_df = pd.DataFrame()
        if jobs_file:
            st.markdown("### Asignación de Jobs (archivo Jobs subido)")
            try:
                jobs = read_jobs_csv_from_filelike(jobs_file)
                assignments_df, jobs_result_df, caprem_df = assign_jobs_greedy(merged, jobs)
                st.success("Asignación ejecutada.")
                st.subheader("JobsResult (resumen por job)")
                st.dataframe(jobs_result_df, height=250)
                st.subheader("Assignment (detalle por job/hora)")
                st.dataframe(assignments_df, height=300)
            except Exception as e:
                st.exception(f"Error leyendo Jobs o asignando: {e}")

        # Offer downloads: CSVs and XLSX
        st.markdown("### Descargas")
        csv_resumen = merged.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar ResumenHorario.csv", csv_resumen, file_name="ResumenHorario.csv", mime="text/csv")

        csv_sobrecargas = sobre.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar Sobrecargas.csv", csv_sobrecargas, file_name="Sobrecargas.csv", mime="text/csv")

        if not assignments_df.empty:
            st.download_button("Descargar Assignment.csv", assignments_df.to_csv(index=False).encode("utf-8"), file_name="Assignment.csv", mime="text/csv")
            st.download_button("Descargar JobsResult.csv", jobs_result_df.to_csv(index=False).encode("utf-8"), file_name="JobsResult.csv", mime="text/csv")
            st.download_button("Descargar CapacityRemaining.csv", caprem_df.to_csv(index=False).encode("utf-8"), file_name="CapacityRemaining.csv", mime="text/csv")

        # Build full Excel report and provide download
        with st.spinner("Generando Report.xlsx..."):
            xlsx_bytes = create_report_xlsx(merged, assignments_df, jobs_result_df, caprem_df)
            st.download_button("Descargar Report.xlsx", xlsx_bytes, file_name="Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.success("Listo. Revisa los resultados y baja el reporte.")