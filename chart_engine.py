# Version 1 - Dynamic Reshaping, Auto-Aggregation & Advanced Styling Plotting Engine

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from chart_styles import PRESETS, format_number_value

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

def reshape_time_series(df, id_cols, value_cols, var_name="Period", value_name="Value", parse_dates=True):
    """Unpivots wide period/date columns into tidy long format."""
    if not value_cols:
        return df
    
    melted_df = pd.melt(
        df,
        id_vars=id_cols,
        value_vars=value_cols,
        var_name=var_name,
        value_name=value_name
    )
    
    if parse_dates:
        melted_df[var_name] = pd.to_datetime(melted_df[var_name], errors="ignore")
        
    return melted_df

def aggregate_data(df, group_col, value_cols, agg_func="Sum"):
    """Aggregates un-aggregated data rows before plotting."""
    if not group_col or not value_cols or not agg_func or agg_func == "None":
        return df
    
    func_map = {
        "Sum": "sum",
        "Average": "mean",
        "Mean": "mean",
        "Count": "count",
        "Max": "max",
        "Min": "min"
    }
    
    mapped_func = func_map.get(agg_func, "sum")
    valid_y = [c for c in value_cols if c in df.columns]
    
    if not valid_y:
        return df
        
    return df.groupby(group_col, as_index=False)[valid_y].agg(mapped_func)

def build_chart(df, chart_type, x_col, y_cols, label_col, title, subtitle,
                preset, show_labels, show_grid, show_legend, width, height, reference=0,
                agg_func=None, custom_colors=None, x_axis_angle=0, number_format="Raw",
                secondary_y_cols=None, font_family=None):
    
    # Apply optional auto-aggregation
    if agg_func and agg_func != "None" and x_col and y_cols and chart_type not in ["Histogram", "Box Plot"]:
        df = aggregate_data(df, group_col=x_col, value_cols=y_cols, agg_func=agg_func)

    style = PRESETS[preset]
    active_font = font_family if font_family else style["font"]
    secondary_y_cols = secondary_y_cols or []
    has_secondary = len(secondary_y_cols) > 0 and chart_type in ["Bar", "Line", "Area", "Scatter"]

    if has_secondary:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    else:
        fig = go.Figure()

    # Determine series colors
    colors = custom_colors if custom_colors else [style["accent"]]

    if chart_type in ["Bar", "Horizontal Bar"]:
        if not y_cols:
            raise ValueError("Select at least one numeric value.")
        horizontal = chart_type == "Horizontal Bar"
        for i, col in enumerate(y_cols):
            color = colors[i % len(colors)]
            text_vals = [format_number_value(v, number_format) for v in df[col]] if show_labels else None
            is_sec = col in secondary_y_cols
            
            trace = go.Bar(
                x=df[col] if horizontal else df[x_col],
                y=df[x_col] if horizontal else df[col],
                name=str(col),
                orientation="h" if horizontal else "v",
                text=text_vals,
                texttemplate="%{text}" if show_labels else None,
                textposition="outside",
                marker=dict(color=color),
            )
            if has_secondary:
                fig.add_trace(trace, secondary_y=is_sec)
            else:
                fig.add_trace(trace)

    elif chart_type in ["Line", "Area"]:
        if not y_cols:
            raise ValueError("Select at least one value series.")
        for i, col in enumerate(y_cols):
            color = colors[i % len(colors)]
            text_vals = [format_number_value(v, number_format) for v in df[col]] if show_labels else None
            is_sec = col in secondary_y_cols

            trace = go.Scatter(
                x=df[x_col],
                y=df[col],
                name=str(col),
                mode="lines+markers+text" if show_labels else "lines+markers",
                text=text_vals,
                textposition="top center",
                fill="tozeroy" if chart_type == "Area" else None,
                line=dict(width=style["line_width"], color=color),
                marker=dict(color=color),
            )
            if has_secondary:
                fig.add_trace(trace, secondary_y=is_sec)
            else:
                fig.add_trace(trace)

    elif chart_type == "Scatter":
        if not y_cols:
            raise ValueError("Select a numeric Y variable.")
        for i, col in enumerate(y_cols):
            color = colors[i % len(colors)]
            is_sec = col in secondary_y_cols

            trace = go.Scatter(
                x=df[x_col],
                y=df[col],
                mode="markers",
                name=str(col),
                marker=dict(size=style["marker_size"], color=color),
            )
            if has_secondary:
                fig.add_trace(trace, secondary_y=is_sec)
            else:
                fig.add_trace(trace)

    elif chart_type in ["Pie", "Donut"]:
        if not label_col or not y_cols:
            raise ValueError("Select categories and values.")
        fig.add_trace(go.Pie(
            labels=df[label_col],
            values=df[y_cols[0]],
            hole=0.52 if chart_type == "Donut" else 0,
            textinfo="label+percent" if show_labels else "percent",
            marker=dict(colors=colors if len(colors) > 1 else None),
        ))

    elif chart_type == "Histogram":
        fig.add_trace(go.Histogram(x=df[x_col], marker=dict(color=colors[0])))

    elif chart_type == "Box Plot":
        if not y_cols:
            raise ValueError("Select a numeric variable.")
        fig.add_trace(go.Box(
            y=df[y_cols[0]],
            name=str(y_cols[0]),
            boxmean=True,
            marker=dict(color=colors[0]),
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
        font=dict(family=active_font, size=style["font_size"]),
        margin=dict(l=75, r=35, t=95, b=70),
        bargap=0.25,
    )

    fig.update_xaxes(showgrid=show_grid, zeroline=False, tickangle=x_axis_angle)
    fig.update_yaxes(showgrid=show_grid, zeroline=False)

    return fig
