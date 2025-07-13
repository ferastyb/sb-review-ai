import streamlit as st
import os
import sqlite3
import tempfile
from sb_parser import parse_sb_pdf
from sb_database import save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad
import pandas as pd

st.set_page_config(page_title="SB Reviewer", layout="wide")
st.title("📄 Service Bulletin Reviewer AI")

st.markdown("---")

uploaded_files = st.file_uploader("Upload Service Bulletin PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Process PDFs"):
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            try:
                result, text = parse_sb_pdf(tmp_file_path)
                if result is None:
                    st.error(f"❌ GPT failed to summarize: {text}")
                    continue

                ad_number, ad_date, ad_link, ad_applicability, ad_amendment = find_relevant_ad(
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
                    group=result['group'],
                    is_compliant=result['is_compliant'],
                    ad_number=ad_number,
                    ad_effective_date=ad_date,
                    ad_link=ad_link,
                    ad_applicability=ad_applicability,
                    ad_amendment=ad_amendment,
                )

                st.success(f"✅ Processed: {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {e}")
            finally:
                os.remove(tmp_file_path)

st.markdown("---")
st.header("🔍 View Uploaded Bulletins")

search_text = st.text_input("Search bulletins")
ata_filter = st.selectbox("Filter by ATA", options=["All"] + [str(i) for i in range(21, 100)])
aircraft_filter = st.selectbox("Filter by Aircraft", options=["All", "787-8", "787-9", "787-10"])

all_data = fetch_all_bulletins()
df = pd.DataFrame(all_data, columns=[
    "SB No.", "Aircraft", "ATA", "System", "Action", "Compliance", "Group", "Compliant",
    "AD Number", "AD Effective Date", "AD Link", "AD Applicability", "AD Amendment"
])

if search_text:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_text, case=False).any(), axis=1)]

if ata_filter != "All":
    df = df[df["ATA"] == int(ata_filter)]

if aircraft_filter != "All":
    df = df[df["Aircraft"].str.contains(aircraft_filter)]

st.dataframe(df, use_container_width=True)
