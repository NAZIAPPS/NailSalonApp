import streamlit as st
from datetime import date
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "nails.db"


def save_record(
    service_date,
    client_name,
    phone,
    service_name,
    amount,
    tip,
    payment_method,
    notes
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO services (
            service_date,
            client_name,
            phone,
            service_name,
            amount,
            tip,
            payment_method,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(service_date),
        client_name,
        phone,
        service_name,
        amount,
        tip,
        payment_method,
        notes
    ))

    conn.commit()
    conn.close()


st.set_page_config(
    page_title="Daily Work",
    page_icon="💅",
    layout="centered"
)

st.title("💅 Daily Work Entry")

with st.form("daily_work_form", clear_on_submit=True):

    service_date = st.date_input(
        "Date",
        value=date.today()
    )

    client_name = st.text_input("Client Name")

    phone = st.text_input("Phone Number")

    service_name = st.selectbox(
        "Service",
        [
            "Gel Manicure",
            "Gel Extension",
            "Refill",
            "Manicure",
            "Pedicure",
            "Nail Art",
            "Removal",
            "Other"
        ]
    )

    amount = st.number_input(
        "Service Amount",
        min_value=0.0,
        step=10.0
    )

    tip = st.number_input(
        "Tip",
        min_value=0.0,
        step=5.0
    )

    payment_method = st.selectbox(
        "Payment Method",
        [
            "Cash",
            "Card",
            "Bank Transfer"
        ]
    )

    notes = st.text_area("Notes")

    submitted = st.form_submit_button(
        "Save Record",
        use_container_width=True
    )

    if submitted:

        if not client_name.strip():
            st.error("Please enter the client name.")

        else:
            save_record(
                service_date,
                client_name,
                phone,
                service_name,
                amount,
                tip,
                payment_method,
                notes
            )

            st.success("Record saved successfully.")
