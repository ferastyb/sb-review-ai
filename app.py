import streamlit as st
import os
import pandas as pd
from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad
import datetime

# App config
st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("📄 Aircraft Service Bulletin Reader (GPT-4 Enhanced)")

# File upload
uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

# Optional aircraft number and delivery date input
with st.expander("✈️ Provide Aircraft Details (optional)"):
    col1, col2 = st.columns(2)
    with col1:
        aircraft_number = st.text_input("Aircraft Number (e.g. ZB123)", "")
    with col2:
        delivery_date = st.date_input("Delivery/Inspection Date", datetime.date.today())

# Process files
if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(
                full_text,
                delivery_date=str(delivery_date),
                aircraft_number=aircraft_number
            )

            if "error" in result:
                st.error("❌ GPT failed to summarize. Details: " + result["error"])
                summary = full_text[:3000] + "..."
                aircraft = ata = system = action = compliance = reason = sb_id = group = ad_title = ad_url = "N/A"
                is_compliant = False
            else:
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

                # Get suggested AD
                suggested_ad = find_relevant_ad(sb_id=sb_id, ata=ata, system=system)
                ad_title = suggested_ad.get("title", "None found")
                ad_url = suggested_ad.get("url", "")

                save_to_db(
                    uploaded_file.name, summary, aircraft, ata, system, action,
                    compliance, reason, sb_id, group, is_compliant, ad_title
                )

                st.success(f"✅ {uploaded_file.name} processed and saved!")
                st.markdown(f"**Suggested AD:** [{ad_title}]({ad_url})" if ad_url else f"**Suggested AD:** {ad_title}")

# Display DB
st.divider()
st.subheader("🔍 View Uploaded Bulletins")

# Load from DB
df = pd.DataFrame(fetch_all_bulletins(), columns=[
    "ID", "File", "Summary", "Aircraft", "ATA", "System", "Action",
    "Compliance", "Reason", "SB ID", "Group", "Is Compliant", "Suggested AD"
])

# Filters
col1, col2 = st.columns(2)
with col1:
    search_term = st.text_input("🔎 Search by keyword", "")
with col2:
    ata_filter = st.text_input("📘 Filter by ATA chapter", "")

if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]

if ata_filter:
    df = df[df["ATA"].str.contains(ata_filter, case=False)]

# Show results
st.dataframe(df[[
    "File", "Aircraft", "ATA", "System", "Action",
    "Compliance", "Group", "Is Compliant", "Suggested AD"
]])

# Optional raw text
if st.checkbox("📜 Show Full Summaries"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Extracted Text", row["Summary"], height=200, key=f"raw_text_{i}")
