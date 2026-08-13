# Chart Studio v2

A focused visualization studio for analysts who already have a final analytical table or series.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Workflow

1. Upload the final analytical table.
2. Choose the analytical purpose: Trend, Comparison, Composition, Relationship, or Distribution.
3. Choose or accept a chart.
4. Map columns.
5. Customize the presentation.
6. Preview.
7. Export.

## Important

Chart preview does not depend on Kaleido or Chrome.

Interactive HTML export is dependency-free.

PNG/SVG export is isolated. If the local environment lacks the renderer, the chart still works and the app remains usable.

## Included chart types

Bar, Horizontal Bar, Line, Area, Scatter, Pie, Donut, Histogram, Box Plot.
