import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="Finance AI Dashboard Pro", layout="wide")

# ---------- LOGIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Finance AI Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------- MAIN APP ----------
st.title("🌙 Finance AI Dashboard Pro")

# Dark Theme CSS
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Load Data
df = pd.read_csv("invoices.csv")

# Sidebar
st.sidebar.header("Filters")

status_filter = st.sidebar.selectbox(
    "Status",
    ["All"] + list(df["status"].unique())
)

vendor_search = st.sidebar.text_input("Search Vendor")

filtered_df = df.copy()

if status_filter != "All":
    filtered_df = filtered_df[filtered_df["status"] == status_filter]

if vendor_search:
    filtered_df = filtered_df[
        filtered_df["vendor"].str.contains(vendor_search, case=False, na=False)
    ]

# Metrics
total_value = filtered_df["amount"].sum()
overdue = len(filtered_df[filtered_df["status"] == "Overdue"])
pending = len(filtered_df[filtered_df["status"] == "Pending"])
paid = len(filtered_df[filtered_df["status"] == "Paid"])

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Value", f"₹{total_value}")
c2.metric("⚠️ Overdue", overdue)
c3.metric("🕒 Pending", pending)
c4.metric("✅ Paid", paid)

st.markdown("---")

# Table
st.subheader("Invoice Records")
st.dataframe(filtered_df, use_container_width=True)

# CSV Download
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download CSV",
    csv,
    "finance_report.csv",
    "text/csv"
)

# PDF Export
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Finance Invoice Report", ln=True)

    for i, row in filtered_df.iterrows():
        pdf.cell(
            200,
            10,
            txt=f"{row['invoice_id']} | {row['vendor']} | Rs.{row['amount']} | {row['status']}",
            ln=True
        )

    pdf.output("finance_report.pdf")

if st.button("📄 Generate PDF Report"):
    create_pdf()

    with open("finance_report.pdf", "rb") as f:
        st.download_button(
            "⬇️ Download PDF",
            f,
            file_name="finance_report.pdf",
            mime="application/pdf"
        )

st.markdown("---")

# Chart
st.subheader("Status Chart")

status_counts = filtered_df["status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]

fig = px.bar(
    status_counts,
    x="Status",
    y="Count",
    color="Status",
    text="Count"
)

st.plotly_chart(fig, use_container_width=True)