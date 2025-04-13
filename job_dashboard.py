import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

st.set_page_config(page_title="Job Tracker Dashboard", layout="wide")
st.title("🧑‍💻 Job Tracker & Scraping Insights")

# Helper function to extract numeric values from Pay column
def extract_pay_range(pay_str):
    if pd.isna(pay_str) or not isinstance(pay_str, str):
        return 0, 0
    pay_str = re.sub(r'[^\d\-\.]', '', pay_str)
    pay_range = pay_str.split('-')
    try:
        if len(pay_range) == 2:
            return float(pay_range[0]), float(pay_range[1])
        elif len(pay_range) == 1 and pay_range[0]:
            return float(pay_range[0]), float(pay_range[0])
    except:
        return 0, 0
    return 0, 0

# Tabs
tab1, tab2 = st.tabs(["📊 Application Tracker", "🔍 Scraped Job Listings"])

# --------- TAB 1: Job Tracker ----------
with tab1:
    st.sidebar.header("📌 Application Summary")
    total_applied = st.sidebar.number_input("Total Jobs Applied", value=50, step=1)
    successful = st.sidebar.number_input("Successfully Applied", value=45, step=1)
    failed = st.sidebar.number_input("Failed to Apply", value=5, step=1)
    calls_received = st.sidebar.number_input("Job Calls Received", value=10, step=1)
    rejections = st.sidebar.number_input("Total Rejections", value=8, step=1)
    offers = st.sidebar.number_input("Offers Received", value=2, step=1)
    interviews_scheduled = st.sidebar.number_input("Interviews Scheduled", value=5, step=1)
    follow_ups_sent = st.sidebar.number_input("Follow-ups Sent", value=7, step=1)

    st.subheader("📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Successfully Applied", successful, f"{(successful / total_applied) * 100:.1f}%")
    with col2:
        st.metric("❌ Failed to Apply", failed, f"{(failed / total_applied) * 100:.1f}%")
    with col3:
        st.metric("📞 Job Calls Received", calls_received)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("🗓️ Interviews Scheduled", interviews_scheduled)
    with col5:
        st.metric("📬 Follow-ups Sent", follow_ups_sent)
    with col6:
        st.metric("🔥 Offer Rate", f"{(offers / total_applied) * 100:.1f}%" if total_applied else "0.0%")

    col7, col8 = st.columns(2)
    with col7:
        st.metric("❗ Total Rejections", rejections)
    with col8:
        st.metric("🎉 Offers Received", offers)

    st.markdown("---")

    st.subheader("🚀 Visual Progress Overview")
    st.progress(successful / total_applied, text=f"{successful} successful applications")
    st.progress(calls_received / total_applied, text=f"{calls_received} interview calls")
    st.progress(interviews_scheduled / total_applied, text=f"{interviews_scheduled} interviews scheduled")

    st.markdown("---")

    st.subheader("📂 Upload Your Job Tracker CSV")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="app_tracker")
    if uploaded_file:
        df_uploaded = pd.read_csv(uploaded_file)
        df_uploaded.columns = df_uploaded.columns.str.strip()

        st.markdown("### 🧾 Tracker Data Preview")
        st.dataframe(df_uploaded, use_container_width=True)
        st.success("CSV uploaded and displayed successfully!")

        if 'Application Status' in df_uploaded.columns:
            st.markdown("### 📊 Application Status Breakdown")
            status_counts = df_uploaded['Application Status'].value_counts()
            fig, ax = plt.subplots()
            ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
            st.pyplot(fig)

        if 'Applied Date' in df_uploaded.columns:
            df_uploaded['Applied Date'] = pd.to_datetime(df_uploaded['Applied Date'], errors='coerce')
            df_uploaded = df_uploaded.dropna(subset=['Applied Date'])
            timeline_data = df_uploaded.groupby(df_uploaded['Applied Date'].dt.date).size()
            st.markdown("### 📅 Application Timeline")
            st.line_chart(timeline_data)

        if 'Skills' in df_uploaded.columns:
            st.markdown("### ☁️ Common Skills in Applications")
            skills_text = ", ".join(df_uploaded['Skills'].dropna().astype(str))
            if skills_text:
                wordcloud = WordCloud(width=1000, height=400, background_color='white').generate(skills_text)
                fig, ax = plt.subplots(figsize=(12, 4))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.info("No skills data available for word cloud.")

        if 'Job Title' in df_uploaded.columns:
            st.markdown("### 📜 Detailed Applications")
            for index, row in df_uploaded.iterrows():
                with st.expander(f"{row['Job Title']} @ {row['Company']} ({row['Location']})"):
                    st.markdown(f"**Work Mode**: {row['Work Mode']}")
                    st.markdown(f"**Pay**: {row['Pay']}")
                    st.markdown(f"**Application Status**: {row['Application Status']}")
                    st.markdown(f"**Location**: {row.get('Location', 'N/A')}")
                    st.markdown(f"**Followed Up**: {row.get('Follow Up', 'N/A')}")
                    st.markdown(f"**Posted/Updated**: {row.get('Posted/Updated', 'N/A')}")
                    st.markdown("**Job Description**:")
                    st.write(row.get("Job Description", "Not Available"))
                    st.markdown("**Skills**:")
                    st.code(row.get("Skills", ""), language="text")


# --------- TAB 2: Scraped Job Listings Dashboard ----------
with tab2:
    st.subheader("🔎 Scraped Job Listings Dashboard")
    uploaded_scraped = st.file_uploader("Upload scraped jobs CSV", type=["csv"], key="scraped_jobs")
    if uploaded_scraped:
        df = pd.read_csv(uploaded_scraped, parse_dates=["Scraped On"])
        df.columns = df.columns.str.strip()
        df["Scraped On"] = pd.to_datetime(df["Scraped On"], errors="coerce")
        df["Pay Min"], df["Pay Max"] = zip(*df["Pay"].apply(extract_pay_range))

        col1, col2, col3 = st.columns(3)
        col1.metric("📟 Total Jobs", len(df))
        col2.metric("🏢 Companies", df["Company"].nunique())
        col3.metric("📅 Last Scraped", df["Scraped On"].max().strftime("%Y-%m-%d"))

        st.sidebar.header("📍 Scraping Filters")
        selected_company = st.sidebar.multiselect("Company", df["Company"].dropna().unique(), default=df["Company"].dropna().unique())
        selected_status = st.sidebar.multiselect("Application Status", df["Application Status"].dropna().unique(), default=df["Application Status"].dropna().unique())
        selected_work_mode = st.sidebar.multiselect("Work Mode", df["Work Mode"].dropna().unique(), default=df["Work Mode"].dropna().unique())
        selected_location = st.sidebar.multiselect("Location", df["Location"].dropna().unique(), default=df["Location"].dropna().unique())
        selected_employment_type = st.sidebar.multiselect("Employment Type", df["Employment Type"].dropna().unique(), default=df["Employment Type"].dropna().unique())
        min_pay, max_pay = st.sidebar.slider("Select Pay Range", int(df["Pay Min"].min()), int(df["Pay Max"].max()), (int(df["Pay Min"].min()), int(df["Pay Max"].max())))

        start_date, end_date = st.sidebar.date_input("Select Scraping Date Range", [df["Scraped On"].min().date(), df["Scraped On"].max().date()])

        filtered_df = df[
            df["Company"].isin(selected_company) &
            df["Application Status"].isin(selected_status) &
            df["Work Mode"].isin(selected_work_mode) &
            df["Location"].isin(selected_location) &
            df["Employment Type"].isin(selected_employment_type) &
            df["Pay Min"].between(min_pay, max_pay) &
            df["Pay Max"].between(min_pay, max_pay) &
            (df["Scraped On"].dt.date >= start_date) &
            (df["Scraped On"].dt.date <= end_date)
        ]

        st.markdown(f"### 🌟 Filtered Jobs ({len(filtered_df)})")
        st.dataframe(filtered_df[["Job Title", "Company", "Location", "Work Mode", "Application Status", "Pay", "Scraped On", "Skills"]], use_container_width=True)

        st.markdown("### ☁️ Skills Word Cloud")
        skills_text = ", ".join(filtered_df["Skills"].dropna().astype(str))
        if skills_text:
            wordcloud = WordCloud(width=1000, height=400, background_color='white').generate(skills_text)
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("No skills data available for word cloud.")

        st.markdown("### 📈 Scraping Activity Over Time")
        timeline_data = filtered_df.groupby(filtered_df["Scraped On"].dt.date).size()
        st.line_chart(timeline_data)

        st.markdown("### 📜 Detailed Job Descriptions")
        for index, row in filtered_df.iterrows():
            with st.expander(f"{row['Job Title']} @ {row['Company']} ({row['Location']})"):
                st.markdown(f"**Work Mode**: {row['Work Mode']}")
                st.markdown(f"**Pay**: {row['Pay']}")
                st.markdown(f"**Application Status**: {row['Application Status']}")
                st.markdown(f"**Posted/Updated**: {row.get('Posted/Updated', 'N/A')}")
                st.markdown("**Job Description**:")
                st.write(row.get("Job Description", "Not Available"))
                st.markdown("**Skills**:")
                st.code(row.get("Skills", ""), language="text")
