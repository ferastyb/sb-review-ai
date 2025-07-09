import streamlit as st
import os
import pandas as pd
from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
import datetime
from web_search import find_relevant_ad

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("📄 Aircraft Service Bulletin Reader (GPT-4 + Compliance Check)")

uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)
delivery_date = st.date_input("Enter aircraft delivery or inspection date")
aircraft_number = st.text_input("Enter Aircraft Number (optional)")

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(full_text, delivery_date=delivery_date, aircraft_number=aircraft_number)

        if "error" in result:
            st.error("❌ GPT failed to summarize. Details: " + result["error"])
            summary = full_text[:3000] + "..."
            aircraft = ata = system = action = compliance = reason = sb_id = group = "N/A"
            is_compliant = False
            suggested_ad = "N/A"
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

            # Suggest AD
            suggested_ad = find_relevant_ad(sb_id, reason)

            save_to_db(uploaded_file.name, summary, aircraft, ata, system, action, compliance)
            st.success(f"✅ {uploaded_file.name} processed and saved!")

        with st.expander(f"📄 {uploaded_file.name}"):
            st.markdown(f"**Aircraft:** {aircraft}")
            st.markdown(f"**ATA:** {ata}")
            st.markdown(f"**System:** {system}")
            st.markdown(f"**Action:** {action}")
            st.markdown(f"**Compliance:** {compliance}")
            st.markdown(f"**Group:** {group}")
            st.markdown(f"**Compliant Today?** {'✅ Yes' if is_compliant else '❌ No'}")
            st.markdown(f"**Suggested AD:** {suggested_ad}")
            st.text_area("Summary", summary, height=250)

st.divider()

st.subheader("🔍 View Uploaded Bulletins")

df = pd.DataFrame(fetch_all_bulletins(), columns=["ID", "File", "Summary", "Aircraft", "ATA", "System", "Action", "Compliance"])

col1, col2 = st.columns(2)
with col1:
    aircraft_filter = st.text_input("Filter by Aircraft")
with col2:
    ata_filter = st.text_input("Filter by ATA")

if aircraft_filter:
    df = df[df["Aircraft"].str.contains(aircraft_filter, case=False, na=False)]
if ata_filter:
    df = df[df["ATA"].str.contains(ata_filter, case=False, na=False)]

st.dataframe(df[["File", "Aircraft", "ATA", "System", "Action", "Compliance"]])

if st.checkbox("Show Full Texts"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Extracted Text", row["Summary"], height=200, key=f"raw_text_{i}")
