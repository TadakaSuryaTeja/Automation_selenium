import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import re

# Set up page config and title
st.set_page_config(page_title="Job Tracker Dashboard", layout="wide")
st.title("🧑‍💻 Job Tracker & Scraping Insights")

# Helper Functions

def extract_pay_range(pay_str):
    """Extracts min and max pay from a string."""
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

def load_data(uploaded_file):
    """Loads the uploaded CSV file and processes columns."""
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    if 'Pay' in df.columns:
        df['Pay Min'], df['Pay Max'] = zip(*df['Pay'].apply(extract_pay_range))
    if 'Applied Date' in df.columns:
        df['Applied Date'] = pd.to_datetime(df['Applied Date'], errors='coerce').dropna()
    if 'Scraped On' in df.columns:
        df["Scraped On"] = pd.to_datetime(df["Scraped On"], errors='coerce')
    return df

def generate_wordcloud(text_data):
    """Generates a word cloud from the given text data."""
    wordcloud = WordCloud(width=1000, height=400, background_color='white').generate(text_data)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    return fig

def plot_job_status_pie_chart(status_counts):
    """Plots a pie chart for job application status."""
    fig, ax = plt.subplots()
    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    return fig

def plot_pay_distribution(df):
    """Plots the pay distribution (Pay Min and Pay Max)."""
    fig, ax = plt.subplots()
    sns.histplot(df['Pay Min'].dropna(), bins=20, alpha=0.7, label='Pay Min', ax=ax)
    sns.histplot(df['Pay Max'].dropna(), bins=20, alpha=0.7, label='Pay Max', ax=ax, color='orange')
    ax.set_xlabel("Pay (in USD)")
    ax.set_ylabel("Number of Jobs")
    ax.legend()
    return fig


def plot_pay_vs_location(df):
    """Plots Pay vs Location as a scatter plot."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x='Location', y='Pay Min', hue='Location', size='Pay Max', sizes=(20, 200), alpha=0.7)
    ax.set_title("Pay vs. Location")
    ax.set_xlabel("Location")
    ax.set_ylabel("Pay (in USD)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def apply_filters(df, filters):
    """Applies filters to the dataframe."""
    filtered_df = df.copy()
    for col, selected in filters.items():
        if col in filtered_df.columns:
            if isinstance(selected, tuple):
                if col == 'Pay Min':
                    filtered_df = filtered_df[filtered_df[col] >= selected[0]]
                elif col == 'Pay Max':
                    filtered_df = filtered_df[filtered_df[col] <= selected[1]]
                elif col == 'Scraped On':
                    filtered_df = filtered_df[(filtered_df[col].dt.date >= selected[0]) & (filtered_df[col].dt.date <= selected[1])]
            else:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]
    return filtered_df

# Sidebar for application summary (static input values)
with st.sidebar:
    st.header("📌 Application Summary")
    total_applied = st.number_input("Total Jobs Applied", value=50, step=1)
    successful = st.number_input("Successfully Applied", value=45, step=1)
    failed = st.number_input("Failed to Apply", value=5, step=1)
    calls_received = st.number_input("Job Calls Received", value=10, step=1)
    rejections = st.number_input("Total Rejections", value=8, step=1)
    offers = st.number_input("Offers Received", value=2, step=1)
    interviews_scheduled = st.number_input("Interviews Scheduled", value=5, step=1)
    follow_ups_sent = st.number_input("Follow-ups Sent", value=7, step=1)

# Tabs
tab1, tab2 = st.tabs(["📊 Application Tracker", "🔍 Scraped Job Listings"])

# --------- TAB 1: Application Tracker ---------
with tab1:
    st.subheader("📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Successfully Applied", successful, f"{(successful / total_applied) * 100:.1f}%")
    col2.metric("❌ Failed to Apply", failed, f"{(failed / total_applied) * 100:.1f}%")
    col3.metric("📞 Job Calls Received", calls_received)

    col4, col5, col6 = st.columns(3)
    col4.metric("🗓️ Interviews Scheduled", interviews_scheduled)
    col5.metric("📬 Follow-ups Sent", follow_ups_sent)
    col6.metric("🔥 Offer Rate", f"{(offers / total_applied) * 100:.1f}%" if total_applied else "0.0%")

    col7, col8 = st.columns(2)
    col7.metric("❗ Total Rejections", rejections)
    col8.metric("🎉 Offers Received", offers)

    st.markdown("---")

    st.subheader("🚀 Visual Progress Overview")
    st.progress(successful / total_applied, text=f"{successful} successful applications")
    st.progress(calls_received / total_applied, text=f"{calls_received} interview calls")
    st.progress(interviews_scheduled / total_applied, text=f"{interviews_scheduled} interviews scheduled")

    st.markdown("---")

# --------- TAB 2: Scraped Job Listings Dashboard ---------
with tab2:
    st.subheader("🔎 Scraped Job Listings Dashboard")

    st.subheader("📂 Upload Your Job Tracker CSV")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="app_tracker")

    if uploaded_file:
        df = load_data(uploaded_file)
        st.success("CSV uploaded successfully!")

        st.markdown("### 📊 Data Insights")
        col1, col2, col3 = st.columns(3)
        col1.metric("📟 Total Jobs", len(df))
        col2.metric("🏢 Companies", df["Company"].nunique() if 'Company' in df.columns else "N/A")
        col3.metric("📅 Last Scraped", df["Scraped On"].max().strftime("%Y-%m-%d") if 'Scraped On' in df.columns else "No data")

        if 'Application Status' in df.columns:
            st.markdown("#### ➡️ Application Status Breakdown")
            status_counts = df['Application Status'].value_counts()
            st.pyplot(plot_job_status_pie_chart(status_counts))

        if 'Pay' in df.columns:
            st.markdown("#### 💰 Pay Distribution")
            st.pyplot(plot_pay_distribution(df))

        if 'Pay' in df.columns and 'Location' in df.columns:
            st.markdown("#### 💼 Pay vs Location")
            st.pyplot(plot_pay_vs_location(df))

        st.markdown("---")

        # --- Filter Section ---
        st.sidebar.header("⚙️ Filtering Scraped Data")
        filters = {}
        categorical_cols = ['Company', 'Application Status', 'Work Mode', 'Location', 'Employment Type']
        for col in categorical_cols:
            if col in df.columns and df[col].nunique() > 0:
                selected_options = st.sidebar.multiselect(f"Select {col}", df[col].dropna().unique(), default=list(df[col].dropna().unique()))
                filters[col] = selected_options

        if 'Pay Min' in df.columns and 'Pay Max' in df.columns:
            min_pay_all = int(df["Pay Min"].min()) if not df["Pay Min"].empty else 0
            max_pay_all = int(df["Pay Max"].max()) if not df["Pay Max"].empty else 1000000
            min_pay, max_pay = st.sidebar.slider("Select Pay Range", min_pay_all, max_pay_all, (min_pay_all, max_pay_all))
            filters['Pay Min'] = (min_pay, float('inf'))
            filters['Pay Max'] = (float('-inf'), max_pay)

        if 'Scraped On' in df.columns and df['Scraped On'].notna().any():
            min_date = df["Scraped On"].min().date()
            max_date = df["Scraped On"].max().date()
            start_date, end_date = st.sidebar.date_input("Select Scraping Date Range", (min_date, max_date))
            filters['Scraped On'] = (start_date, end_date)

        # Apply Filters
        filtered_df = apply_filters(df, filters)

        st.markdown(f"### 🌟 Filtered Jobs ({len(filtered_df)})")
        if not filtered_df.empty:
            st.dataframe(filtered_df[["Job Title", "Company", "Location", "Work Mode", "Application Status", "Pay", "Scraped On", "Skills"]], use_container_width=True)

            st.markdown("#### ☁️ Filtered Skills")
            filtered_skills_text = ", ".join(filtered_df["Skills"].dropna().astype(str))
            if filtered_skills_text:
                st.pyplot(generate_wordcloud(filtered_skills_text))
            else:
                st.info("No skills data available for word cloud in the filtered dataset.")

            st.markdown("#### 📜 Detailed Job Descriptions (Filtered)")
            for index, row in filtered_df.iterrows():
                with st.expander(f"{row['Job Title']} @ {row['Company']} ({row['Location']})"):
                    for col, value in row.items():
                        if pd.notna(value):
                            st.markdown(f"**{col.replace('_', ' ').title()}**: {value}")
                    if "Job Description" in row and pd.notna(row["Job Description"]):
                        st.markdown("**Job Description**:")
                        st.write(row["Job Description"])
                    if "Skills" in row and pd.notna(row["Skills"]):
                        st.markdown("**Skills**:")
                        st.code(row["Skills"], language="text")
        else:
            st.info("No jobs match the selected filters.")
