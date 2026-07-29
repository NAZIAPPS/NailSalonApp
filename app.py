import sqlite3
from datetime import date
from pathlib import Path

import streamlit as st

from database.database import create_database


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="Nail Salon",
    page_icon="💅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

create_database()


# -----------------------------
# Mobile styling
# -----------------------------
st.markdown(
    """
    <style>
        .block-container {
            max-width: 520px;
            padding-top: 1rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        h1 {
            font-size: 28px !important;
            margin-bottom: 0 !important;
        }

        .welcome-text {
            color: #777777;
            font-size: 15px;
            margin-bottom: 20px;
        }

        .summary-card {
            background: white;
            border: 1px solid #eeeeee;
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 12px;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
        }

        .card-title {
            color: #777777;
            font-size: 14px;
            margin-bottom: 5px;
        }

        .card-value {
            color: #222222;
            font-size: 26px;
            font-weight: 700;
        }

        .section-title {
            font-size: 19px;
            font-weight: 700;
            margin-top: 24px;
            margin-bottom: 12px;
        }

        div.stButton > button {
            width: 100%;
            min-height: 52px;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Database connection
# -----------------------------
database_path = Path("database") / "nails.db"

connection = sqlite3.connect(database_path)
cursor = connection.cursor()


# Today's totals
today = date.today().isoformat()

cursor.execute(
    """
    SELECT
        COALESCE(SUM(amount), 0),
        COALESCE(SUM(tip), 0),
        COUNT(*)
    FROM services
    WHERE service_date = ?
    """,
    (today,),
)

today_income, today_tips, today_services = cursor.fetchone()


# Current month totals
current_month = date.today().strftime("%Y-%m")

cursor.execute(
    """
    SELECT
        COALESCE(SUM(amount), 0),
        COUNT(*)
    FROM services
    WHERE substr(service_date, 1, 7) = ?
    """,
    (current_month,),
)

month_income, month_services = cursor.fetchone()

connection.close()


# -----------------------------
# Header
# -----------------------------
st.title("💅 Nail Salon")

st.markdown(
    '<div class="welcome-text">Today’s salon overview</div>',
    unsafe_allow_html=True,
)


# -----------------------------
# Summary cards
# -----------------------------
st.markdown(
    f"""
    <div class="summary-card">
        <div class="card-title">Today’s Income</div>
        <div class="card-value">AED {today_income:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="summary-card">
        <div class="card-title">Today’s Clients</div>
        <div class="card-value">{today_services}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="summary-card">
        <div class="card-title">This Month</div>
        <div class="card-value">AED {month_income:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="summary-card">
        <div class="card-title">Today’s Tips</div>
        <div class="card-value">AED {today_tips:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Quick menu
# -----------------------------
st.markdown(
    '<div class="section-title">Quick Menu</div>',
    unsafe_allow_html=True,
)

if st.button("➕ Add New Service", use_container_width=True):
    st.switch_page("pages/1_Daily_Work.py")

if st.button("📋 View Records", use_container_width=True):
    st.switch_page("pages/2_Records.py")

if st.button("👤 Clients", use_container_width=True):
    st.switch_page("pages/5_Clients.py")

if st.button("📊 Monthly Report", use_container_width=True):
    st.switch_page("pages/3_Monthly_Report.py")

if st.button("📤 Export to Excel", use_container_width=True):
    st.switch_page("pages/4_Export.py")