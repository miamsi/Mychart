import io
import pandas as pd
import streamlit as st
from chart_engine import build_chart
from chart_styles import PRESETS
from exporters import chart_to_png, chart_to_svg

st.set_page_config(page_title="Chart Studio", page_icon="📊", layout="wide")

st.title("Chart Studio")
st.caption("Turn finished analytical tables into presentation-ready charts.")

if "df" not in st.session_state:
    st.session_state.df = None

with st.sidebar:
    st.header("1. Data")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

    if uploaded:
        try:
            if uploaded.name.lower().endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded)
            else:
                st.session_state.df = pd.read_excel(uploaded)
        except Exception as e:
            st.error(f"Could not read file: {e}")

    st.divider()
    st.header("2. Chart")
    chart_type = st.selectbox(
        "Type",
        ["Bar", "Horizontal Bar", "Line", "Area", "Scatter", "Pie", "Donut", "Histogram", "Box"],
    )
    preset = st.selectbox("Style preset", list(PRESETS))

df = st.session_state.df

if df is None:
    st.info("Upload your finished analytical table to begin.")
    st.code("""Month,Realisasi,Target
Jan,72,80
Feb,76,80
Mar,84,80
Apr,81,80""")
    st.stop()

st.subheader("Data preview")
st.dataframe(df.head(20), use_container_width=True)

numeric_cols = df.select_dtypes(include="number").columns.tolist()
all_cols = df.columns.tolist()

with st.sidebar:
    st.header("3. Data mapping")

    if chart_type in ["Pie", "Donut"]:
        label_col = st.selectbox("Category", all_cols)
        value_col = st.selectbox("Value", numeric_cols or all_cols)
        x_col = None
        y_cols = [value_col]
    elif chart_type == "Histogram":
        x_col = st.selectbox("Variable", numeric_cols or all_cols)
        y_cols = []
        label_col = None
    elif chart_type == "Box":
        y_col = st.selectbox("Variable", numeric_cols or all_cols)
        x_col = None
        y_cols = [y_col]
        label_col = None
    else:
        x_col = st.selectbox("X-axis", all_cols)
        y_options = numeric_cols or all_cols
        y_cols = st.multiselect(
            "Y-axis / series",
            y_options,
            default=y_options[:1],
        )
        label_col = None

    st.header("4. Presentation")
    title = st.text_input("Title", value=f"{chart_type} Chart")
    subtitle = st.text_input("Subtitle", value="")
    show_labels = st.checkbox("Data labels", value=True)
    show_grid = st.checkbox("Gridlines", value=False)
    legend = st.checkbox("Show legend", value=True)
    width = st.slider("Chart width", 600, 1800, 1100, 50)
    height = st.slider("Chart height", 350, 1000, 600, 25)

    st.header("5. Advanced")
    sort_values = st.checkbox("Sort by first Y series", value=False)
    top_n = st.number_input("Top N (0 = all)", min_value=0, value=0, step=1)

    if chart_type in ["Line", "Area", "Bar", "Horizontal Bar"]:
        reference = st.number_input("Reference line (0 = off)", value=0.0, step=1.0)
    else:
        reference = 0.0

try:
    chart_df = df.copy()

    if sort_values and y_cols:
        chart_df = chart_df.sort_values(y_cols[0], ascending=False)

    if top_n > 0 and chart_type not in ["Line", "Area", "Histogram", "Box"]:
        chart_df = chart_df.head(int(top_n))

    fig = build_chart(
        chart_df,
        chart_type=chart_type,
        x_col=x_col,
        y_cols=y_cols,
        label_col=label_col,
        title=title,
        subtitle=subtitle,
        preset=preset,
        show_labels=show_labels,
        show_grid=show_grid,
        show_legend=legend,
        width=width,
        height=height,
        reference=reference,
    )

    st.subheader("Preview")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        png = chart_to_png(fig)
        st.download_button(
            "Export PNG",
            data=png,
            file_name="chart.png",
            mime="image/png",
            use_container_width=True,
        )
    with c2:
        svg = chart_to_svg(fig)
        st.download_button(
            "Export SVG",
            data=svg,
            file_name="chart.svg",
            mime="image/svg+xml",
            use_container_width=True,
        )

except Exception as e:
    st.error(f"Chart could not be generated: {e}")
