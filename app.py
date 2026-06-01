from unittest import result
import google.generativeai as genai
import requests
import json
from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

if "ai_charts" not in st.session_state:
    st.session_state.ai_charts = None
    

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)




# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Smart ETL Data Cleaner",
    layout="wide"
)

st.title("📊 Smart ETL Data Cleaner")

st.write("Upload a CSV or Excel file for data analysis.")

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

# -----------------------------
# PROCESS FILE
# -----------------------------
if uploaded_file is not None:

    try:

        # -----------------------------
        # READ FILE
        # -----------------------------
        if uploaded_file.name.endswith(".csv"):

            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')

            except:
                df = pd.read_csv(uploaded_file, encoding='latin1')

        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully!")
        
        

        # -----------------------------
        # DATA PREVIEW
        # -----------------------------
        st.subheader("📌 Dataset Preview")

        st.dataframe(df.head(20))


        # -----------------------------
        # DATASET INFO
        # -----------------------------
        st.subheader("📌 Dataset Information")

        info_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Missing Values": df.isnull().sum().values,
            "Duplicate Values": df.duplicated().sum(),
            "Umique Values": df.nunique().values
        })

        st.dataframe(info_df)
        
        
        # =============================
        # TRANSFORMATION SECTION
        # =============================

        st.header("⚙️ Data Transformation Options")

        transformed_df = df.copy()

        
        # -----------------------------
        # DOWNLOAD CLEANED FILE
        # -----------------------------
        csv = transformed_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download Cleaned CSV",
            data=csv,
            file_name=f"cleaned_{uploaded_file.name.split('.')[0]}.csv",
            mime="text/csv"
        )
        # =============================
        # AI DATASET ASSISTANT
        # =============================

        st.header("🤖 AI Dataset Assistant")

        if st.button("Generate AI Insights"):

            with st.spinner("Generating AI Dashboard..."):

                try:

                    st.session_state.ai_charts = generate_ai_summary(metadata)

                except Exception as e:

                    st.error(f"AI Error: {e}")

        with st.spinner("Analyzing dataset with AI..."):
                    
            if st.session_state.ai_charts:
                ai_charts = st.session_state.ai_charts
                st.subheader("📊 AI Generated Dashboard")
                # =============================
                # FILTER SECTION
                # =============================

                st.header("🎛️ Dashboard Filters")

                categorical_cols = transformed_df.select_dtypes(
                    include="object"
                ).columns

                filterable_cols = []

                for col in categorical_cols:
                    unique_count = transformed_df[col].nunique()

                    
                    if unique_count <= 15:
                        filterable_cols.append(col)

                filtered_df = transformed_df.copy()

                selected_filters = {}

                for col in filterable_cols[:3]:

                    options = transformed_df[col].dropna().unique()

                    selected_value = st.selectbox(
                        f"Select {col}",
                        options=["All"] + list(options),
                        key=col
                    )

                    selected_filters[col] = selected_value

                    if selected_value != "All":

                        filtered_df = filtered_df[
                            filtered_df[col] == selected_value
                        ]

                # =============================
                # CHART SECTION
                # =============================

                    allowed_charts = ["bar", "line", "scatter", "pie"]

                    cols = st.columns(2)

                    for idx, chart_data in enumerate(ai_charts):
                        current_col = cols[idx % 2]

                        with current_col:
                            pass

    except Exception as e:
            st.error(f"Error processing file: {e}")

    