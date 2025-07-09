import streamlit as st
import os
import pandas as pd
import datetime
from sb_parser import extract_text_from_pdf, summarize_with_ai
from sb_database import init_db, save_to_db, fetch_all_bulletins
from web_search import find_relevant_ad

# App setup
st.set_page_config(page_title="Service Bulletin Previewer", layout="wide")
init_db()
st.title("📄 Aircraft Service Bulletin Reviewer")

uploaded_files = st.file_uploader("Upload Service Bulletins (PDF)", type="pdf", accept_multiple_files=True)

delivery_date = st.date_input("Enter Aircraft Delivery or Inspection Date", datetime.date.today())
aircraft_number = st.text_input("Enter Aircraft Number (if applicable)")

# File processing
if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            full_text = extract_text_from_pdf(uploaded_file)
            result = summarize_with_ai(
                full_text,
                delivery_date=delivery_date.isoformat(),
                aircraft_number=aircraft_number
            )

            if "error" in result:
                st.error("❌ GPT failed to summarize. Details: " + result["error"])
                summary = full_text[:3000] + "..."
                aircraft = ata = system = action = compliance = reason = sb_id = group = "N/A"
                is_compliant = False
                suggested_ad = {"title": "No relevant AD found", "url": ""}
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

                suggested_ad = find_relevant_ad(sb_id=sb_id, ata=ata, system=system)

            save_to_db(
                uploaded_file.name, summary, aircraft, ata, system,
                action, compliance, reason, sb_id, group, is_compliant,
                suggested_ad["title"]
            )

            st.success(f"✅ {uploaded_file.name} processed and saved!")
            if suggested_ad["url"]:
                st.markdown(f"📌 **Suggested AD**: [{suggested_ad['title']}]({suggested_ad['url']})")
            else:
                st.info("No relevant AD found.")

st.divider()
st.subheader("🔍 View Uploaded Bulletins")

# Load and display data
df = pd.DataFrame(fetch_all_bulletins(), columns=[
    "ID", "File", "Summary", "Aircraft", "ATA", "System",
    "Action", "Compliance", "Reason", "SB ID", "Group", "Compliant", "AD"
])

# UI Filters
col1, col2 = st.columns(2)
with col1:
    selected_ata = st.selectbox("Filter by ATA Chapter", ["All"] + sorted(df["ATA"].dropna().unique().tolist()))
with col2:
    selected_aircraft = st.selectbox("Filter by Aircraft", ["All"] + sorted(df["Aircraft"].dropna().unique().tolist()))

if selected_ata != "All":
    df = df[df["ATA"] == selected_ata]
if selected_aircraft != "All":
    df = df[df["Aircraft"].str.contains(selected_aircraft, case=False)]

search_term = st.text_input("Search by keyword", "")
if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]

st.dataframe(df[[
    "File", "Aircraft", "ATA", "System", "Action", "Compliance", "Compliant", "AD"
]])

# Detailed view
if st.checkbox("Show Full Summaries"):
    for i, row in df.iterrows():
        st.markdown(f"### 📄 {row['File']}")
        st.text_area("Extracted Summary", row["Summary"], height=200, key=f"summary_{i}")
