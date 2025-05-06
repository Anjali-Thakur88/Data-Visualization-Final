# app_openfda.py

import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Drug Safety Dashboard",
    layout="wide",
)

# --- Sidebar navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Top Drugs", "Search by Drug", "Role Distribution"])


# --- Data loader for Top Drugs ---
@st.cache_data
def load_events(limit: int = 100) -> pd.DataFrame:
    """
    Fetch the most recent `limit` adverse-event reports from openFDA.
    Returns a DataFrame with columns: date, drug, role.
    """
    url = "https://api.fda.gov/drug/event.json"
    params = {"limit": limit}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    results = resp.json().get("results", [])

    records = []
    for ev in results:
        for drug in ev.get("patient", {}).get("drug", []):
            records.append({
                "date":  ev.get("receiptdate"),
                "drug":  drug.get("medicinalproduct", "").strip(),
                "role":  drug.get("drugcharacterization"),
            })

    return pd.DataFrame(records)


# --- Data loader using FDA search API for specific drug queries ---
@st.cache_data
def load_search_events(drug_name: str, limit: int = 200) -> pd.DataFrame:
    """
    Pull up to `limit` reports matching exactly `drug_name` via the openFDA search API.
    """
    url = "https://api.fda.gov/drug/event.json"
    query = f'patient.drug.medicinalproduct:"{drug_name}"'
    params = {"search": query, "limit": limit}
    resp = requests.get(url, params=params)
    if resp.status_code == 404:
        return pd.DataFrame()
    resp.raise_for_status()
    results = resp.json().get("results", [])

    records = []
    for ev in results:
        for drug in ev.get("patient", {}).get("drug", []):
            name = drug.get("medicinalproduct", "").strip()
            if name.lower() == drug_name.lower():
                records.append({
                    "date": ev.get("receiptdate"),
                    "drug": name,
                    "role": drug.get("drugcharacterization"),
                })
    return pd.DataFrame(records)


# --- Page: Top Drugs ---
def page_top_drugs():
    st.title("🏆 Top Reported Drugs (last 100 events)")
    df = load_events(limit=100)
    if df.empty or "drug" not in df.columns:
        st.warning("No data available. Try again shortly.")
        return

    # Compute top 10
    top10 = df["drug"].value_counts().nlargest(10)

    # Provide context and insights
    st.write(
        "This bar chart shows the number of FDA adverse event reports for the top 10 most frequently reported drugs in our sample of 100 recent records."
    )
    st.write("Longer bars indicate more total reports.")

    # Draw bar chart and legend
    chart_df = top10.to_frame(name='Report Count')
    st.bar_chart(chart_df)
    st.write("**Legend:** Bar height = number of FDA adverse event reports for each drug.")


# --- Page: Search by Drug ---
def page_search_drug():
    st.title("🔍 Search Adverse Events by Drug")
    drug_query = st.text_input("Enter drug name:", "IBUPROFEN").strip()
    if not drug_query:
        st.info("Type a drug name above to search.")
        return

    # Fetch matching records via search API
    df = load_search_events(drug_query, limit=200)
    if df.empty:
        st.warning(f"No reports found for **{drug_query.title()}**.")
        return

    # Parse receipt date and format
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["date"])
    df["date"] = df["date"].dt.date

    # Summary insights
    st.write(f"Found **{len(df):,}** adverse-event reports for **{drug_query.title()}**.")
    min_date = df["date"].min()
    max_date = df["date"].max()
    st.write(f"These reports span from **{min_date}** to **{max_date}**.")

    # Role breakdown
    role_map = {"1": "Primary suspect", "2": "Secondary suspect", "3": "Concomitant"}
    df["role_desc"] = df["role"].astype(str).map(role_map).fillna("Unknown")
    role_counts = df["role_desc"].value_counts()
    st.write("**Report Role Breakdown:**")
    st.table(role_counts)

    # Show recent records
    st.subheader("Recent Reports")
    display_df = df.sort_values("date", ascending=False)[["date", "drug", "role_desc"]]
    display_df.columns = ["Date", "Drug", "Role"]
    st.dataframe(display_df.head(20), use_container_width=True)


# --- Page: Role Distribution ---
def page_role_distribution():
    st.title("⚖️ Role Distribution for a Single Drug")
    drug_name = st.text_input("Which drug?", "IBUPROFEN").strip()
    if not drug_name:
        st.info("Type a drug name above to see role distribution.")
        return

    df = load_search_events(drug_name, limit=200)
    if df.empty:
        st.warning(f"No reports found for **{drug_name.title()}**.")
        return

    # Map and count roles
    role_map = {"1": "Primary suspect", "2": "Secondary suspect", "3": "Concomitant"}
    df["role_desc"] = df["role"].astype(str).map(role_map).fillna("Unknown")
    counts = df["role_desc"].value_counts()

    st.write(f"Role distribution for **{drug_name.title()}**:")
    st.bar_chart(counts.to_frame(name="Count"))
    st.write("**Legend:** Bar height = number of FDA adverse event reports in each role category.")


# --- Render pages ---
if page == "Top Drugs":
    page_top_drugs()
elif page == "Search by Drug":
    page_search_drug()
else:
    page_role_distribution()
