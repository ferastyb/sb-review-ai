import streamlit as st
import pandas as pd
from datetime import date

from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("🔧 Service Bulletin Review Tool")

aircraft_number = st.text_input("✈️ Enter Aircraft Number (e.g. ZA100)")
delivery_date = st.date_input("📅 Delivery or Inspection Date", value=date.today())

uploaded_files = st.file_uploader("📤 Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files and aircraft_number:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(
                full_text,
                delivery_date=delivery_date.isoformat(),
                aircraft_number=aircraft_number
            )

            if not result:
                st.error("❌ GPT failed to summarize. Invalid JSON from GPT")
                continue

            summary = full_text[:1000]  # store partial text
            aircraft = ", ".join(result.get("aircraft", []))
            ata = result.get("ata")
            system = result.get("system")
            action = result.get("action")
            compliance = result.get("compliance")
            reason = result.get("reason")
            sb_id = result.get("sb_id")
            group = result.get("group")
            is_compliant = result.get("is_compliant", False)

            # Suggest AD
            ad_info = find_relevant_ad(sb_id, ata, system)
            ad_title = ad_info.get("title", "Not found")
            ad_effective_date = ad_info.get("effective_date", "N/A")

            save_to_db(
                uploaded_file.name, summary, aircraft, ata, system,
                action, compliance, reason, sb_id, group, is_compliant,
                ad_title, ad_effective_date
            )

            st.success(f"✅ {uploaded_file.name} processed and saved!")

# View DB
st.subheader("🔍 View Uploaded Bulletins")

search = st.text_input("Search by keyword")
filter_ata = st.text_input("Filter by ATA chapter (optional)")
filter_aircraft = st.text_input("Filter by Aircraft type (optional)")

df = pd.DataFrame(fetch_all_bulletins(), columns=[
    "ID", "File", "Summary", "Aircraft", "ATA", "System", "Action",
    "Compliance", "Reason", "SB ID", "Group", "Compliant", "AD Number", "AD Effective Date"
])

if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
if filter_ata:
    df = df[df["ATA"].astype(str).str.contains(filter_ata)]
if filter_aircraft:
    df = df[df["Aircraft"].str.contains(filter_aircraft, case=False)]

st.dataframe(df.drop(columns=["ID", "Reason", "SB ID"]))

if st.checkbox("Show Full Texts"):
    for _, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.markdown("**Extracted Summary**")
        st.code(row["Summary"])
