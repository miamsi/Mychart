# Version 1 - Streamlit Main Application UI with Reshaping, Aggregation, and Styling Controls

import io
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from chart_engine import recommend_chart, build_chart, CHART_TYPES, reshape_time_series
from chart_styles import PRESETS, AVAILABLE_FONTS, COLOR_PALETTES, NUMBER_FORMATS

st.set_page_config(page_title="Chart Studio", page_icon="📊", layout="wide")

# ---------- Session ----------
if "df" not in st.session_state:
    st.session_state.df = None

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1500px;}
.small-muted {color:#6b7280; font-size:0.9rem;}
.section-title {font-size:1.05rem; font-weight:700; margin-top:0.5rem;}
div[data-testid="stMetric"] {background:#f7f7f8; padding:12px; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.title("Chart Studio")
st.caption("Turn your final analytical tables into polished, presentation-ready charts.")

# ---------- Top data area ----------
with st.container(border=True):
    c1, c2, c3 = st.columns([2.4, 1.2, 1.2])
    with c1:
        uploaded = st.file_uploader("Upload your final analytical table", type=["csv", "xlsx", "xls"])
    with c2:
        if st.session_state.df is not None:
            st.metric("Rows", f"{len(st.session_state.df):,}")
    with c3:
        if st.session_state.df is not None:
            st.metric("Columns", f"{len(st.session_state.df.columns):,}")

if uploaded:
    try:
        if uploaded.name.lower().endswith(".csv"):
            st.session_state.df = pd.read_csv(uploaded)
        else:
            st.session_state.df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Could not read the file: {e}")
        st.stop()

df = st.session_state.df

if df is None:
    st.info("Start by uploading the Excel/CSV containing your finished analytical result.")
    st.markdown("""
### Example

| Month | Realisasi | Target |
|---|---:|---:|
| January | 72 | 80 |
| February | 76 | 80 |
| March | 84 | 80 |
| April | 81 | 80 |

The app is designed for this stage of your workflow. **You do the analysis first. Chart Studio handles the visualization.**
""")
    st.stop()

# ---------- Tabs ----------
data_tab, design_tab, export_tab = st.tabs(["1 · Data", "2 · Design", "3 · Export"])

with data_tab:
    st.subheader("Your analytical table")
    st.caption("This is the data Chart Studio will visualize. It does not modify your source file.")
    
    with st.expander("Reshape Time Series Data (Wide-to-Long Unpivot)", expanded=False):
        st.caption("Use this tool if your periods/dates are spread across separate columns.")
        all_table_cols = df.columns.tolist()
        id_cols = st.multiselect("ID / Category Columns (Keep as identifiers)", all_table_cols)
        value_cols = st.multiselect("Period / Date Columns (To collapse into rows)", [c for c in all_table_cols if c not in id_cols])
        
        col_name_var = st.text_input("New Date/Period Column Name", value="Period")
        col_name_val = st.text_input("New Value Column Name", value="Value")
        parse_dates_flag = st.checkbox("Automatically parse dates", value=True)
        
        if st.button("Apply Reshape"):
            if value_cols:
                st.session_state.df = reshape_time_series(
                    df, id_cols=id_cols, value_cols=value_cols,
                    var_name=col_name_var, value_name=col_name_val, parse_dates=parse_dates_flag
                )
                st.rerun()

    st.dataframe(df, use_container_width=True, height=430)

with design_tab:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    all_cols = df.columns.tolist()

    recommended = recommend_chart(df)
    if "chart_type" not in st.session_state:
        st.session_state.chart_type = recommended

    left, center, right = st.columns([1.0, 2.2, 1.0], gap="large")

    with left:
        st.markdown("### What are you showing?")
        intent = st.radio(
            "Analytical purpose",
            ["Trend", "Comparison", "Composition", "Relationship", "Distribution"],
            label_visibility="collapsed",
        )

        intent_map = {
            "Trend": ["Line", "Area", "Bar"],
            "Comparison": ["Horizontal Bar", "Bar", "Line"],
            "Composition": ["Donut", "Pie", "Bar"],
            "Relationship": ["Scatter"],
            "Distribution": ["Histogram", "Box Plot"],
        }

        choices = intent_map[intent]
        chart_type = st.selectbox(
            "Chart",
            choices,
            index=choices.index(st.session_state.chart_type) if st.session_state.chart_type in choices else 0,
        )
        st.session_state.chart_type = chart_type

        st.divider()
        st.markdown("### Style")
        preset = st.selectbox("Preset", list(PRESETS))
        font_family = st.selectbox("Font Family", AVAILABLE_FONTS, index=0)
        number_format = st.selectbox("Number Format", NUMBER_FORMATS, index=0)
        selected_palette_name = st.selectbox("Color Palette", list(COLOR_PALETTES.keys()), index=0)
        x_axis_angle = st.slider("X-Axis Label Rotation (°)", min_value=0, max_value=90, value=0, step=15)

    with right:
        st.markdown("### Quick controls")
        title = st.text_input("Title", value="Analytical Result")
        subtitle = st.text_input("Subtitle", value="")
        show_labels = st.checkbox("Data labels", value=True)
        show_legend = st.checkbox("Legend", value=True)
        show_grid = st.checkbox("Gridlines", value=False)

        st.divider()
        st.markdown("### Size")
        width = st.slider("Width", 700, 1800, 1100, 50)
        height = st.slider("Height", 400, 1000, 620, 20)

    with center:
        st.markdown("### Build your chart")

        label_col = None
        x_col = None
        y_cols = []
        secondary_y_cols = []
        agg_func = "None"

        if chart_type in ["Donut", "Pie"]:
            label_col = st.selectbox("Categories", all_cols)
            value_col = st.selectbox("Values", numeric_cols or all_cols)
            y_cols = [value_col]

        elif chart_type == "Histogram":
            x_col = st.selectbox("Variable", numeric_cols or all_cols)

        elif chart_type == "Box Plot":
            x_col = st.selectbox("Variable", numeric_cols or all_cols)
            y_cols = [x_col]

        else:
            x_col = st.selectbox("X-axis", all_cols)
            available_y = [c for c in numeric_cols if c != x_col] or all_cols
            y_cols = st.multiselect(
                "Values / series",
                available_y,
                default=available_y[:2] if len(available_y) >= 2 else available_y[:1],
            )
            
            if chart_type in ["Bar", "Line", "Area", "Scatter"] and len(y_cols) > 1:
                secondary_y_cols = st.multiselect(
                    "Secondary Y-axis series (Right axis)",
                    y_cols,
                    default=[]
                )

        if chart_type not in ["Histogram", "Box Plot"]:
            agg_func = st.selectbox("Data Aggregation", ["None", "Sum", "Average", "Count", "Max", "Min"], index=0)

        if chart_type in ["Horizontal Bar", "Bar", "Line", "Area"]:
            with st.expander("Analysis helpers", expanded=False):
                sort_values = st.checkbox("Sort by first value", value=False)
                top_n = st.number_input("Show top N (0 = all)", min_value=0, value=0, step=1)
                reference = st.number_input("Reference line (0 = off)", value=0.0, step=1.0)
        else:
            sort_values = False
            top_n = 0
            reference = 0.0

        custom_colors = COLOR_PALETTES.get(selected_palette_name)
        if y_cols:
            with st.expander("Custom Series Colors (Override Palette)", expanded=False):
                override_colors = []
                for i, col in enumerate(y_cols):
                    default_hex = (
                        custom_colors[i % len(custom_colors)]
                        if custom_colors
                        else PRESETS[preset]["accent"]
                    )
                    chosen_hex = st.color_picker(f"Color for '{col}'", value=default_hex, key=f"color_{col}")
                    override_colors.append(chosen_hex)
                if override_colors:
                    custom_colors = override_colors

        chart_df = df.copy()
        if sort_values and y_cols:
            chart_df = chart_df.sort_values(y_cols[0], ascending=False)
        if top_n > 0 and chart_type in ["Horizontal Bar", "Bar"]:
            chart_df = chart_df.head(int(top_n))

        try:
            fig = build_chart(
                df=chart_df,
                chart_type=chart_type,
                x_col=x_col,
                y_cols=y_cols,
                label_col=label_col,
                title=title,
                subtitle=subtitle,
                preset=preset,
                show_labels=show_labels,
                show_grid=show_grid,
                show_legend=show_legend,
                width=width,
                height=height,
                reference=reference,
                agg_func=agg_func,
                custom_colors=custom_colors,
                x_axis_angle=x_axis_angle,
                number_format=number_format,
                secondary_y_cols=secondary_y_cols,
                font_family=font_family,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.session_state.current_fig = fig
        except Exception as e:
            st.warning(f"Set the required fields to preview the chart. ({e})")

with export_tab:
    st.subheader("Export")
    st.caption("Export is separate from preview. A missing export dependency will never break your chart.")

    fig = st.session_state.get("current_fig")
    if fig is None:
        st.info("Create a chart in the Design tab first.")
    else:
        st.success("Your chart is ready.")

        # Interactive HTML is dependency-free and always available.
        html = fig.to_html(include_plotlyjs="cdn", full_html=True)
        st.download_button(
            "Download interactive HTML",
            data=html,
            file_name="chart.html",
            mime="text/html",
            use_container_width=True,
        )

        st.markdown("#### Image export")
        st.caption("PNG/SVG export uses Plotly's renderer and may require a local rendering dependency. It is intentionally isolated from the chart preview.")

        try:
            png = fig.to_image(format="png", scale=2)
            st.download_button(
                "Download PNG",
                data=png,
                file_name="chart.png",
                mime="image/png",
                use_container_width=True,
            )
        except Exception:
            st.warning("PNG export is unavailable in this environment. The interactive chart still works normally.")

        try:
            svg = fig.to_image(format="svg")
            st.download_button(
                "Download SVG",
                data=svg,
                file_name="chart.svg",
                mime="image/svg+xml",
                use_container_width=True,
            )
        except Exception:
            st.warning("SVG export is unavailable in this environment. The interactive chart still works normally.")
