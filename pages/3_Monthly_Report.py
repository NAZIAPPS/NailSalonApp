import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "nails.db"

st.set_page_config(
    page_title="Monthly Report",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Monthly Report")

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query(
    "SELECT * FROM services",
    conn
)

conn.close()

total_income = df["amount"].sum()
total_tip = df["tip"].sum()
total_clients = df["client_name"].nunique()
total_services = len(df)

col1, col2 = st.columns(2)

with col1:
    st.metric("💰 Total Income", f"AED {total_income:,.2f}")

with col2:
    st.metric("💵 Total Tips", f"AED {total_tip:,.2f}")

col3, col4 = st.columns(2)

with col3:
    st.metric("👩 Clients", total_clients)

with col4:
    st.metric("💅 Services", total_services)