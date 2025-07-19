import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.column_detection import detect_column_types
from utils.data_cleaning import clean_data
from utils.charts import generate_overview_charts
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from utils.chart_suggester import suggest_chart_type
from pandas.api.types import is_numeric_dtype

import plotly.graph_objects as go


st.set_page_config(page_title="HR Data Insights", layout="wide")

# Top Title Bar
st.markdown("""
    <div style="background-color:#4F81BD;padding:1rem 2rem;border-radius:5px;margin-bottom:20px;">
        <h2 style="color:white;margin:0;">\U0001F4CA HR Data Insights Dashboard</h2>
    </div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("## \U0001F4C1 Navigation")
nav_option = {
    "Main Dashboard": "📊 Main Dashboard",
    "Customize Your Chart": "⚙️ Chart Customizer",
    "Build Your Own Chart": "📐 Chart Builder",
    "Waterfall Analysis":"📉 Waterfall Analysis",
    "About": "ℹ️ About"
}

selected_page = None
for key, label in nav_option.items():
    if st.sidebar.button(label):
        selected_page = key

if "current_page" not in st.session_state:
    st.session_state.current_page = "Main Dashboard"
if selected_page:
    st.session_state.current_page = selected_page

page = st.session_state.current_page

st.sidebar.markdown("---")

# File Upload
uploaded_file = st.sidebar.file_uploader("\U0001F4C4 Upload Excel or CSV File", type=["xlsx", "csv"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1]

    if file_type == "csv":
        df = pd.read_csv(uploaded_file)
    elif file_type == "xlsx":
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        selected_sheet = st.sidebar.selectbox("📚 Select a Sheet", sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
    else:
        st.error("Unsupported file format.")
        st.stop()

    df_clean = clean_data(df)
    column_types = detect_column_types(df_clean)

    if page == "Main Dashboard":
        st.success(f"✅ File loaded successfully! ({df.shape[0]} rows × {df.shape[1]} columns)")
        st.subheader("\U0001F50D Data Preview")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("\U0001F4CC Dataset Summary")
        st.markdown(f"- **Rows:** {df.shape[0]}")
        st.markdown(f"- **Columns:** {df.shape[1]}")
        summary = pd.DataFrame({
            "Column": df.columns,
            "Type": [df[col].dtype for col in df.columns],
            "Missing (%)": [round(df[col].isna().mean() * 100, 2) for col in df.columns]
        })
        st.dataframe(summary, use_container_width=True)

        st.subheader("\U0001F4C2 Column Type Summary")
        for dtype, cols in column_types.items():
            st.markdown(f"**{dtype.title()} Columns:** {', '.join(cols) if cols else '❌ None detected'}")

        st.subheader("\U0001F4C8 Initial Visual Insights")
        generate_overview_charts(df_clean, column_types)

    elif page == "Customize Your Chart":
        st.subheader("⚙️ Customize Your Charts")

        if column_types["categorical"]:
            selected_cat = st.multiselect("\U0001F4CA Categorical Columns to Visualize", column_types["categorical"])
            for col in selected_cat:
                st.markdown(f"#### `{col}` Value Counts")
                top_values = df_clean[col].value_counts().head(10).reset_index()
                top_values.columns = [col, "Count"]
                fig = px.bar(top_values, x=col, y="Count", color=col,
                             color_discrete_sequence=px.colors.qualitative.Pastel,
                             labels={col: col, "Count": "Frequency"},
                             title=f"Top 10 Values in {col}")
                fig.update_layout(margin=dict(t=50, b=40), height=400)
                st.plotly_chart(fig, use_container_width=True, key=f"cat_{col}")

        if column_types["numerical"]:
            selected_num = st.multiselect("\U0001F4C9 Numerical Columns to Visualize", column_types["numerical"])
            for col in selected_num:
                st.markdown(f"#### `{col}` Histogram")
                fig = px.histogram(df_clean, x=col, nbins=20,
                                   color_discrete_sequence=['#4F81BD'],
                                   labels={col: col},
                                   title=f"Distribution of {col}")
                fig.update_layout(margin=dict(t=50, b=40), height=400)
                st.plotly_chart(fig, use_container_width=True, key=f"num_{col}")

        if column_types["datetime"] and column_types["numerical"]:
            date_col = st.selectbox("\U0001F4C5 Choose Date Column", column_types["datetime"])
            value_col = st.selectbox("\U0001F4B0 Choose Numeric Column to Plot", column_types["numerical"])
            ts = df_clean[[date_col, value_col]].dropna()
            ts[date_col] = pd.to_datetime(ts[date_col])
            agg = ts.groupby(date_col)[value_col].sum().reset_index()
            fig = px.line(agg, x=date_col, y=value_col,
                          title=f"{value_col} Over Time ({date_col})",
                          markers=True)
            fig.update_traces(line=dict(color="#E26A6A", width=2))
            fig.update_layout(margin=dict(t=50, b=40), height=400)
            st.plotly_chart(fig, use_container_width=True)

    elif page == "Build Your Own Chart":
        st.subheader("🛠️ Build Your Own Chart")

        col1, col2, col3, col4 = st.columns(4)
        x_axis = col1.selectbox("X-Axis", df_clean.columns)
        y_axis = col2.multiselect("Y-Axis", ["None"] + list(df_clean.columns))
        color_by = col3.selectbox("Color By", ["None"] + column_types["categorical"])

        # Suggest chart type
        chart_type_suggestion = suggest_chart_type(df_clean, x_axis, y_axis if y_axis else None)
        st.markdown(f"\U0001F4A1 **Suggested Chart:** `{chart_type_suggestion}`")

        chart_options = ["Bar", "Histogram", "Scatter", "Line", "Pie", "Area", "Bubble", "Waterfall"]
        chart_type = col4.selectbox("Chart Type", chart_options, index=chart_options.index(chart_type_suggestion))

        fig = None
        if chart_type == "Bar":
            if y_axis != "None":
                data = df_clean.groupby(x_axis)[y_axis].sum().reset_index()
                fig = px.bar(data, x=x_axis, y=y_axis,
                             color=color_by if color_by != "None" else None,
                             title=f"Bar Chart: {y_axis} by {x_axis}")
            else:
                data = df_clean[x_axis].value_counts().reset_index()
                data.columns = [x_axis, "Count"]
                fig = px.bar(data, x=x_axis, y="Count",
                             color=color_by if color_by != "None" else None,
                             title=f"Bar Chart of {x_axis}")

        elif chart_type == "Histogram":
            fig = px.histogram(df_clean, x=x_axis,
                               color=color_by if color_by != "None" else None,
                               nbins=20,
                               title=f"Histogram of {x_axis}")

        elif chart_type == "Scatter" and y_axis != "None":
            if is_datetime(df_clean[x_axis]) or is_datetime(df_clean[y_axis]):
                st.warning("⚠️ Trendline not supported for datetime axes.")
                fig = px.scatter(df_clean, x=x_axis, y=y_axis,
                                 color=color_by if color_by != "None" else None,
                                 title=f"Scatter Plot: {y_axis} vs {x_axis}")
            else:
                fig = px.scatter(df_clean, x=x_axis, y=y_axis,
                                 color=color_by if color_by != "None" else None,
                                 trendline="ols",
                                 title=f"Scatter Plot: {y_axis} vs {x_axis}")

        elif chart_type == "Line" and y_axis != "None":
            fig = px.line(df_clean, x=x_axis, y=y_axis,
                          color=color_by if color_by != "None" else None,
                          title=f"Line Chart: {y_axis} over {x_axis}")

        elif chart_type == "Pie":
            pie_data = df_clean[x_axis].value_counts().reset_index()
            pie_data.columns = [x_axis, "Count"]
            fig = px.pie(pie_data, names=x_axis, values="Count",
                         title=f"Pie Chart of {x_axis}")

        elif chart_type == "Area" and y_axis != "None":
            fig = px.area(df_clean, x=x_axis, y=y_axis,
                          color=color_by if color_by != "None" else None,
                          title=f"Area Chart: {y_axis} over {x_axis}")

        elif chart_type == "Bubble":
            if isinstance(y_axis, list) or y_axis == "None":
                st.error("Bubble charts require a single numeric Y-axis column.")
            elif not is_numeric_dtype(df_clean[y_axis]):
                st.error("Y-axis must be numeric for bubble chart sizing.")
            else:
                fig = px.scatter(df_clean, x=x_axis, y=y_axis,
                                size=y_axis,
                                color=color_by if color_by != "None" else None,
                                title=f"Bubble Chart: {y_axis} vs {x_axis}")

        elif chart_type == "Waterfall" and y_axis != "None":
            data = df_clean.groupby(x_axis)[y_axis].sum().reset_index()
            fig = go.Figure(go.Waterfall(
                x=data[x_axis],
                y=data[y_axis],
                name="Waterfall Chart"
            ))
            fig.update_layout(title=f"Waterfall Chart: {y_axis} by {x_axis}")

        if fig:
            fig.update_layout(margin=dict(t=50, b=40), height=500)
            st.plotly_chart(fig, use_container_width=True)

    elif page == "Waterfall Analysis":
        st.subheader("📉 Waterfall Analysis")

        # Step 1: Choose grouping column (like "Period")
        group_col = st.selectbox("🧩 Select Grouping Column (Optional)", ["None"] + list(df_clean.columns))

        # Step 2: Select row if group is used
        if group_col != "None":
            selected_value = st.selectbox(f"🔍 Select a value from `{group_col}`", df_clean[group_col].dropna().unique())
            filtered_df = df_clean[df_clean[group_col] == selected_value]
        else:
            filtered_df = df_clean

        # Step 3: Let user select numeric columns as steps
        numeric_cols = [col for col in filtered_df.columns if is_numeric_dtype(filtered_df[col])]
        selected_cols = st.multiselect("📊 Select Numeric Columns for Waterfall Steps (in order)", numeric_cols)

        if selected_cols:
            # Step 4: Define measure types
            col1, col2 = st.columns([2, 1])
            col_order = col1.text_area("✏️ Step Labels (One per line)", "\n".join(selected_cols)).splitlines()
            measures = col2.multiselect("📏 Step Type (Match Order)", ["relative", "total"], default=["relative"] * len(selected_cols))

            if len(col_order) != len(selected_cols) or len(measures) != len(selected_cols):
                st.error("❗ Labels and Measures must match the number of selected columns.")
            else:
                values = [filtered_df[col].sum() for col in selected_cols]

                fig = go.Figure(go.Waterfall(
                    name="Dynamic Waterfall",
                    orientation="v",
                    measure=measures,
                    x=col_order,
                    y=values,
                    connector={"line": {"color": "gray"}}
                ))

                title_suffix = f" for `{selected_value}`" if group_col != "None" else ""
                fig.update_layout(
                    title=f"Waterfall Chart{title_suffix}",
                    showlegend=False,
                    height=500,
                    margin=dict(t=50, b=40)
                )

                st.plotly_chart(fig, use_container_width=True)

    elif page == "About":
        st.title("About This App")
        st.markdown("""
        **HR Data Insights Dashboard** is a Streamlit-based web application that enables users to upload, explore, and visualize HR datasets with ease.

        **Features:**
        - Automated data profiling
        - Smart chart recommendations
        - Customizable and build-your-own charts
        - Export cleaned data

        Developed with ❤️ using Python, Pandas, and Plotly.
        """)

    # Export
    st.sidebar.download_button("⬇️ Download Cleaned Data", data=df_clean.to_csv(index=False).encode('utf-8'), file_name="cleaned_data.csv", mime="text/csv")
