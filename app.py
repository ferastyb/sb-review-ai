import streamlit as st
import os
import sqlite3
import pandas as pd
from sb_parser import parse_service_bulletin
from sb_database import create_database, save_to_db, fetch_all_bulletins
from web_search import search_for_relevant_ad

# Ensure database exists
create_database()

st.set_page_config(layout="wide")
st.title("🔧 Service Bulletin Review App")

uploaded_files = st.file_uploader("Upload Service Bulletin PDFs", type=["pdf"], accept_multiple_files=True)
if st.button("Process PDFs") and uploaded_files:
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        with open(f"temp_{uploaded_file.name}", "wb") as f:
            f.write(bytes_data)

        try:
            result, text = parse_service_bulletin(f"temp_{uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ GPT failed to summarize: {str(e)}")
            os.remove(f"temp_{uploaded_file.name}")
            continue

        # Always run AD search for each SB
        ad_number, ad_date, ad_link, ad_applicability, amendment = search_for_relevant_ad(
            result["sb_id"], result["ata"], result["system"]
        )

        save_to_db(
            filename=uploaded_file.name,
            summary=text,
            aircraft=", ".join(result["aircraft"]),
            ata=result["ata"],
            system=result["system"],
            action=result["action"],
            compliance=result["compliance"],
            reason=result["reason"],
            sb_id=result["sb_id"],
            group=result["group"],
            is_compliant=result["is_compliant"],
            ad_number=ad_number,
            ad_effective_date=ad_date,
            ad_link=ad_link,
            ad_applicability=ad_applicability,
            ad_amendment=amendment
        )

        os.remove(f"temp_{uploaded_file.name}")
    st.success("✅ Processing complete!")

# UI: View and filter results
st.markdown("## 🔍 View Uploaded Bulletins")

all_data = fetch_all_bulletins()
df = pd.DataFrame(all_data, columns=[
    "SB No.", "Aircraft", "ATA", "System", "Action", "Compliance", "Group",
    "Compliant", "AD Number", "AD Effective Date", "AD Link", "AD Applicability", "AD Amendment"
])

# Filters
ata_filter = st.selectbox("Filter by ATA", options=["All"] + sorted(df["ATA"].unique().tolist()))
ac_filter = st.selectbox("Filter by Aircraft", options=["All"] + sorted(set(sum([x.split(", ") for x in df["Aircraft"]], []))))

if ata_filter != "All":
    df = df[df["ATA"] == ata_filter]
if ac_filter != "All":
    df = df[df["Aircraft"].str.contains(ac_filter)]

st.dataframe(df, use_container_width=True)
