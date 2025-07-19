import streamlit as st
import plotly.express as px
import pandas as pd

def generate_overview_charts(df, column_types):
    # --- Categorical columns ---
    for cat_col in column_types["categorical"]:
        st.markdown(f"#### 📊 Top Categories in `{cat_col}`")
        top_values = df[cat_col].value_counts().head(10).reset_index()
        top_values.columns = [cat_col, "Count"]
        fig = px.bar(top_values, x=cat_col, y="Count", color=cat_col,
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    labels={cat_col: cat_col, "Count": "Frequency"},
                    title=f"Top 10 Values in {cat_col}")
        fig.update_layout(margin=dict(t=50, b=40), height=400)
        st.plotly_chart(fig, use_container_width=True)

    # --- Numerical columns ---
    colors = px.colors.qualitative.Set3
    for idx, num_col in enumerate(column_types["numerical"]):
        st.markdown(f"#### 📈 Distribution of `{num_col}`")

        color = colors[idx % len(colors)]

        fig = px.histogram(df, x=num_col, nbins=20,
                        color_discrete_sequence=[color],
                        labels={num_col: num_col},
                        title=f"Distribution of {num_col}")
        fig.update_layout(margin=dict(t=50, b=40), height=400)
        st.plotly_chart(fig, use_container_width=True, key=f"num_{num_col}")

    # --- Time Series (if any datetime + one numerical) ---
    if column_types["datetime"] and column_types["numerical"]:
        for date_col in column_types["datetime"]:
            for value_col in column_types["numerical"]:
                try:
                    ts = df[[date_col, value_col]].dropna()
                    ts[date_col] = pd.to_datetime(ts[date_col])
                    agg = ts.groupby(date_col)[value_col].sum().reset_index()

                    st.markdown(f"#### ⏱️ Time Series: `{value_col}` over `{date_col}`")
                    fig = px.line(agg, x=date_col, y=value_col,
                                markers=True,
                                title=f"{value_col} Over Time ({date_col})",
                                labels={date_col: "Date", value_col: "Total"})
                    fig.update_traces(line=dict(color="#E26A6A", width=2))
                    fig.update_layout(margin=dict(t=50, b=40), height=400)
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass