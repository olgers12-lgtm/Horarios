# Reemplaza/usa estas funciones en tu app Streamlit para evitar errores cuando xlsxwriter no está instalado.
# Uso: importa df_to_excel_bytes y usa el bloque de descarga seguro mostrado abajo.

import io
import pandas as pd
import streamlit as st

def df_to_excel_bytes(df: pd.DataFrame) -> bytes | None:
    """
    Intenta escribir df a XLSX en memoria usando primero xlsxwriter, luego openpyxl.
    Si ambos fallan (paquetes no instalados), devuelve None.
    """
    output = io.BytesIO()

    # Intento 1: xlsxwriter (generalmente más rápido y fiable para formatos)
    try:
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Asignaciones")
            # writer.save() no es necesario dentro del context manager en pandas >= 1.2
        return output.getvalue()
    except Exception as e_xlsxwriter:
        # No panic: intentamos openpyxl
        # (podría ser ImportError por no instalado, u otro error)
        # limpiar buffer
        output.seek(0)
        output.truncate(0)

    # Intento 2: openpyxl
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Asignaciones")
        return output.getvalue()
    except Exception as e_openpyxl:
        # Ningún motor disponible -> devolvemos None, el caller debe hacer fallback a CSV
        return None

# Ejemplo de uso seguro en tu app Streamlit (reemplaza tu bloque de descarga por esto):
def download_schedule_safe(df_schedule: pd.DataFrame, label_prefix: str = "horario_propuesto"):
    """
    Botón(s) de descarga que no rompen la app si faltan paquetes Excel.
    - Intenta Excel (xlsx) con df_to_excel_bytes
    - Si no disponible, muestra aviso y ofrece CSV
    """
    # Primero CSV (siempre disponible)
    csv_bytes = df_schedule.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"Descargar {label_prefix}.csv",
        data=csv_bytes,
        file_name=f"{label_prefix}.csv",
        mime="text/csv",
    )

    # Intentar Excel
    excel_bytes = df_to_excel_bytes(df_schedule)
    if excel_bytes is not None:
        st.download_button(
            label=f"Descargar {label_prefix}.xlsx",
            data=excel_bytes,
            file_name=f"{label_prefix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.warning(
            "No hay motor Excel instalado en este entorno (xlsxwriter/openpyxl). "
            "Si deseas descargar .xlsx instala 'xlsxwriter' o 'openpyxl'.\n"
            "Comando: pip install xlsxwriter openpyxl"
        )
