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