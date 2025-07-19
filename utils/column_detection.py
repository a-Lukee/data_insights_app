from difflib import get_close_matches

def detect_column_types(df):
    return {
        "categorical": df.select_dtypes(include=["object", "category"]).columns.tolist(),
        "numerical": df.select_dtypes(include=["int64", "float64"]).columns.tolist(),
        "datetime": df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()
    }