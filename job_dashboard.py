import streamlit as st
import pandas as pd

st.set_page_config(page_title="Job Tracker Dashboard", layout="wide")

# Title
st.title("📊 Job Application Tracker Dashboard")

# Sidebar - data input
st.sidebar.header("Job Tracker Summary")
total_applied = st.sidebar.number_input("Total Jobs Applied", value=50, step=1)
successful = st.sidebar.number_input("Successfully Applied", value=45, step=1)
failed = st.sidebar.number_input("Failed to Apply", value=5, step=1)
calls_received = st.sidebar.number_input("Job Calls Received", value=10, step=1)
rejections = st.sidebar.number_input("Total Rejections", value=8, step=1)
offers = st.sidebar.number_input("Offers Received", value=2, step=1)

st.markdown("---")

# KPI Display - 3 column layout
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="✅ Successfully Applied", value=successful, delta=f"{(successful/total_applied)*100:.1f}%")

with col2:
    st.metric(label="❌ Failed to Apply", value=failed, delta=f"{(failed/total_applied)*100:.1f}%")

with col3:
    st.metric(label="📞 Job Calls Received", value=calls_received)

# Second Row
col4, col5, col6 = st.columns(3)

with col4:
    st.metric(label="❗ Total Rejections", value=rejections)

with col5:
    st.metric(label="🎉 Offers Received", value=offers)

with col6:
    conversion_rate = (offers / total_applied) * 100 if total_applied else 0
    st.metric(label="🔥 Offer Rate", value=f"{conversion_rate:.1f}%")

st.markdown("---")

# Optional: Display progress bars
st.subheader("📈 Progress Summary")
st.progress(successful / total_applied)
st.info(f"{successful} out of {total_applied} applications submitted successfully.")

st.progress(calls_received / total_applied)
st.info(f"{calls_received} interview calls out of {total_applied}.")

st.markdown("---")

# Optional: Upload job application CSV
st.subheader("📂 Upload Job Tracker CSV (optional)")
uploaded_file = st.file_uploader("Upload your job tracker file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
    st.success("CSV uploaded and displayed successfully!")

