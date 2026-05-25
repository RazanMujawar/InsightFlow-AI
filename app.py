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

def generate_ai_summary(metadata):

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    prompt = f"""
You are a data visualization expert.

Based on this dataset metadata, recommend the 4 best visualizations.

Return ONLY valid JSON.

Use this format:

[
  {{
    "chart": "bar",
    "x": "column_name",
    "y": "column_name",
    "title": "chart title",
    "insight": "2-3 sentence business-friendly explanation of the chart and what users should observe"
    The insight should:
    - explain what the chart shows
    - explain why it matters
    - be easy for non-technical users to understand
    - avoid one-line responses
  }}
]

Allowed chart types:
- bar
- line
- scatter
- pie

Dataset Metadata:
{metadata}
"""

    response = model.generate_content(prompt)
    
    cleaned_response = response.text.strip()

    # Remove markdown formatting if present
    cleaned_response = cleaned_response.replace("```json", "")
    cleaned_response = cleaned_response.replace("```", "")

    return json.loads(cleaned_response)


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
        # DATA QUALITY CALCULATION
        # -----------------------------
        total_cells = df.shape[0] * df.shape[1]

        missing_cells = df.isnull().sum().sum()

        duplicate_rows = df.duplicated().sum()

        duplicate_penalty = duplicate_rows * df.shape[1]

        quality_score = (
            1 - ((missing_cells + duplicate_penalty) / total_cells)
        ) * 100

        quality_score = round(quality_score, 2)
        

        # -----------------------------
        # TOP KPI CARDS
        # -----------------------------
        st.subheader("📊 Dataset Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Rows", df.shape[0])

        with col2:
            st.metric("Columns", df.shape[1])

        with col3:
            st.metric("Data Quality", f"{quality_score}%")

        # -----------------------------
        # QUALITY STATUS
        # -----------------------------
        if quality_score == 100:
            st.success("✅ Dataset quality is excellent. No transformations required.")
        
        elif quality_score >= 90:
            st.success("Excellent Data Quality ✅")

        elif quality_score >= 70:
            st.warning("Moderate Data Quality ⚠️")

        else:
            st.error("Poor Data Quality ❌")
            
        # -----------------------------
        # METADATA FOR AI
        # -----------------------------
        metadata = {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": list(df.columns),
            "data_types": {
                col: str(dtype)
                for col, dtype in df.dtypes.items()
            },
            "missing_values": {
                col: int(val)
                for col, val in df.isnull().sum().items()
            },
            "duplicate_rows": int(df.duplicated().sum()),
            "quality_score": quality_score
        }

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
        # HANDLE MISSING VALUES
        # -----------------------------
        st.subheader("Handle Missing Values")

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

        numeric_cols = transformed_df.select_dtypes(include=['number']).columns
        categorical_cols = transformed_df.select_dtypes(exclude=['number']).columns

        if missing_strategy == "Fill Numeric with Mean":

            transformed_df[numeric_cols] = transformed_df[numeric_cols].fillna(
                transformed_df[numeric_cols].mean()
            )

            st.success("✅ Numeric missing values filled using Mean")

        elif missing_strategy == "Fill Numeric with Median":

            transformed_df[numeric_cols] = transformed_df[numeric_cols].fillna(
                transformed_df[numeric_cols].median()
            )

            st.success("✅ Numeric missing values filled using Median")

        elif missing_strategy == "Fill All with Mode":

            for col in transformed_df.columns:
                transformed_df[col] = transformed_df[col].fillna(
                    transformed_df[col].mode()[0]
                )

            st.success("✅ All missing values filled using Mode")

        elif missing_strategy == "Fill Categorical with 'Unknown'":

            transformed_df[categorical_cols] = transformed_df[categorical_cols].fillna(
                "Unknown"
            )

            st.success("✅ Categorical missing values filled with 'Unknown'")

        elif missing_strategy == "Drop Missing Rows":

            transformed_df = transformed_df.dropna()

            st.success("✅ Missing rows dropped")

        # -----------------------------
        # REMOVE DUPLICATES
        # -----------------------------
        st.subheader("Duplicate Handling")

        remove_duplicates = st.checkbox("Remove Duplicate Rows")

        if remove_duplicates:
            before = transformed_df.shape[0]

            transformed_df = transformed_df.drop_duplicates()

            after = transformed_df.shape[0]

            st.success(f"✅ Removed {before - after} duplicate rows")

        # -----------------------------
        # CLEAN COLUMN NAMES
        # -----------------------------
        st.subheader("Column Name Cleaning")

        clean_columns = st.checkbox(
            "Convert column names to lowercase and replace spaces"
        )

        if clean_columns:
            transformed_df.columns = (
                transformed_df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
                .str.replace("-", "_")
            )

            st.success("✅ Column names cleaned")

        # -----------------------------
        # SHOW TRANSFORMED DATA
        # -----------------------------
        st.subheader("📌 Transformed Dataset Preview")

        st.dataframe(transformed_df.head(20))
        st.write("Remaining Missing Values:")
        st.write(transformed_df.isnull().sum())

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
                        
                        st.subheader("📊 AI Generated Dashboard")
                        
                        ai_charts = st.session_state.ai_charts

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
                            
                            try:

                                chart_type = chart_data.get("chart")
                                x_col = chart_data.get("x")
                                y_col = chart_data.get("y")
                                title = chart_data.get("title")
                                insight = chart_data.get("insight")

                                # -----------------------------
                                # VALIDATION
                                # -----------------------------
                                if chart_type not in allowed_charts:
                                    continue

                                if x_col not in transformed_df.columns:
                                    continue

                                if y_col not in transformed_df.columns:
                                    continue

                                st.markdown(f"### {title}")
                                if insight:
                                    st.info(f"📌 Insight: {insight}")

                                fig, ax = plt.subplots(figsize=(6, 4))
                                
                                # -----------------------------
                                # BAR CHART
                                # -----------------------------
                                if chart_type == "bar":

                                    grouped = (
                                        filtered_df
                                        .groupby(x_col)[y_col]
                                        .sum()
                                        .sort_values(ascending=False)
                                        .head(10)
                                    )

                                    grouped.plot(
                                        kind="bar",
                                        ax=ax
                                    )

                                # -----------------------------
                                # LINE CHART
                                # -----------------------------
                                elif chart_type == "line":

                                    grouped = (
                                        filtered_df
                                        .groupby(x_col)[y_col]
                                        .sum()
                                    )

                                    grouped.plot(
                                        kind="line",
                                        ax=ax
                                    )

                                # -----------------------------
                                # SCATTER CHART
                                # -----------------------------
                                elif chart_type == "scatter":

                                    ax.scatter(
                                        filtered_df[x_col],
                                        filtered_df[y_col]
                                    )

                                    ax.set_xlabel(x_col)
                                    ax.set_ylabel(y_col)

                                # -----------------------------
                                # PIE CHART
                                # -----------------------------
                                elif chart_type == "pie":

                                    grouped = (
                                        filtered_df
                                        .groupby(x_col)[y_col]
                                        .sum()
                                        .head(5)
                                    )

                                    grouped.plot(
                                        kind="pie",
                                        ax=ax,
                                        autopct="%1.1f%%"
                                    )

                                ax.set_title(title)
                                plt.tight_layout()
                                st.pyplot(fig)

                            except Exception as e:

                                st.warning(
                                f"Could not generate chart: {e}"
                            )

    except Exception as e:

                    st.error(f"AI Error: {e}")
    except Exception as e:
        st.error(f"❌ Error: {e}")
        