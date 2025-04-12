import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

st.set_page_config(page_title="Job Tracker Dashboard", layout="wide")

st.title("🧑‍💻 Job Tracker & Scraping Insights")


# Helper function to extract numeric values from Pay column
def extract_pay_range(pay_str):
    # Remove non-numeric characters and split by '-'
    pay_str = re.sub(r'[^\d\-\.]', '', pay_str)  # Keep only digits, hyphens, and periods
    pay_range = pay_str.split('-')

    # If there's a range, return the min and max values, else return the same value twice
    if len(pay_range) == 2:
        min_pay = float(pay_range[0].strip())
        max_pay = float(pay_range[1].strip())
        return min_pay, max_pay
    elif len(pay_range) == 1:
        return float(pay_range[0].strip()), float(pay_range[0].strip())
    else:
        return 0, 0  # If parsing fails, return 0, 0


# Tabs for navigation
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

    st.subheader("📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="✅ Successfully Applied", value=successful, delta=f"{(successful / total_applied) * 100:.1f}%")
    with col2:
        st.metric(label="❌ Failed to Apply", value=failed, delta=f"{(failed / total_applied) * 100:.1f}%")
    with col3:
        st.metric(label="📞 Job Calls Received", value=calls_received)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label="❗ Total Rejections", value=rejections)
    with col5:
        st.metric(label="🎉 Offers Received", value=offers)
    with col6:
        conversion_rate = (offers / total_applied) * 100 if total_applied else 0
        st.metric(label="🔥 Offer Rate", value=f"{conversion_rate:.1f}%")

    st.markdown("---")

    st.subheader("🧪 Progress Summary")
    st.progress(successful / total_applied)
    st.info(f"{successful} out of {total_applied} applications submitted successfully.")
    st.progress(calls_received / total_applied)
    st.info(f"{calls_received} interview calls out of {total_applied}.")

    st.markdown("---")

    st.subheader("📂 Upload Job Tracker CSV (optional)")
    uploaded_file = st.file_uploader("Upload your job tracker file", type=["csv"], key="app_tracker")
    if uploaded_file:
        df_uploaded = pd.read_csv(uploaded_file)
        st.dataframe(df_uploaded)
        st.success("CSV uploaded and displayed successfully!")

# --------- TAB 2: Job Scraping Dashboard ----------
with tab2:
    st.subheader("🔎 Scraped Job Listings Dashboard")

    uploaded_scraped = st.file_uploader("Upload scraped jobs CSV", type=["csv"], key="scraped_jobs")
    if uploaded_scraped:
        df = pd.read_csv(uploaded_scraped, parse_dates=["Scraped On"])
        df["Scraped On"] = pd.to_datetime(df["Scraped On"], errors="coerce")

        # Clean column names for consistency (optional)
        df.columns = df.columns.str.strip()

        # Clean and extract pay ranges
        df["Pay Min"], df["Pay Max"] = zip(*df["Pay"].apply(extract_pay_range))

        # Show top-level summary
        col1, col2, col3 = st.columns(3)
        col1.metric("🧾 Total Jobs", len(df))
        col2.metric("🏢 Companies", df["Company"].nunique())
        col3.metric("📅 Last Scraped", df["Scraped On"].max().strftime("%Y-%m-%d %H:%M"))

        # Sidebar filters
        st.sidebar.header("📍 Scraping Filters")
        selected_company = st.sidebar.multiselect("Company", df["Company"].unique(), default=df["Company"].unique())
        selected_status = st.sidebar.multiselect("Application Status", df["Application Status"].unique(),
                                                 default=df["Application Status"].unique())
        selected_work_mode = st.sidebar.multiselect("Work Mode", df["Work Mode"].unique(),
                                                    default=df["Work Mode"].unique())
        selected_location = st.sidebar.multiselect("Location", df["Location"].unique(), default=df["Location"].unique())
        selected_employment_type = st.sidebar.multiselect("Employment Type", df["Employment Type"].unique(),
                                                          default=df["Employment Type"].unique())

        # Adding pay range filter
        min_pay, max_pay = st.sidebar.slider("Select Pay Range",
                                             min_value=int(df["Pay Min"].min()),
                                             max_value=int(df["Pay Max"].max()),
                                             value=(int(df["Pay Min"].min()), int(df["Pay Max"].max())))

        # Adding date range filter for scraping date
        start_date, end_date = st.sidebar.date_input(
            "Select Scraping Date Range",
            [df["Scraped On"].min().date(), df["Scraped On"].max().date()]
        )

        # Apply filters
        filtered_df = df[
            df["Company"].isin(selected_company) &
            df["Application Status"].isin(selected_status) &
            df["Work Mode"].isin(selected_work_mode) &
            df["Location"].isin(selected_location) &
            df["Employment Type"].isin(selected_employment_type) &
            df["Pay Min"].between(min_pay, max_pay) &
            df["Pay Max"].between(min_pay, max_pay) &
            (df["Scraped On"].dt.date >= pd.to_datetime(start_date).date()) &  # Ensure comparison with .date()
            (df["Scraped On"].dt.date <= pd.to_datetime(end_date).date())  # Ensure comparison with .date()
            ]

        st.markdown(f"### 🎯 Filtered Jobs ({len(filtered_df)})")
        st.dataframe(filtered_df[[
            "Job Title", "Company", "Location", "Work Mode", "Application Status", "Pay", "Scraped On", "Skills"
        ]], use_container_width=True)

        # Word Cloud for Skills
        st.markdown("### ☁️ Skills Word Cloud")
        skills_text = ", ".join(filtered_df["Skills"].dropna().tolist())
        if skills_text:
            wordcloud = WordCloud(width=1000, height=400, background_color='white').generate(skills_text)
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("No skills data available for word cloud.")

        # Timeline of scraping activity
        st.markdown("### 📈 Scraping Activity Over Time")
        timeline_data = filtered_df.groupby(filtered_df["Scraped On"].dt.date).size()
        st.line_chart(timeline_data)

        # Optional: Expandable job description preview
        st.markdown("### 📃 Detailed Job Descriptions")
        for index, row in filtered_df.iterrows():
            with st.expander(f"{row['Job Title']} @ {row['Company']} ({row['Location']})"):
                st.markdown(f"**Work Mode**: {row['Work Mode']}")
                st.markdown(f"**Pay**: {row['Pay']}")
                st.markdown(f"**Application Status**: {row['Application Status']}")
                st.markdown(f"**Posted/Updated**: {row['Posted/Updated']}")
                st.markdown("**Job Description**:")
                st.write(row["Job Description"])
                st.markdown("**Skills**:")
                st.code(row["Skills"], language="text")
