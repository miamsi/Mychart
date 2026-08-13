import plotly.graph_objects as go
from plotly.subplots import make_subplots
from chart_styles import PRESETS

def build_chart(
    df, chart_type, x_col, y_cols, label_col, title, subtitle,
    preset, show_labels, show_grid, show_legend, width, height, reference=0
):
    style = PRESETS[preset]

    fig = go.Figure()

    if chart_type in ["Bar", "Horizontal Bar"]:
        orientation = "h" if chart_type == "Horizontal Bar" else "v"
        for col in y_cols:
            fig.add_trace(go.Bar(
                x=df[x_col] if orientation == "v" else df[col],
                y=df[col] if orientation == "v" else df[x_col],
                name=str(col),
                text=df[col] if show_labels else None,
                texttemplate="%{text}",
                textposition="outside",
                orientation=orientation,
                marker=dict(
                    color=style["accent"],
                    line=dict(width=0)
                ),
            ))

    elif chart_type in ["Line", "Area"]:
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
        if len(y_cols) < 1:
            raise ValueError("Select a numeric Y variable.")
        for col in y_cols:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                mode="markers+text" if show_labels else "markers",
                text=df[col] if show_labels else None,
                textposition="top center",
                name=str(col),
                marker=dict(size=style["marker_size"]),
            ))

    elif chart_type in ["Pie", "Donut"]:
        fig = go.Figure(go.Pie(
            labels=df[label_col],
            values=df[y_cols[0]],
            hole=0.52 if chart_type == "Donut" else 0,
            textinfo="label+percent" if show_labels else "percent",
        ))

    elif chart_type == "Histogram":
        fig.add_trace(go.Histogram(
            x=df[x_col],
            marker=dict(color=style["accent"]),
        ))

    elif chart_type == "Box":
        fig.add_trace(go.Box(
            y=df[y_cols[0]],
            name=str(y_cols[0]),
            boxmean=True,
            marker=dict(color=style["accent"]),
        ))

    if reference and chart_type in ["Line", "Area", "Bar", "Horizontal Bar"]:
        fig.add_hline(
            y=reference,
            line_dash="dash",
            annotation_text=f"Reference: {reference:g}",
        )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" + (f"<br><sup>{subtitle}</sup>" if subtitle else ""),
            x=0.02,
            xanchor="left",
        ),
        width=width,
        height=height,
        template=style["template"],
        showlegend=show_legend and chart_type not in ["Pie", "Donut", "Histogram", "Box"],
        font=dict(
            family=style["font"],
            size=style["font_size"],
        ),
        margin=dict(l=70, r=35, t=90, b=65),
        bargap=0.25,
    )

    fig.update_xaxes(showgrid=show_grid, zeroline=False)
    fig.update_yaxes(showgrid=show_grid, zeroline=False)

    return fig
