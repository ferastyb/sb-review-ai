import streamlit as st
import os
import pandas as pd
from sb_parser import extract_text_from_pdf
from sb_database import init_db, save_to_db, fetch_all_bulletins

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("📄 Aircraft Service Bulletin Reader (Offline Mode)")

uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)

            # Use dummy metadata (you can improve this later)
            aircraft = "Unknown"
            ata = "Unknown"
            system = "Unknown"
            action = "Read-only"
            compliance = "Not extracted"
            summary = full_text[:3000] + "..." if len(full_text) > 3000 else full_text

            save_to_db(uploaded_file.name, summary, aircraft, ata, system, action, compliance)
            st.success(f"{uploaded_file.name} text extracted and saved!")

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
