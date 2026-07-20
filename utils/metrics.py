import math
import pandas as pd
import streamlit as st


def format_metric_value(kpi_name, value):
    """
    Formats KPI values for display in Streamlit metric cards.
    """

    if value is None:
        return "N/A"

    # Handle Pandas Series
    if isinstance(value, pd.Series):

        if len(value) == 1:
            value = value.iloc[0]
        else:
            return f"{len(value)} values"

    # Handle DataFrame
    if isinstance(value, pd.DataFrame):

        return f"{len(value)} rows"

    # Handle integers
    if isinstance(value, int):

        return f"{value:,}"

    # Handle floats
    if isinstance(value, float):

        if math.isnan(value):
            return "N/A"

        # Percentage KPIs
        if "margin" in kpi_name.lower() or "ratio" in kpi_name.lower():

            return f"{value:.2%}"

        # Normal float
        if value.is_integer():

            return f"{int(value):,}"

        return f"{value:,.2f}"

    # Everything else
    return str(value)

def render_kpi_cards(dynamic_kpis):
    """
    Displays KPI cards dynamically.
    """

    successful_kpis = []

    for kpi_name, details in dynamic_kpis.items():

        if details["status"] == "success":

            successful_kpis.append(
                (
                    kpi_name,
                    details["result"]
                )
            )

    if not successful_kpis:

        st.info("No KPI results available.")
        return

    columns = st.columns(4)

    for index, (kpi_name, value) in enumerate(successful_kpis):

        with columns[index % 4]:

            st.metric(
                label=kpi_name,
                value=format_metric_value(
                    kpi_name,
                    value
                )
            )