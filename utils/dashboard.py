import streamlit as st
import matplotlib.pyplot as plt

def render_dashboard(ai_charts, filtered_df):

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
        