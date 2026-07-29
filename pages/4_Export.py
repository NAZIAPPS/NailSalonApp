import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "nails.db"
EXPORT_PATH = Path(__file__).parent.parent / "exports"

EXPORT_PATH.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Export",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Export to Excel")

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query(
    "SELECT * FROM services",
    conn
)

conn.close()

if df.empty:
    st.warning("No data available.")
else:

    file_name = EXPORT_PATH / "Nail_Salon_Report.xlsx"

    if st.button("Create Excel File"):
        df.to_excel(file_name, index=False)

        st.success("Excel file created successfully!")

        with open(file_name, "rb") as file:
            st.download_button(
                label="Download Excel",
                data=file,
                file_name="Nail_Salon_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )