import streamlit as st
import os
import pandas as pd
from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
import re

st.set_page_config(page_title="Service Bulletin Reviewer", layout="wide")

init_db()

st.title("🛠️ Aircraft Service Bulletin AI Assistant")

uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(full_text)

# Populate fields
aircraft = ", ".join(result.get("aircraft", []))
ata = result.get("ata", "")
system = result.get("system", "")
action = result.get("action", "")
compliance = result.get("compliance", "")
reason = result.get("reason", "")
sb_id = result.get("sb_id", "")
summary = str(result)


            # Try to extract basic fields from AI summary
            def extract_field(pattern):
                match = re.search(f"{pattern}:(.*)", summary, re.IGNORECASE)
                return match.group(1).strip() if match else ""

            aircraft = extract_field("aircraft model")
            ata = extract_field("ATA chapter")
            system = extract_field("affected system|affected part")
            action = extract_field("type of action")
            compliance = extract_field("compliance recommendation")

            save_to_db(uploaded_file.name, summary, aircraft, ata, system, action, compliance)

            st.success(f"{uploaded_file.name} processed and saved!")

st.divider()

st.subheader("🔍 Search & View Summaries")

df = pd.DataFrame(fetch_all_bulletins(), columns=["ID", "File", "Summary", "Aircraft", "ATA", "System", "Action", "Compliance"])

search_term = st.text_input("Search (Aircraft, System, ATA, Action)", "")

if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]

st.dataframe(df[["File", "Aircraft", "ATA", "System", "Action", "Compliance"]])

if st.checkbox("Show Full Summaries"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Summary", row["Summary"], height=200, key=f"summary_{i}")

