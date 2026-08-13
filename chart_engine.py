import pandas as pd
import plotly.graph_objects as go
from chart_styles import PRESETS

CHART_TYPES = [
    "Bar", "Horizontal Bar", "Line", "Area",
    "Scatter", "Pie", "Donut", "Histogram", "Box Plot"
]

def recommend_chart(df):
    numeric = df.select_dtypes(include="number").columns.tolist()
    cols = df.columns.tolist()

    if len(cols) >= 2:
        first = str(cols[0]).lower()
        if any(k in first for k in ["month", "date", "year", "quarter", "period", "week"]):
            return "Line"

    if len(numeric) == 1 and len(df) <= 15:
        return "Horizontal Bar"

    if len(numeric) >= 2 and len(df) >= 10:
        return "Scatter"

    if len(numeric) == 1:
        return "Histogram"

    return "Bar"

def build_chart(df, chart_type, x_col, y_cols, label_col, title, subtitle,
                preset, show_labels, show_grid, show_legend, width, height, reference=0):
    style = PRESETS[preset]
    fig = go.Figure()

    if chart_type in ["Bar", "Horizontal Bar"]:
        if not y_cols:
            raise ValueError("Select at least one numeric value.")
        horizontal = chart_type == "Horizontal Bar"
        for col in y_cols:
            fig.add_trace(go.Bar(
                x=df[col] if horizontal else df[x_col],
                y=df[x_col] if horizontal else df[col],
                name=str(col),
                orientation="h" if horizontal else "v",
                text=df[col] if show_labels else None,
                texttemplate="%{text}",
                textposition="outside",
                marker=dict(color=style["accent"]),
            ))

    elif chart_type in ["Line", "Area"]:
        if not y_cols:
            raise ValueError("Select at least one value series.")
        for col in y_cols:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                name=str(col),
                mode="lines+markers+text" if show_labels else "lines+markers",
                text=df[col] if show_labels else None,
                textposition="top center",
                fill="tozeroy" if chart_type == "Area" else None,
                line=dict(width=style["line_width"]),
            ))

    elif chart_type == "Scatter":
        if not y_cols:
            raise ValueError("Select a numeric Y variable.")
        for col in y_cols:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                mode="markers",
                name=str(col),
                marker=dict(size=style["marker_size"]),
            ))

    elif chart_type in ["Pie", "Donut"]:
        if not label_col or not y_cols:
            raise ValueError("Select categories and values.")
        fig.add_trace(go.Pie(
            labels=df[label_col],
            values=df[y_cols[0]],
            hole=0.52 if chart_type == "Donut" else 0,
            textinfo="label+percent" if show_labels else "percent",
        ))

    elif chart_type == "Histogram":
        fig.add_trace(go.Histogram(x=df[x_col], marker=dict(color=style["accent"])))

    elif chart_type == "Box Plot":
        if not y_cols:
            raise ValueError("Select a numeric variable.")
        fig.add_trace(go.Box(
            y=df[y_cols[0]],
            name=str(y_cols[0]),
            boxmean=True,
            marker=dict(color=style["accent"]),
        ))

    if reference and chart_type in ["Line", "Area", "Bar", "Horizontal Bar"]:
        fig.add_hline(y=reference, line_dash="dash",
                      annotation_text=f"Reference: {reference:g}")

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" + (f"<br><sup>{subtitle}</sup>" if subtitle else ""),
            x=0.02,
            xanchor="left",
        ),
        width=width,
        height=height,
        template=style["template"],
        showlegend=show_legend and chart_type not in ["Pie", "Donut", "Histogram", "Box Plot"],
        font=dict(family=style["font"], size=style["font_size"]),
        margin=dict(l=75, r=35, t=95, b=70),
        bargap=0.25,
    )
    fig.update_xaxes(showgrid=show_grid, zeroline=False)
    fig.update_yaxes(showgrid=show_grid, zeroline=False)
    return fig
