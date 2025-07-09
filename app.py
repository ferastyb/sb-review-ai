# app.py
import streamlit as st
import pandas as pd
from datetime import date

from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()

st.title("🛩️ Aircraft Service Bulletin Reader (with Compliance Checker)")

# Aircraft and delivery info
with st.sidebar:
    st.subheader("✈️ Aircraft Info")
    aircraft_number = st.text_input("Enter your aircraft number (e.g. ZA839)")
    delivery_date = st.date_input("📅 Delivery or Inspection Date", value=date.today())

# File upload
uploaded_files = st.file_uploader("📤 Upload Service Bulletins (PDF)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(full_text, delivery_date=delivery_date.isoformat(), aircraft_number=aircraft_number)

            if "error" in result:
                st.error(f"❌ GPT failed to summarize: {result['error']}")
                continue

            # Extract summary fields
            summary = full_text[:300] + "..."
            aircraft = ", ".join(result.get("aircraft", []))
            ata = result.get("ata", "")
            system = result.get("system", "")
            action = result.get("action", "")
            compliance = result.get("compliance", "")
            reason = result.get("reason", "")
            sb_id = result.get("sb_id", "")
            group = result.get("group", "")
            is_compliant = result.get("is_compliant")

            # Search for AD
            ad_info = find_relevant_ad(sb_id, ata, system)
            ad_title = ad_info.get("title", "Not found")
            ad_effective_date = ad_info.get("effective_date", "N/A")

            save_to_db(
                uploaded_file.name, summary, aircraft, ata, system,
                action, compliance, reason, sb_id, group, is_compliant,
                ad_title, ad_effective_date
            )
            st.success(f"✅ {uploaded_file.name} processed and saved!")

# Show table
st.subheader("🔍 View Uploaded Bulletins")
all_data = fetch_all_bulletins()
df = pd.DataFrame(all_data, columns=[
    "File", "Summary", "Aircraft", "ATA", "System", "Action", "Compliance",
    "Group", "Compliant", "AD Number", "AD Effective Date"
])

search = st.text_input("Search by keyword")
ata_filter = st.text_input("Filter by ATA chapter (optional)")
aircraft_filter = st.text_input("Filter by Aircraft type (optional)")

if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
if ata_filter:
    df = df[df["ATA"].str.contains(ata_filter, case=False)]
if aircraft_filter:
    df = df[df["Aircraft"].str.contains(aircraft_filter, case=False)]

st.dataframe(df.drop(columns=["Summary"]))

if st.checkbox("🔎 Show Full Texts"):
    for _, row in df.iterrows():
        st.subheader(f"📄 {row['File']}")
        st.markdown("**Extracted Summary**")
        st.code(row['Summary'])
