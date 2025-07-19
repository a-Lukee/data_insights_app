import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    # Remove leading/trailing whitespace in string data
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].astype(str).str.strip()

    # Try to convert columns to datetime if possible
    for col in df.columns:
        if "date" in col.lower() or "joined" in col.lower() or "start" in col.lower() or "end" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass

    # Drop duplicate rows
    df = df.drop_duplicates()

    return df
