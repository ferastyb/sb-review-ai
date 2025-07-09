import streamlit as st
import pandas as pd
from datetime import date

from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad

# Initialize app
st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("📄 Aircraft Service Bulletin Reader")

# User inputs for compliance checks
col1, col2 = st.columns(2)
with col1:
    aircraft_number = st.text_input("✈️ Aircraft Number", "")
with col2:
    delivery_date = st.date_input("📆 Delivery or Inspection Date", value=date.today())

uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files and aircraft_number and delivery_date:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(
                full_text,
                delivery_date=delivery_date.isoformat(),
                aircraft_number=aircraft_number
            )

            if "error" in result:
                st.error("❌ GPT failed to summarize: " + result["error"])
                continue

            # Extract structured values
            summary = str(result)
            aircraft = ", ".join(result.get("aircraft", []))
            ata = result.get("ata", "")
            system = result.get("system", "")
            action = result.get("action", "")
            compliance = result.get("compliance", "")
            reason = result.get("reason", "")
            sb_id = result.get("sb_id", "")
            group = result.get("group", "")
            is_compliant = result.get("is_compliant", False)

            # Find relevant AD
            ad_info = find_relevant_ad(sb_id, ata, system)
            ad_number = ad_info.get("ad_number", "")
            ad_effective_date = ad_info.get("effective_date", "")

            # Save to DB
            save_to_db(
                uploaded_file.name, summary, aircraft, ata, system,
                action, compliance, reason, sb_id, group, is_compliant,
                ad_number, ad_effective_date
            )

            st.success(f"✅ {uploaded_file.name} processed and saved!")

st.divider()
st.subheader("🔍 View Uploaded Bulletins")

# Load from DB
all_data = fetch_all_bulletins()
df = pd.DataFrame(all_data, columns=[
    "ID", "File", "Summary", "Aircraft", "ATA", "System", "Action",
    "Compliance", "Reason", "SB ID", "Group", "Compliant",
    "AD Number", "AD Effective Date"
])

# Search bar
search_term = st.text_input("Search bulletins", "")
if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]

# Filters
col3, col4 = st.columns(2)
with col3:
    selected_ata = st.selectbox("Filter by ATA", options=["All"] + sorted(df["ATA"].dropna().unique().tolist()))
    if selected_ata != "All":
        df = df[df["ATA"] == selected_ata]

with col4:
    selected_aircraft = st.selectbox("Filter by Aircraft", options=["All"] + sorted(df["Aircraft"].dropna().unique().tolist()))
    if selected_aircraft != "All":
        df = df[df["Aircraft"].str.contains(selected_aircraft)]

# Show table
st.dataframe(df[[
    "File", "Aircraft", "ATA", "System", "Action", "Compliance",
    "Group", "Compliant", "AD Number", "AD Effective Date"
]])

# Optional full summaries
if st.checkbox("Show Full Summaries"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Extracted Summary", row["Summary"], height=200, key=f"summary_{i}")
