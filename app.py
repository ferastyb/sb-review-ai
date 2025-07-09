import streamlit as st
import os
import pandas as pd
import datetime
from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("📄 Aircraft Service Bulletin Reader")

today = datetime.date.today()
delivery_date = st.date_input("Enter aircraft delivery date:", today)
aircraft_number = st.text_input("Enter aircraft number (for group logic):")

uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(full_text, delivery_date=str(delivery_date), aircraft_number=aircraft_number)

            if "error" in result:
                st.error("❌ GPT failed to summarize. Details: " + result["error"])
                summary = full_text[:3000] + "..."
                aircraft = ata = system = action = compliance = reason = sb_id = group = "N/A"
                is_compliant = False
                ad_suggestion = {"title": "N/A"}
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

                suggested_ad = find_relevant_ad(sb_id, ata=ata, system=system)

                save_to_db(
                    uploaded_file.name, summary, aircraft, ata, system,
                    action, compliance, reason, sb_id, group, is_compliant,
                    suggested_ad["title"]
                )

                st.success(f"✅ {uploaded_file.name} processed and saved!")

st.divider()
st.subheader("🔍 View Uploaded Bulletins")

df = pd.DataFrame(fetch_all_bulletins(), columns=[
    "ID", "File", "Summary", "Aircraft", "ATA", "System",
    "Action", "Compliance", "Reason", "SB ID", "Group",
    "Compliant?", "Suggested AD"
])

col1, col2 = st.columns(2)
with col1:
    search_term = st.text_input("Search by keyword", "")
with col2:
    ata_filter = st.text_input("Filter by ATA (optional)", "")

if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
if ata_filter:
    df = df[df["ATA"].astype(str).str.contains(ata_filter, case=False)]

st.dataframe(df[[
    "File", "Aircraft", "ATA", "System", "Action",
    "Compliance", "Compliant?", "Suggested AD"
]])

if st.checkbox("Show Full Summaries"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Extracted Summary", row["Summary"], height=200, key=f"raw_text_{i}")
