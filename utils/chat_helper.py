import google.generativeai as genai
import re
import pandas as pd

def chat_with_dataset(
    metadata,
    question,
    relevant_data
):

    model = genai.GenerativeModel(
        "models/gemini-2.5-flash"
    )

    prompt = f"""
You are a Senior Data Analyst.

You are analyzing a dataframe.

The Relevant Dataset Records section contains
actual rows from the dataset.

Use ONLY these rows to answer the question.

If the answer exists in the rows,
provide it directly.

Do not say that data is unavailable unless
the rows are empty.

If the answer is not present in the provided data,
say:

"I could not find sufficient data to answer this question."

Dataset Metadata:

{metadata}

Relevant Dataset Records:

{relevant_data}

User Question:

{question}

Provide a concise and accurate answer.
Do not make assumptions.
Do not hallucinate.
"""

    response = model.generate_content(prompt)

    return response.text

def detect_query_type(question):
    question = question.lower()

    lookup_keywords = [
        "order id",
        "customer id",
        "customer name",
        "product id",
        "find",
        "lookup",
        "who is",
        "show me"
    ]

    for keyword in lookup_keywords:

        if keyword in question:
            return "lookup"

    return "analysis"


def find_matching_rows(df, question):

   identifier = extract_identifier(question)
   if identifier:

        matches = pd.DataFrame()

        for col in df.columns:

            temp = df[
                df[col]
                .astype(str)
                .str.contains(
                    identifier,
                    case=False,
                    na=False
                )
            ]

            matches = pd.concat(
                [matches, temp]
            )

        return matches.drop_duplicates()

def extract_identifier(question):

    patterns = [

        r'[A-Z]{2}-\d{4}-\d+',

        r'[A-Z]{2}-[A-Z]{2}-\d+'
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            question,
            re.IGNORECASE
        )

        if match:

            return match.group()

    return None