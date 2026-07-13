#utils/ app.py

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
from utils.ai_helper import generate_ai_summary
from utils.profiling import calculate_quality_score 
from utils.profiling import generate_metadata
from utils.chat_helper import chat_with_dataset
from utils.dashboard import render_dashboard
from utils.transformations import apply_missing_strategy
from utils.chat_helper import find_matching_rows
from utils.chat_helper import detect_query_type
from utils.query_engine import (
    generate_pandas_query,
    execute_query,
    explain_result,
    generate_executive_summary,
    discover_dataset_kpis,
    generate_kpi_queries,
    execute_kpi_queries
)

# =============================
# SESSION STATE
# =============================

if "ai_charts" not in st.session_state:
    st.session_state.ai_charts = None

if "dataset_profile" not in st.session_state:
    st.session_state.dataset_profile = None

if "dynamic_kpis" not in st.session_state:
    st.session_state.dynamic_kpis = None

if "kpi_queries" not in st.session_state:
    st.session_state.kpi_queries = None

if "analyzed_dataset_id" not in st.session_state:
    st.session_state.analyzed_dataset_id = None


# =============================
# GEMINI CONFIGURATION
# =============================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

genai.configure(
    api_key=GEMINI_API_KEY
)


# =============================
# PAGE CONFIG
# =============================

st.set_page_config(
    page_title="Smart ETL Data Cleaner",
    layout="wide"
)

st.title(
    "📊 Smart ETL Data Cleaner"
)

st.write(
    "Upload a CSV or Excel file for data analysis."
)


# =============================
# FILE UPLOAD
# =============================

uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)


# =============================
# PROCESS FILE
# =============================

if uploaded_file is not None:

    try:

        # -----------------------------
        # READ FILE
        # -----------------------------

        if uploaded_file.name.endswith(
            ".csv"
        ):

            try:

                df = pd.read_csv(
                    uploaded_file,
                    encoding="utf-8"
                )

            except UnicodeDecodeError:

                df = pd.read_csv(
                    uploaded_file,
                    encoding="latin1"
                )

        else:

            df = pd.read_excel(
                uploaded_file
            )


        st.success(
            "✅ File uploaded successfully!"
        )


        # =============================
        # RAW DATASET QUALITY
        # =============================

        quality_score = (
            calculate_quality_score(df)
        )


        # =============================
        # DATASET OVERVIEW
        # =============================

        st.subheader(
            "📊 Dataset Overview"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Rows",
                df.shape[0]
            )

        with col2:

            st.metric(
                "Columns",
                df.shape[1]
            )

        with col3:

            st.metric(
                "Data Quality",
                f"{quality_score}%"
            )


        # -----------------------------
        # QUALITY STATUS
        # -----------------------------

        if quality_score == 100:

            st.success(
                "✅ Dataset quality is excellent. "
                "No transformations required."
            )

        elif quality_score >= 90:

            st.success(
                "Excellent Data Quality ✅"
            )

        elif quality_score >= 70:

            st.warning(
                "Moderate Data Quality ⚠️"
            )

        else:

            st.error(
                "Poor Data Quality ❌"
            )


        # =============================
        # TRANSFORMATION SECTION
        # =============================

        st.header(
            "⚙️ Data Transformation Options"
        )

        transformed_df = df.copy()


        # -----------------------------
        # MISSING VALUES
        # -----------------------------

        missing_strategy = st.selectbox(
            "Choose strategy",
            [
                "Do Nothing",
                "Fill Numeric with Mean",
                "Fill Numeric with Median",
                "Fill All with Mode",
                "Fill Categorical with 'Unknown'",
                "Drop Missing Rows"
            ]
        )

        transformed_df = (
            apply_missing_strategy(
                transformed_df,
                missing_strategy
            )
        )


        # -----------------------------
        # DUPLICATES
        # -----------------------------

        remove_duplicates = st.checkbox(
            "Remove Duplicate Rows"
        )

        if remove_duplicates:

            transformed_df = (
                transformed_df
                .drop_duplicates()
            )


        # -----------------------------
        # COLUMN CLEANING
        # -----------------------------

        clean_columns = st.checkbox(
            "Clean Column Names"
        )

        if clean_columns:

            transformed_df.columns = (
                transformed_df.columns
                .str.strip()
                .str.lower()
                .str.replace(
                    " ",
                    "_"
                )
                .str.replace(
                    "-",
                    "_"
                )
            )


        # =============================
        # TRANSFORMED DATA PREVIEW
        # =============================

        st.subheader(
            "📌 Transformed Dataset Preview"
        )

        st.dataframe(
            transformed_df.head(20)
        )


        # =============================
        # FINAL DATASET PROFILING
        # =============================

        final_quality_score = (
            calculate_quality_score(
                transformed_df
            )
        )

        metadata = generate_metadata(
            transformed_df,
            final_quality_score
        )


        # =============================
        # DATASET FINGERPRINT
        # =============================

        dataset_id = (
            uploaded_file.name,
            transformed_df.shape,
            tuple(
                transformed_df.columns
            ),
            final_quality_score
        )


        # -----------------------------
        # CLEAR OLD AI ANALYSIS
        # -----------------------------

        if (
            st.session_state.analyzed_dataset_id
            is not None
            and
            st.session_state.analyzed_dataset_id
            != dataset_id
        ):

            st.session_state.dataset_profile = None

            st.session_state.dynamic_kpis = None

            st.session_state.kpi_queries = None

            st.session_state.analyzed_dataset_id = None

            st.session_state.ai_charts = None


        # =============================
        # DOWNLOAD CLEANED FILE
        # =============================

        csv = (
            transformed_df
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            label="📥 Download Cleaned CSV",
            data=csv,
            file_name=(
                f"cleaned_"
                f"{uploaded_file.name.split('.')[0]}"
                f".csv"
            ),
            mime="text/csv"
        )


        # =============================
        # AI DATASET ANALYSIS
        # =============================

        st.header(
            "🤖 AI Dataset Analysis"
        )

        st.write(
            "Analyze the dataset structure and "
            "automatically discover relevant KPIs."
        )


        if st.button(
            "🔍 Analyze Dataset",
            key="analyze_dataset"
        ):

            try:

                # -----------------------------
                # DISCOVER KPIs
                # GEMINI CALL 1
                # -----------------------------

                with st.spinner(
                    "Discovering relevant KPIs..."
                ):

                    dataset_profile = (
                        discover_dataset_kpis(
                            metadata
                        )
                    )


                # -----------------------------
                # GENERATE KPI QUERIES
                # GEMINI CALL 2
                # -----------------------------

                with st.spinner(
                    "Generating KPI calculations..."
                ):

                    kpi_queries = (
                        generate_kpi_queries(
                            dataset_profile.get(
                                "recommended_kpis",
                                []
                            ),
                            list(
                                transformed_df.columns
                            )
                        )
                    )


                # -----------------------------
                # EXECUTE KPIs LOCALLY
                # NO GEMINI CALL
                # -----------------------------

                with st.spinner(
                    "Calculating KPI results..."
                ):

                    dynamic_kpis = (
                        execute_kpi_queries(
                            kpi_queries,
                            transformed_df
                        )
                    )


                # -----------------------------
                # SAVE RESULTS
                # -----------------------------

                st.session_state.dataset_profile = (
                    dataset_profile
                )

                st.session_state.kpi_queries = (
                    kpi_queries
                )

                st.session_state.dynamic_kpis = (
                    dynamic_kpis
                )

                st.session_state.analyzed_dataset_id = (
                    dataset_id
                )


                st.success(
                    "✅ Dataset analysis completed!"
                )


            except Exception as e:

                st.error(
                    f"AI Analysis Error: {e}"
                )


        # =============================
        # DEVELOPER DETAILS
        # =============================

        if (
            st.session_state.dataset_profile
            is not None
        ):

            with st.expander(
                "🛠️ Developer Details"
            ):

                st.subheader(
                    "Dataset Profile"
                )

                st.json(
                    st.session_state.dataset_profile
                )


                st.subheader(
                    "Generated KPI Queries"
                )

                st.json(
                    st.session_state.kpi_queries
                )


                st.subheader(
                    "Dynamic KPI Results"
                )

                st.write(
                    st.session_state.dynamic_kpis
                )


        # =============================
        # AI DATA ANALYST
        # =============================

        st.header(
            "🤖 AI Data Analyst"
        )

        st.subheader(
            "📊 Ask Questions About Your Data"
        )

        analytics_question = st.text_input(
            "Ask a business question"
        )


        if st.button(
            "Ask AI",
            key="ask_ai"
        ):

            if not analytics_question.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                with st.spinner(
                    "Analyzing..."
                ):

                    try:

                        query = (
                            generate_pandas_query(
                                analytics_question,
                                list(
                                    transformed_df.columns
                                )
                            )
                        )


                        # TEMPORARY DEBUG VIEW
                        with st.expander(
                            "View Generated Query"
                        ):

                            st.code(
                                query,
                                language="python"
                            )


                        result = execute_query(
                            query,
                            transformed_df
                        )


                        st.subheader(
                            "📊 Result"
                        )

                        st.write(
                            result
                        )


                        explanation = explain_result(
                            analytics_question,
                            result
                        )


                        st.subheader(
                            "🧠 AI Explanation"
                        )

                        st.info(
                            explanation
                        )


                    except Exception as e:

                        st.error(
                            f"Analysis Error: {e}"
                        )


        # =============================
        # EXECUTIVE SUMMARY
        # =============================

        st.header(
            "📄 Executive Summary"
        )

        if st.button(
            "Generate Executive Summary",
            key="executive_summary"
        ):

            if (
                st.session_state.dynamic_kpis
                is None
            ):

                st.warning(
                    "Please click 'Analyze Dataset' first "
                    "to discover and calculate relevant KPIs."
                )

            else:

                with st.spinner(
                    "Generating executive summary..."
                ):

                    try:

                        summary = (
                            generate_executive_summary(
                                metadata,
                                st.session_state.dataset_profile,
                                st.session_state.dynamic_kpis
                            )
                        )

                        st.markdown(
                            summary
                        )

                    except Exception as e:

                        st.error(
                            f"Executive Summary Error: {e}"
                        )


        # =============================
        # AI GENERATED DASHBOARD
        # =============================

        st.header(
            "📈 AI Dashboard"
        )


        if st.button(
            "Generate AI Insights",
            key="generate_ai_insights"
        ):

            with st.spinner(
                "Generating AI Dashboard..."
            ):

                try:

                    st.session_state.ai_charts = (
                        generate_ai_summary(
                            metadata
                        )
                    )


                except Exception as e:

                    st.error(
                        f"AI Error: {e}"
                    )


        # -----------------------------
        # RENDER DASHBOARD
        # -----------------------------

        if st.session_state.ai_charts:

            ai_charts = (
                st.session_state.ai_charts
            )

            st.subheader(
                "📊 AI Generated Dashboard"
            )


            # =============================
            # DASHBOARD FILTERS
            # =============================

            st.header(
                "🎛️ Dashboard Filters"
            )

            categorical_cols = (
                transformed_df
                .select_dtypes(
                    include=["object", "str"]
                )
                .columns
            )

            filterable_cols = []

            for col in categorical_cols:

                unique_count = (
                    transformed_df[col]
                    .nunique()
                )

                if unique_count <= 15:

                    filterable_cols.append(
                        col
                    )


            filtered_df = (
                transformed_df.copy()
            )


            for col in filterable_cols[:3]:

                options = (
                    transformed_df[col]
                    .dropna()
                    .unique()
                )

                selected_value = st.selectbox(
                    f"Select {col}",
                    options=[
                        "All"
                    ] + list(options),
                    key=f"dashboard_filter_{col}"
                )


                if selected_value != "All":

                    filtered_df = (
                        filtered_df[
                            filtered_df[col]
                            == selected_value
                        ]
                    )


            # =============================
            # CHART SECTION
            # =============================

            render_dashboard(
                ai_charts,
                filtered_df
            )


    except Exception as e:

        st.error(
            f"Error processing file: {e}"
        )