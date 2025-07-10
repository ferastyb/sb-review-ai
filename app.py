import streamlit as st
import pandas as pd
from datetime import date
from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad

st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
st.title("📄 Aircraft Service Bulletin Reader")

# Initialize database
init_db()

# Upload form
with st.form("upload_form"):
    col1, col2 = st.columns(2)
    with col1:
        aircraft_number = st.text_input("✈️ Aircraft Number")
    with col2:
        delivery_date = st.date_input("📅 Delivery or Inspection Date", value=date.today())

    uploaded_files = st.file_uploader("📎 Upload Service Bulletins (PDF)", type=["pdf"], accept_multiple_files=True)
    submitted = st.form_submit_button("Process PDFs")

if submitted and uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(text, delivery_date, aircraft_number)

            if "error" in result:
                st.error(f"❌ GPT failed to summarize: {result['error']}")
                continue

            # ✅ FIX: Call the function and unpack 5 return values
            ad_number, ad_date, ad_link, ad_applicability, amendment = find_relevant_ad(
                result['sb_id'], result['ata'], result['system']
            )

            save_to_db(
                filename=uploaded_file.name,
                summary=text,
                aircraft=", ".join(result['aircraft']),
                ata=result['ata'],
                system=result['system'],
                action=result['action'],
                compliance=result['compliance'],
                reason=result['reason'],
                sb_id=result['sb_id'],
                group_name=result['group'],
                is_compliant=result['is_compliant'],
                ad_number=ad_number,
                ad_effective_date=ad_date,
                ad_link=ad_link,
                ad_applicability=ad_applicability,
                amendment=amendment
            )

st.markdown("---")
st.subheader("🔍 View Uploaded Bulletins")

# Filters
keyword = st.text_input("Search bulletins")
ata_filter = st.selectbox("Filter by ATA", options=["All"] + [str(i) for i in range(20, 80)])
aircraft_filter = st.selectbox("Filter by Aircraft", options=["All", "787-8", "787-9", "787-10"])

all_data = fetch_all_bulletins()
df = pd.DataFrame(all_data, columns=[
    "File", "Aircraft", "ATA", "System", "Action",
    "Compliance", "Group", "Compliant",
    "AD Number", "AD Effective Date", "AD Link", "AD Applicability", "Amendment"
])

# Apply filters
if keyword:
    df = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
if ata_filter != "All":
    df = df[df["ATA"] == ata_filter]
if aircraft_filter != "All":
    df = df[df["Aircraft"].str.contains(aircraft_filter)]

# Show table (excluding raw Summary)
st.dataframe(df, use_container_width=True)

# Optional: Show full summaries
if st.checkbox("Show Full Summaries", value=False):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.markdown("**Extracted Summary**")
        st.code(row['Summary'])
