# -----------------------------
# DATA QUALITY CALCULATION
# -----------------------------
from turtle import st


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