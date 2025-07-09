import streamlit as st
import os
import pandas as pd
from datetime import date

from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("📄 Aircraft Service Bulletin Reader")

# Aircraft delivery info
col1, col2 = st.columns(2)
with col1:
    aircraft_number = st.text_input("✈️ Enter Aircraft Number (e.g. ZA100)")
with col2:
    delivery_date = st.date_input("📅 Delivery or Inspection Date", value=date.today())

# File upload
uploaded_files = st.file_uploader(
    "Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True
)

if uploaded_files:
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

            # Extract fields from result
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

            # Suggest relevant AD
            ad_info = find_relevant_ad(sb_id, ata, system)

            # Save all to DB
            save_to_db(
                uploaded_file.name,
                summary,
                aircraft,
                ata,
                system,
                action,
                compliance,
                reason,
                sb_id,
                group,
                is_compliant,
                ad_info.get("ad_number", "N/A"),
                ad_info.get("ad_effective_date", "N/A")
            )

            st.success(f"✅ {uploaded_file.name} processed and saved!")

# View stored bulletins
st.divider()
st.subheader("🔍 View Uploaded Bulletins")

df = pd.DataFrame(fetch_all_bulletins(), columns=[
    "ID", "File", "Summary", "Aircraft", "ATA", "System", "Action", "Compliance",
    "Reason", "SB ID", "Group", "Compliant", "AD Number", "AD Effective Date"
])

# Filter UI
search_term = st.text_input("Search by keyword", "")
filter_ata = st.text_input("Filter by ATA chapter (optional)", "")
filter_aircraft = st.text_input("Filter by Aircraft type (optional)", "")

if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
if filter_ata:
    df = df[df["ATA"].astype(str).str.contains(filter_ata.strip(), case=False)]
if filter_aircraft:
    df = df[df["Aircraft"].astype(str).str.contains(filter_aircraft.strip(), case=False)]

# Table display
st.dataframe(df[[
    "File", "Aircraft", "ATA", "System", "Action", "Compliance",
    "Group", "Compliant", "AD Number", "AD Effective Date"
]])

# Optional full text
if st.checkbox("Show Full Texts"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Extracted Summary", row["Summary"], height=200, key=f"raw_text_{i}")
