import streamlit as st
import os
import pandas as pd
from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from datetime import datetime

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("📄 Aircraft Service Bulletin Reader (with Compliance Checker)")

uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    aircraft_number = st.text_input("Enter your aircraft variable number (e.g. ZA839)")
    delivery_date = st.date_input("Enter your aircraft's inspection/delivery date")

    if aircraft_number and delivery_date:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                full_text = extract_text_from_pdf(uploaded_file)
                result = summarize_with_ai(full_text, str(delivery_date), aircraft_number)

                if "error" in result:
                    st.error("❌ GPT failed to summarize. Details: " + result["error"])
                    summary = full_text[:30000] + "..."
                    aircraft = ata = system = action = compliance = compliance_status = group = "N/A"
                else:
                    summary = result.get("raw_summary", str(result))
                    aircraft = ", ".join(result.get("aircraft", []))
                    ata = result.get("ata", "")
                    system = result.get("system", "")
                    action = result.get("action", "")
                    compliance = result.get("compliance", "")
                    compliance_status = result.get("compliance_status", "Unknown")
                    group = result.get("group", "Unknown")

                save_to_db(uploaded_file.name, summary, aircraft, ata, system, action, compliance)
                st.success(f"{uploaded_file.name} processed and saved!")
                st.info(f"✈️ Aircraft Group: {group}\n📅 Compliance: {compliance}\n🕒 Status: {compliance_status}")

st.divider()
st.subheader("🔍 View Uploaded Bulletins")

df = pd.DataFrame(fetch_all_bulletins(), columns=["ID", "File", "Summary", "Aircraft", "ATA", "System", "Action", "Compliance"])

search_term = st.text_input("Search by keyword", "")

if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]

st.dataframe(df[["File", "Aircraft", "ATA", "System", "Action", "Compliance"]])

if st.checkbox("Show Full Texts"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Extracted Text", row["Summary"], height=200, key=f"raw_text_{i}")
