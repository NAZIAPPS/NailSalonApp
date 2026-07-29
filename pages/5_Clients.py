import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Clients",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        .block-container {
            max-width: 520px;
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 3rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        h1 {
            font-size: 27px !important;
        }

        .client-card {
            background: white;
            border: 1px solid #eeeeee;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
        }

        .client-name {
            font-size: 19px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .client-info {
            color: #666666;
            font-size: 14px;
            line-height: 1.8;
        }

        div.stButton > button {
            width: 100%;
            min-height: 48px;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("👤 Clients")
st.caption("Search clients and view their service history")


database_path = Path("database") / "nails.db"

if not database_path.exists():
    st.error("Database file was not found.")
    st.stop()


connection = sqlite3.connect(database_path)


query = """
SELECT
    TRIM(client_name) AS client_name,
    MAX(phone) AS phone,
    COUNT(*) AS visit_count,
    COALESCE(SUM(amount), 0) AS total_paid,
    COALESCE(SUM(tip), 0) AS total_tips,
    MAX(service_date) AS last_visit
FROM services
WHERE client_name IS NOT NULL
  AND TRIM(client_name) != ''
GROUP BY LOWER(TRIM(client_name))
ORDER BY last_visit DESC
"""


clients_df = pd.read_sql_query(query, connection)


if clients_df.empty:
    connection.close()
    st.info("No clients have been recorded yet.")

    if st.button("➕ Add New Service", use_container_width=True):
        st.switch_page("pages/1_Daily_Work.py")

    st.stop()


search_text = st.text_input(
    "Search client",
    placeholder="Enter client name or phone",
)


filtered_df = clients_df.copy()

if search_text.strip():
    search_value = search_text.strip().lower()

    filtered_df = filtered_df[
        filtered_df["client_name"]
        .fillna("")
        .str.lower()
        .str.contains(search_value, regex=False)
        |
        filtered_df["phone"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(search_value, regex=False)
    ]


st.write(f"Clients found: **{len(filtered_df)}**")


if filtered_df.empty:
    connection.close()
    st.warning("No matching client was found.")
    st.stop()


client_names = filtered_df["client_name"].tolist()

selected_client = st.selectbox(
    "Select client",
    client_names,
)


selected_row = filtered_df[
    filtered_df["client_name"] == selected_client
].iloc[0]


phone = selected_row["phone"]

if pd.isna(phone) or str(phone).strip() == "":
    phone = "Not recorded"


st.markdown(
    f"""
    <div class="client-card">
        <div class="client-name">{selected_row["client_name"]}</div>

        <div class="client-info">
            📞 Phone: {phone}<br>
            💅 Visits: {int(selected_row["visit_count"])}<br>
            💰 Total Paid: AED {float(selected_row["total_paid"]):,.2f}<br>
            ⭐ Total Tips: AED {float(selected_row["total_tips"]):,.2f}<br>
            📅 Last Visit: {selected_row["last_visit"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


history_query = """
SELECT
    service_date AS Date,
    service_name AS Service,
    amount AS Amount,
    tip AS Tip,
    payment_method AS Payment,
    notes AS Notes
FROM services
WHERE LOWER(TRIM(client_name)) = LOWER(TRIM(?))
ORDER BY service_date DESC, id DESC
"""


history_df = pd.read_sql_query(
    history_query,
    connection,
    params=(selected_client,),
)

connection.close()


st.subheader("Service History")


if history_df.empty:
    st.info("No service history was found.")

else:
    for _, record in history_df.iterrows():

        service_date = record["Date"]
        service_name = record["Service"]

        if pd.isna(service_name) or str(service_name).strip() == "":
            service_name = "Service"

        amount = float(record["Amount"] or 0)
        tip = float(record["Tip"] or 0)

        payment = record["Payment"]

        if pd.isna(payment) or str(payment).strip() == "":
            payment = "Not recorded"

        notes = record["Notes"]

        if pd.isna(notes) or str(notes).strip() == "":
            notes = "No notes"

        with st.expander(
            f"{service_date} — {service_name} — AED {amount:,.2f}"
        ):
            st.write(f"**Service:** {service_name}")
            st.write(f"**Amount:** AED {amount:,.2f}")
            st.write(f"**Tip:** AED {tip:,.2f}")
            st.write(f"**Payment:** {payment}")
            st.write(f"**Notes:** {notes}")


st.divider()


if st.button("➕ Add New Service", use_container_width=True):
    st.switch_page("pages/1_Daily_Work.py")

if st.button("🏠 Back to Home", use_container_width=True):
    st.switch_page("app.py")