# InsightFlow AI

InsightFlow AI is an AI-powered data analytics platform that transforms raw CSV and Excel datasets into structured, actionable business insights.

The platform combines automated data preparation, dynamic dataset understanding, AI-driven KPI discovery, natural language analytics, grounded business explanations, executive summaries, and intelligent dashboards in a single Streamlit application.

Rather than relying on a fixed dataset structure or a single business domain, InsightFlow AI is designed to analyze uploaded datasets dynamically and adapt its analytical workflow based on the available columns, metrics, dimensions, and date fields.

---

## Overview

Traditional data analysis often requires several manual steps:

- Inspecting the dataset
- Identifying data quality issues
- Cleaning and transforming data
- Understanding columns and relationships
- Selecting relevant KPIs
- Writing analytical queries
- Calculating business metrics
- Creating visualizations
- Interpreting results for stakeholders

InsightFlow AI aims to simplify this workflow.

Users can upload a CSV or Excel dataset, apply data transformations, allow AI to understand the dataset structure, automatically discover relevant KPIs, ask business questions in natural language, and generate business-friendly analytical insights.

The platform follows a hybrid AI and deterministic analytics approach.

AI is used for semantic understanding, analytical reasoning, and query generation, while Pandas performs calculations directly on the uploaded dataset.

---

## Key Features

### Data Upload and Processing

- Upload CSV and Excel datasets
- Automatic CSV encoding fallback
- Dynamic dataset processing
- Support for different dataset structures

### Data Quality Analysis

- Automated data quality scoring
- Missing value detection
- Duplicate row analysis
- Dataset row and column overview
- Data quality status classification

### Data Transformation

Users can apply optional data cleaning operations, including:

- Fill numeric missing values using mean
- Fill numeric missing values using median
- Fill missing values using mode
- Fill categorical missing values with `Unknown`
- Drop rows containing missing values
- Remove duplicate rows
- Clean and standardize column names
- Download the transformed dataset as CSV

### AI Dataset Understanding

The AI analyzes dynamically generated dataset metadata to identify:

- Dimensions
- Metrics
- Date columns
- Dataset-specific analytical opportunities
- Relevant business KPIs

Dataset understanding is based on the uploaded dataset rather than a hardcoded domain.

### Dynamic KPI Discovery

InsightFlow AI automatically recommends important KPIs based on the structure of the dataset.

For example, a sales dataset may produce KPIs such as:

- Total Sales
- Profit Margin
- Average Order Value
- Top Product by Sales
- Shipping Cost Ratio

A different dataset, such as an HR dataset, may produce:

- Average Salary
- Employee Count
- Average Performance Score
- Average Employee Tenure
- Top Department by Performance

The KPI discovery process adapts to the available dataset columns.

### Batch KPI Query Generation

After discovering relevant KPIs, the platform generates Pandas expressions for all recommended KPIs in a single AI request.

Example:

```python
df["Sales"].sum()
```

```python
df["Profit"].sum() / df["Sales"].sum()
```

```python
df.groupby("Order ID")["Sales"].sum().mean()
```

The generated expressions are executed locally against the actual DataFrame.

This allows AI to determine what should be analyzed while Pandas performs the actual calculation.

### Natural Language Data Analytics

Users can ask business questions directly in natural language.

Example questions:

- Which state generates the highest profit?
- Which sub-category is least profitable?
- Show average sales by customer segment.
- Which region has the lowest profit?
- What are the top five loss-making products?
- Which customer generated the highest profit?
- Which category has the highest average discount?
- Compare sales across regions.
- Show profitability by category.

The system converts the user's question into a Pandas expression.

Example:

```text
User Question:
Which state generates the highest profit?
```

Generated analytical expression:

```python
df.groupby("State")["Profit"].sum().sort_values(
    ascending=False
).head(1)
```

Pandas then executes the expression against the uploaded dataset.

### Grounded AI Explanations

The language model does not directly guess answers from a small sample of dataset rows.

Instead, the workflow follows this pattern:

```text
User Question
      |
      v
AI Query Generation
      |
      v
Pandas Expression
      |
      v
Local DataFrame Execution
      |
      v
Actual Dataset Result
      |
      v
AI Business Explanation
```

This architecture improves analytical grounding because the final explanation is based on results calculated directly from the dataset.

### Executive Summary Generation

InsightFlow AI can generate stakeholder-friendly executive summaries containing:

- Executive overview
- Key findings
- Business risks
- Opportunities
- Actionable recommendations

The executive analysis is designed to communicate analytical findings in clear business language.

### AI-Generated Dashboard

The platform analyzes dataset metadata and recommends suitable visualizations.

Supported chart types currently include:

- Bar charts
- Line charts
- Scatter plots
- Pie charts

The dashboard includes:

- AI-generated chart titles
- Business-friendly chart explanations
- Dynamic column selection
- Dataset-driven visualization recommendations
- Interactive categorical filters
- Two-column dashboard layout

### AI API Optimization

The KPI analysis workflow was designed to reduce unnecessary AI API usage.

#### Previous Approach

```text
KPI Discovery        -> 1 AI Request
KPI 1 Query          -> 1 AI Request
KPI 2 Query          -> 1 AI Request
KPI 3 Query          -> 1 AI Request
KPI 4 Query          -> 1 AI Request
KPI 5 Query          -> 1 AI Request
```

Total:

```text
6 AI requests
```

#### Optimized Approach

```text
KPI Discovery
      |
      v
1 AI Request

Batch KPI Query Generation
      |
      v
1 AI Request

Local Pandas KPI Execution
      |
      v
0 AI Requests
```

Total:

```text
2 AI requests
```

AI analysis results are stored using Streamlit session state to prevent unnecessary regeneration during interface reruns.

---

## System Architecture

```text
                  CSV / Excel Dataset
                           |
                           v
                  Data Quality Engine
                           |
                           v
                  Transformation Engine
                           |
                           v
                    Metadata Generator
                           |
                           v
                AI Dataset Understanding
                           |
                           v
                 Dynamic KPI Discovery
                           |
                           v
              Batch Pandas Query Generation
                           |
                           v
                 Local Pandas Execution
                           |
              +------------+-------------+
              |                          |
              v                          v
       AI Data Analyst            Executive Insights
              |                          |
              +------------+-------------+
                           |
                           v
                  AI Generated Dashboard
```

---

## Hybrid AI Analytics Architecture

InsightFlow AI follows a hybrid AI and deterministic analytics architecture.

### AI Responsibilities

The AI model is responsible for:

- Understanding dataset metadata
- Identifying dimensions and metrics
- Discovering relevant KPIs
- Generating Pandas analytical expressions
- Recommending visualizations
- Explaining calculated results
- Generating business-friendly insights

### Pandas Responsibilities

Pandas is responsible for:

- Data transformations
- Missing value handling
- Duplicate removal
- Filtering
- Aggregations
- Grouping
- KPI calculations
- Query execution
- Returning actual dataset results

The core principle is:

```text
AI decides what and how to analyze
              |
              v
Pandas calculates the actual result
              |
              v
AI explains the grounded result
```

This separates semantic reasoning from deterministic computation.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Streamlit | Interactive web application |
| Pandas | Data transformation and analytics |
| Matplotlib | Data visualization |
| Google Gemini API | Dataset understanding and AI reasoning |
| python-dotenv | Environment variable management |

---

## Project Structure

```text
InsightFlow-AI/
|
|-- app.py
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- .env
|
|-- utils/
|   |-- ai_helper.py
|   |-- dashboard.py
|   |-- profiling.py
|   |-- query_engine.py
|   |-- transformations.py
|
|-- data/
|   |-- raw/
|
|-- venv/
```

### File Responsibilities

#### `app.py`

Main Streamlit application responsible for:

- File upload
- User interface
- Data transformation workflow
- Session-state management
- AI analysis orchestration
- Data analyst interface
- Executive summary interface
- Dashboard rendering workflow

#### `utils/profiling.py`

Responsible for:

- Data quality calculation
- Dataset metadata generation
- Column sample value extraction

#### `utils/transformations.py`

Responsible for:

- Missing value handling
- Data cleaning transformations

#### `utils/query_engine.py`

Responsible for:

- Natural language to Pandas query generation
- Query execution
- AI result explanation
- Dataset KPI discovery
- Batch KPI query generation
- KPI execution
- Executive summary generation

#### `utils/ai_helper.py`

Responsible for:

- AI visualization recommendations
- Structured chart configuration generation

#### `utils/dashboard.py`

Responsible for:

- Dynamic chart validation
- Chart generation
- Dashboard rendering

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Navigate to the Project Directory

```bash
cd InsightFlow-AI
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

On Windows:

```bash
venv\Scripts\activate
```

On macOS or Linux:

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the project root directory.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

The `.env` file must not be committed to source control.

Make sure `.gitignore` contains:

```text
.env
venv/
__pycache__/
*.pyc
```

---

## Running the Application

Run the Streamlit application:

```bash
streamlit run app.py
```

Streamlit will display a local application URL in the terminal.

Example:

```text
Local URL: http://localhost:8501
```

Open the displayed URL in a web browser.

---

## Application Workflow

### Step 1: Upload Dataset

Upload a CSV or Excel file.

### Step 2: Review Data Quality

The platform calculates:

- Number of rows
- Number of columns
- Data quality score

### Step 3: Transform Data

Apply optional transformations such as:

- Missing value handling
- Duplicate removal
- Column name standardization

### Step 4: Analyze Dataset

Click:

```text
Analyze Dataset
```

The platform:

1. Understands the dataset structure.
2. Identifies dimensions and metrics.
3. Detects date columns.
4. Discovers relevant KPIs.
5. Generates KPI calculations in a batch.
6. Executes the calculations locally using Pandas.
7. Stores the results in Streamlit session state.

### Step 5: Ask Business Questions

Enter a natural language question in the AI Data Analyst section.

The platform generates and executes an analytical Pandas expression.

### Step 6: Generate Executive Insights

Generate a business-focused executive summary based on the analytical results.

### Step 7: Generate Dashboard

Generate AI-recommended visualizations and use dashboard filters to explore the data.

---

## Example Use Cases

InsightFlow AI can be used to explore datasets related to:

### Sales Analytics

- Revenue analysis
- Profitability analysis
- Product performance
- Regional performance
- Customer analysis

### Inventory Analytics

- Stock analysis
- Inventory value
- Low-stock identification
- Product availability
- Inventory performance

### HR Analytics

- Employee analysis
- Salary analysis
- Department performance
- Employee tenure
- Performance metrics

### Operations Analytics

- Cost analysis
- Operational performance
- Process metrics
- Regional comparisons
- Efficiency analysis

The system is designed to adapt its analytical recommendations based on the uploaded dataset.

---

## Current Development Status

Implemented features:

- CSV and Excel upload
- Data quality scoring
- Missing value handling
- Duplicate removal
- Column name cleaning
- Transformed dataset export
- Dataset metadata generation
- AI dataset structure discovery
- Dimension identification
- Metric identification
- Date column identification
- Dynamic KPI discovery
- Batch KPI query generation
- Local Pandas KPI execution
- Natural language analytics
- AI result explanation
- Executive summary generation
- AI visualization recommendation
- Dynamic dashboard generation
- Dashboard filters
- Streamlit session-state caching
- AI API request optimization

---

## Planned Improvements

Future enhancements include:

- AST-based query validation
- Improved AI API retry and quota handling
- Additional visualization types
- Export executive summary as PDF
- Save analysis history
- Multi-dataset comparison
- Migration to the latest Google Gen AI SDK

---

## Security Considerations

InsightFlow AI currently executes AI-generated Pandas expressions in a restricted evaluation environment.

Potentially unsafe operations and keywords are blocked before query execution.

The current execution architecture is intended for local development and portfolio demonstration.

For a production deployment, generated expressions should be validated using a stronger mechanism such as:

- Python Abstract Syntax Tree validation
- Strict operation allowlisting
- Isolated execution environments
- Sandboxed analytical workers

The application should not be considered a secure arbitrary-code execution environment in its current development state.

---

## Project Goal

The goal of InsightFlow AI is to explore how generative AI can work alongside deterministic data-processing systems.

Instead of allowing a language model to directly answer analytical questions from incomplete dataset context, the platform uses AI for semantic reasoning and Pandas for actual computation.

The project demonstrates a practical hybrid analytics architecture:

```text
AI Reasoning
      +
Deterministic Data Processing
      =
Grounded Business Analytics
```

---

## Author

**Razan Mujawar**

B.Tech Computer Science Engineering  
Artificial Intelligence and Machine Learning

Focus Areas:

- Data Analytics
- Business Intelligence
- Generative AI
- AI-Powered Applications
- Business Analysis