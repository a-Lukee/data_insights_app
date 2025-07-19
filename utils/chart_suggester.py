from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype as is_datetime

def suggest_chart_type(df, x_col, y_col=None):
    if isinstance(y_col, list):
        if not y_col:
            y_col = None
        else:
            y_col = y_col[0]

    if y_col is None or y_col not in df.columns:
        if df[x_col].dtype == "object" or df[x_col].nunique() < 20:
            return "Bar"
        elif is_numeric_dtype(df[x_col]):
            return "Histogram"
        else:
            return "Pie"

    elif is_datetime(df[x_col]) and is_numeric_dtype(df[y_col]):
        return "Line"
    elif is_numeric_dtype(df[x_col]) and is_numeric_dtype(df[y_col]):
        return "Scatter"
    elif df[x_col].dtype == "object" and is_numeric_dtype(df[y_col]):
        return "Bar"
    else:
        return "Bar"
