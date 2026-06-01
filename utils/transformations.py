# -----------------------------
# HANDLE MISSING VALUES
# -----------------------------
from turtle import st


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
