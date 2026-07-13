#utils/ profiling.py

def calculate_quality_score(df):

    total_cells = df.shape[0] * df.shape[1]

    missing_cells = df.isnull().sum().sum()

    duplicate_rows = df.duplicated().sum()

    duplicate_penalty = duplicate_rows * df.shape[1]

    quality_score = (
        1 - ((missing_cells + duplicate_penalty) / total_cells)
    ) * 100

    return round(quality_score, 2)


def generate_metadata(df, quality_score):
    sample_values = {}

    for col in df.columns:
        sample_values[col] = (
            df[col]
            .dropna()
            .astype(str)
            .unique()[:5]
            .tolist()
        )
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
        "quality_score": quality_score,
        "sample_values": sample_values
    }

    return metadata