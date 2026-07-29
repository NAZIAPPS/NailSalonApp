import sqlite3
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent.parent / "database" / "nails.db"
SERVICES = [
    "Gel Manicure",
    "Gel Extension",
    "Refill",
    "Manicure",
    "Pedicure",
    "Nail Art",
    "Removal",
    "Other",
]
PAYMENT_METHODS = ["Cash", "Card", "Bank Transfer"]

st.set_page_config(
    page_title="Records",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 720px;
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 3rem;
        }
        [data-testid="stHeader"] { background: transparent; }
        h1 { font-size: 27px !important; }
        div.stButton > button {
            width: 100%;
            min-height: 46px;
            border-radius: 13px;
            font-size: 15px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def connect():
    return sqlite3.connect(DB_PATH)


def load_records():
    with connect() as conn:
        return pd.read_sql_query(
            """
            SELECT
                id,
                service_date,
                client_name,
                phone,
                service_name,
                amount,
                tip,
                payment_method,
                notes
            FROM services
            ORDER BY service_date DESC, id DESC
            """,
            conn,
        )


def update_record(
    record_id,
    service_date,
    client_name,
    phone,
    service_name,
    amount,
    tip,
    payment_method,
    notes,
):
    with connect() as conn:
        conn.execute(
            """
            UPDATE services
            SET service_date = ?,
                client_name = ?,
                phone = ?,
                service_name = ?,
                amount = ?,
                tip = ?,
                payment_method = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                str(service_date),
                client_name.strip(),
                phone.strip(),
                service_name,
                float(amount),
                float(tip),
                payment_method,
                notes.strip(),
                int(record_id),
            ),
        )
        conn.commit()


def delete_record(record_id):
    with connect() as conn:
        conn.execute("DELETE FROM services WHERE id = ?", (int(record_id),))
        conn.commit()


def parse_date(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


st.title("📋 Records")
st.caption("Search, edit or delete saved services")

if not DB_PATH.exists():
    st.error("Database file was not found.")
    st.stop()

records_df = load_records()

if records_df.empty:
    st.info("No records found.")
    if st.button("➕ Add New Service", use_container_width=True):
        st.switch_page("pages/1_Daily_Work.py")
    st.stop()

search = st.text_input(
    "🔍 Search",
    placeholder="Client name, phone or service...",
)

filtered_df = records_df.copy()
if search.strip():
    value = search.strip().lower()
    mask = (
        filtered_df["client_name"].fillna("").astype(str).str.lower().str.contains(value, regex=False)
        | filtered_df["phone"].fillna("").astype(str).str.lower().str.contains(value, regex=False)
        | filtered_df["service_name"].fillna("").astype(str).str.lower().str.contains(value, regex=False)
    )
    filtered_df = filtered_df[mask]

st.write(f"Records found: **{len(filtered_df)}**")

if filtered_df.empty:
    st.warning("No matching record was found.")
    st.stop()

for _, row in filtered_df.iterrows():
    record_id = int(row["id"])
    client_name = str(row["client_name"] or "Unknown client")
    service_name = str(row["service_name"] or "Service")
    amount = float(row["amount"] or 0)
    service_date = str(row["service_date"] or "")

    with st.expander(
        f"{service_date} — {client_name} — {service_name} — AED {amount:,.2f}"
    ):
        st.write(f"**Phone:** {row['phone'] or 'Not recorded'}")
        st.write(f"**Tip:** AED {float(row['tip'] or 0):,.2f}")
        st.write(f"**Payment:** {row['payment_method'] or 'Not recorded'}")
        st.write(f"**Notes:** {row['notes'] or 'No notes'}")

        edit_tab, delete_tab = st.tabs(["✏️ Edit", "🗑 Delete"])

        with edit_tab:
            with st.form(f"edit_form_{record_id}"):
                edit_date = st.date_input(
                    "Date",
                    value=parse_date(row["service_date"]),
                    key=f"date_{record_id}",
                )
                edit_client = st.text_input(
                    "Client Name",
                    value=str(row["client_name"] or ""),
                    key=f"client_{record_id}",
                )
                edit_phone = st.text_input(
                    "Phone Number",
                    value=str(row["phone"] or ""),
                    key=f"phone_{record_id}",
                )

                current_service = str(row["service_name"] or "Other")
                service_options = SERVICES.copy()
                if current_service not in service_options:
                    service_options.insert(0, current_service)

                edit_service = st.selectbox(
                    "Service",
                    service_options,
                    index=service_options.index(current_service),
                    key=f"service_{record_id}",
                )
                edit_amount = st.number_input(
                    "Service Amount",
                    min_value=0.0,
                    value=float(row["amount"] or 0),
                    step=10.0,
                    key=f"amount_{record_id}",
                )
                edit_tip = st.number_input(
                    "Tip",
                    min_value=0.0,
                    value=float(row["tip"] or 0),
                    step=5.0,
                    key=f"tip_{record_id}",
                )

                current_payment = str(row["payment_method"] or "Cash")
                payment_options = PAYMENT_METHODS.copy()
                if current_payment not in payment_options:
                    payment_options.insert(0, current_payment)

                edit_payment = st.selectbox(
                    "Payment Method",
                    payment_options,
                    index=payment_options.index(current_payment),
                    key=f"payment_{record_id}",
                )
                edit_notes = st.text_area(
                    "Notes",
                    value=str(row["notes"] or ""),
                    key=f"notes_{record_id}",
                )

                save_changes = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

                if save_changes:
                    if not edit_client.strip():
                        st.error("Please enter the client name.")
                    else:
                        update_record(
                            record_id,
                            edit_date,
                            edit_client,
                            edit_phone,
                            edit_service,
                            edit_amount,
                            edit_tip,
                            edit_payment,
                            edit_notes,
                        )
                        st.success("Record updated successfully.")
                        st.rerun()

        with delete_tab:
            st.warning("Deleting this record cannot be undone.")
            confirm_delete = st.checkbox(
                "I confirm that I want to delete this record",
                key=f"confirm_delete_{record_id}",
            )
            if st.button(
                "Delete Record",
                key=f"delete_{record_id}",
                type="primary",
                disabled=not confirm_delete,
                use_container_width=True,
            ):
                delete_record(record_id)
                st.success("Record deleted successfully.")
                st.rerun()
