import google.generativeai as genai
import json
import pandas as pd

def generate_pandas_query(question, columns):

    model = genai.GenerativeModel(
        "models/gemini-2.5-flash"
    )

    prompt = f"""
You are a Pandas expert.

Dataset columns:

{columns}

Convert the user's question into ONLY a valid pandas expression.

Rules:
- Assume dataframe name is df
- Return ONLY pandas code
- No markdown
- No explanations
- No imports
- No print statements
- No variable assignments

Examples:

Question:
Which region has highest sales?

Output:
df.groupby("Region")["Sales"].sum().sort_values(ascending=False).head(1)

Question:
Top 5 customers by sales

Output:
df.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(5)

User Question:
{question}
"""

    response = model.generate_content(prompt)

    return response.text.strip()

def execute_query(query, df):

    blocked_words = [
        "import",
        "open",
        "exec",
        "eval",
        "__",
        "os.",
        "sys.",
        "subprocess",
        "compile",
        "globals",
        "locals",
        "getattr",
        "setattr",
        "delattr"
    ]

    query_lower = query.lower()

    for word in blocked_words:

        if word in query_lower:

            return "Unsafe query detected."

    try:

        safe_globals = {
            "__builtins__": {},
            "df": df,
            "pd": pd
        }

        result = eval(
            query,
            safe_globals,
            {}
        )

        return result

    except Exception as e:

        return f"Execution Error: {e}"
    
def explain_result(question, result):

    model = genai.GenerativeModel(
        "models/gemini-2.5-flash"
    )

    prompt = f"""
You are a Senior Business Analyst.

Question:
{question}

Query Result:
{result}

Explain:

1. What the result means
2. Why it matters
3. Any business implication

Keep it under 150 words.
Use business-friendly language.
"""

    response = model.generate_content(
        prompt
    )

    return response.text


def generate_executive_summary(
    metadata,
    dataset_profile,
    dynamic_kpis
):

    model = genai.GenerativeModel(
        "models/gemini-2.5-flash"
    )

    successful_kpis = {}

    for kpi_name, kpi_data in dynamic_kpis.items():

        if kpi_data.get("status") == "success":

            successful_kpis[kpi_name] = str(
                kpi_data.get("result")
            )

    prompt = f"""
You are a Senior Business Analyst preparing an executive
summary for business stakeholders.

The analysis below is based on an uploaded dataset.

DATASET METADATA:

{metadata}

AI-DISCOVERED DATASET PROFILE:

{dataset_profile}

PANDAS-CALCULATED KPI RESULTS:

{successful_kpis}

IMPORTANT GROUNDING RULES:

- Base all numerical claims on the provided KPI results.
- Do not invent values.
- Do not estimate missing metrics.
- Do not claim a KPI was calculated if it is not present.
- The KPI values were calculated directly from the dataset
  using Pandas and should be treated as the source of truth.
- Clearly distinguish facts from business interpretation.
- Do not use LaTeX.
- Do not use mathematical dollar-sign formatting.
- Write currency values as plain text.
- Write percentages as plain text.
- Round long decimal values for readability.
- Use professional but easy-to-understand business language.

Create an executive summary with these sections:

## Executive Summary

Provide a concise overview of the dataset and its analytical context.

## Key Findings

Explain the most important KPI results and what they reveal.

## Risks

Identify potential business risks supported by the available KPI results.

## Opportunities

Identify realistic opportunities based on the results.

## Recommendations

Provide practical, actionable recommendations.

Keep the entire summary under 400 words.

Do not mention Pandas, Gemini, generated queries, metadata,
or the internal analysis process.
"""

    response = model.generate_content(
        prompt
    )

    return response.text.strip()

def discover_dataset_kpis(metadata):

    model = genai.GenerativeModel(
        "models/gemini-2.5-flash"
    )

    prompt = f"""
You are a Senior Data Analyst.

Analyze the dataset metadata below and identify the
structure and the most useful KPIs for this specific dataset.

Dataset Metadata:

{metadata}

Your tasks:

1. Identify categorical or grouping columns as dimensions.
2. Identify meaningful numeric columns as metrics.
3. Identify date or time-related columns.
4. Recommend exactly 5 important KPIs that can be calculated
   directly from the available dataset columns.

STRICT KPI RULES:

- Each KPI must represent ONE calculation only.
- Do not combine multiple KPIs into one KPI name.
- Do not use words such as "and", "/" or multiple alternatives
  to combine calculations.
- Each KPI must be directly calculable using Pandas.
- Do not recommend vague analytical tasks.
- Do not recommend dashboards, reports or general analysis.
- Do not invent columns.
- Prefer KPIs that provide useful decision-making information.
- Adapt KPIs to the dataset domain.
- Keep KPI names short and precise.

BAD KPI EXAMPLES:

"Total Sales and Sales Growth"
"Top/Bottom Products by Sales & Profit"
"Revenue and Profit Analysis"
"Customer and Product Performance"

GOOD KPI EXAMPLES:

"Total Sales"
"Profit Margin"
"Average Order Value"
"Top Product by Sales"
"Shipping Cost Ratio"

For an HR dataset, suitable KPIs might include:

"Average Salary"
"Employee Count"
"Average Performance Score"
"Average Employee Tenure"
"Top Department by Performance"

For an inventory dataset, suitable KPIs might include:

"Total Inventory Value"
"Low Stock Product Count"
"Average Stock Level"
"Top Product by Stock Value"
"Out of Stock Product Count"

Return ONLY valid JSON.

Use exactly this structure:

{{
    "dimensions": [],
    "metrics": [],
    "date_columns": [],
    "recommended_kpis": []
}}

Dataset Metadata:

{metadata}
"""

    response = model.generate_content(
        prompt
    )

    cleaned_response = (
        response.text
        .strip()
        .replace("```json", "")
        .replace("```", "")
    )

    return json.loads(
        cleaned_response
    )

def generate_kpi_queries(
    recommended_kpis,
    columns
):

    model = genai.GenerativeModel(
        "models/gemini-2.5-flash"
    )

    prompt = f"""
You are an expert Python Pandas data analyst.

A dataset contains these columns:

{columns}

The following KPIs have been recommended for this dataset:

{recommended_kpis}

Your task is to generate ONE valid Pandas expression for EACH KPI.

IMPORTANT RULES:

- Assume the DataFrame name is df.
- Use ONLY columns that exist in the provided column list.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not include explanations.
- Do not include imports.
- Do not use print().
- Do not assign variables.
- Do not use loops.
- Do not use exec() or eval().
- Each query must be a single Pandas expression.
- Calculations must use the actual DataFrame.
- For average order value, calculate total value per unique order first, then calculate the mean.
- For percentages or ratios, return the calculated numeric value.
- Do not invent column names.
- If a KPI cannot be calculated from the available columns, return null for its query.

Return JSON in exactly this structure:

{{
    "kpi_queries": [
        {{
            "kpi": "KPI name",
            "query": "df expression"
        }}
    ]
}}

Example:

{{
    "kpi_queries": [
        {{
            "kpi": "Total Sales",
            "query": "df['Sales'].sum()"
        }},
        {{
            "kpi": "Total Profit",
            "query": "df['Profit'].sum()"
        }}
    ]
}}

Recommended KPIs:

{recommended_kpis}

Dataset Columns:

{columns}
"""

    response = model.generate_content(
        prompt
    )

    cleaned_response = response.text.strip()

    cleaned_response = cleaned_response.replace(
        "```json",
        ""
    )

    cleaned_response = cleaned_response.replace(
        "```",
        ""
    )

    result = json.loads(
        cleaned_response
    )

    return result.get(
        "kpi_queries",
        []
    )
    
def execute_kpi_queries(
    kpi_queries,
    df
):

    kpi_results = {}

    for kpi_data in kpi_queries:

        kpi_name = kpi_data.get(
            "kpi"
        )

        query = kpi_data.get(
            "query"
        )

        if not kpi_name:
            continue

        if not query:

            kpi_results[kpi_name] = {
                "status": "unavailable",
                "query": None,
                "result": (
                    "KPI cannot be calculated "
                    "from available columns."
                )
            }

            continue

        result = execute_query(
            query,
            df
        )

        if isinstance(result, str):

            if (
                result.startswith(
                    "Execution Error"
                )
                or result
                == "Unsafe query detected."
            ):

                kpi_results[kpi_name] = {
                    "status": "failed",
                    "query": query,
                    "result": result
                }

                continue

        kpi_results[kpi_name] = {
            "status": "success",
            "query": query,
            "result": result
        }

    return kpi_results