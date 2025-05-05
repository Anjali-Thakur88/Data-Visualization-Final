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
page = st.sidebar.radio("Go to:", ["Top Drugs", "Search by Drug", "Trends"])


# --- Data loaders with error handling and proper limits ---
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


@st.cache_data
def load_trend(drug_name: str, days: int = 180) -> pd.Series:
    """
    Build a time series of daily report counts for a given drug over the past `days`.
    Returns a pandas Series indexed by date.
    """
    df = load_events(limit=100)
    if df.empty or "drug" not in df.columns:
        return pd.Series(dtype=int)

    # Parse dates, drop parse errors
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["date"])

    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    mask = (
        (df["drug"].str.lower() == drug_name.lower()) &
        (df["date"] >= cutoff)
    )
    daily_counts = df[mask].groupby(df["date"].dt.date).size()
    return daily_counts.sort_index()


# --- Page: Top Drugs ---
def page_top_drugs():
    st.title("🏆 Top Reported Drugs (last 100 events)")
    df = load_events(limit=100)

    if df.empty or "drug" not in df.columns:
        st.warning("No data available. Try again in a moment.")
        return

    top10 = df["drug"].value_counts().nlargest(10)
    st.bar_chart(top10)


# --- Page: Search by Drug ---
def page_search_drug():
    st.title("🔍 Search Adverse Events by Drug")
    drug_query = st.text_input("Enter drug name:", "IBUPROFEN").strip()

    if not drug_query:
        st.info("Type a drug name above to search.")
        return

    df = load_events(limit=100)

    if df.empty or "drug" not in df.columns:
        st.warning("No data available (API limit or network issue).")
        return

    mask = df["drug"].str.contains(drug_query, case=False, na=False)
    subset = df[mask]

    st.write(f"Found **{len(subset):,}** reports for **{drug_query.title()}**.")
    st.dataframe(subset.head(20), use_container_width=True)


# --- Page: Trends ---
def page_trends():
    st.title("📈 Report Trends for a Single Drug")
    drug_name = st.text_input("Which drug?", "PARACETAMOL").strip()

    if not drug_name:
        st.info("Type a drug name above to see its trend.")
        return

    series = load_trend(drug_name, days=180)
    if series.empty:
        st.warning("No recent data found for that drug.")
    else:
        st.line_chart(series)


# --- Render pages ---
if page == "Top Drugs":
    page_top_drugs()
elif page == "Search by Drug":
    page_search_drug()
elif page == "Trends":
    page_trends()
    