import streamlit as st
import os
import pandas as pd
from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from datetime import date
import json
import re

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("📄 Aircraft Service Bulletin Reader (with GPT-4 + AD Lookup)")

uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            delivery_date = st.date_input("Enter delivery/inspection date", value=date.today())
            aircraft_number = st.text_input("Enter Aircraft Number")

            result = summarize_with_ai(full_text, delivery_date=str(delivery_date), aircraft_number=aircraft_number)

            if "error" in result:
                st.error("❌ GPT failed to summarize. Details: " + result["error"])
                summary = full_text[:3000] + "..."
                aircraft = ata = system = action = compliance = "N/A"
            else:
                summary = json.dumps(result, indent=2)
                aircraft = ", ".join(result.get("aircraft", []))
                ata = result.get("ata", "")
                system = result.get("system", "")
                action = result.get("action", "")
                compliance = result.get("compliance", "")

            save_to_db(uploaded_file.name, summary, aircraft, ata, system, action, compliance)
            st.success(f"✅ {uploaded_file.name} processed and saved!")

            # 🔍 Suggested Relevant AD
            if aircraft or ata:
                query = f"{aircraft} ATA {ata} airworthiness directive"
                st.markdown("### 🛠️ Suggested Relevant AD")
                try:
                    import web
                    results = web.search(query)
                    top_result = results["results"][0]
                    st.markdown(f"- [{top_result['title']}]({top_result['link']})")
                except Exception as e:
                    st.warning("Could not fetch AD info.")

st.divider()
st.subheader("🔍 View Uploaded Bulletins")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    ata_filter = st.text_input("Filter by ATA Chapter")
with filter_col2:
    aircraft_filter = st.text_input("Filter by Aircraft Type")

df = pd.DataFrame(fetch_all_bulletins(), columns=["ID", "File", "Summary", "Aircraft", "ATA", "System", "Action", "Compliance"])

if ata_filter:
    df = df[df["ATA"].str.contains(ata_filter, case=False, na=False)]
if aircraft_filter:
    df = df[df["Aircraft"].str.contains(aircraft_filter, case=False, na=False)]

search_term = st.text_input("Search by keyword", "")
if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]

st.dataframe(df[["File", "Aircraft", "ATA", "System", "Action", "Compliance"]])

if st.checkbox("Show Full Texts"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Extracted Text", row["Summary"], height=200, key=f"raw_text_{i}")
