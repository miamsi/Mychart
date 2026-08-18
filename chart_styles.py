# Version 1 - Enhanced Styling Configurations & Formatters

import pandas as pd

PRESETS = {
    "Executive": {
        "template": "plotly_white",
        "font": "Arial",
        "font_size": 14,
        "line_width": 3,
        "marker_size": 10,
        "accent": "#1F4E79",
    },
    "Government Report": {
        "template": "simple_white",
        "font": "Arial",
        "font_size": 13,
        "line_width": 2.5,
        "marker_size": 8,
        "accent": "#2F5597",
    },
    "Academic": {
        "template": "simple_white",
        "font": "Times New Roman",
        "font_size": 13,
        "line_width": 2,
        "marker_size": 7,
        "accent": "#333333",
    },
    "Minimal": {
        "template": "plotly_white",
        "font": "Arial",
        "font_size": 12,
        "line_width": 2,
        "marker_size": 7,
        "accent": "#444444",
    },
}

AVAILABLE_FONTS = ["Arial", "Times New Roman", "Segoe UI", "Roboto", "Courier New", "Georgia"]

COLOR_PALETTES = {
    "Default Accent": None,
    "Ministry Blue": ["#1F4E79", "#2F5597", "#5B9BD5", "#41719C", "#9DC3E6"],
    "Corporate Teal": ["#005F73", "#0A9396", "#94D2BD", "#E9D8A6", "#EE9B00"],
    "High Contrast": ["#D90429", "#0077B6", "#2B2D42", "#8D99AE", "#FFB703"],
    "Emerald & Gold": ["#064E3B", "#047857", "#10B981", "#F59E0B", "#D97706"],
}

NUMBER_FORMATS = ["Raw", "IDR (Rp B/M/K)", "USD ($ B/M/K)", "Percentage (%)", "Compact (K/M/B/T)"]

def format_number_value(val, fmt_type="Raw"):
    """Formats numeric values for labels and axis presentation."""
    if val is None or pd.isna(val):
        return ""
    try:
        val = float(val)
    except (ValueError, TypeError):
        return str(val)

    if fmt_type == "Percentage (%)":
        return f"{val:.1f}%"
    
    prefix = ""
    if fmt_type == "IDR (Rp B/M/K)":
        prefix = "Rp "
    elif fmt_type == "USD ($ B/M/K)":
        prefix = "$"

    if fmt_type in ["IDR (Rp B/M/K)", "USD ($ B/M/K)", "Compact (K/M/B/T)"]:
        abs_val = abs(val)
        if abs_val >= 1e12:
            return f"{prefix}{val / 1e12:.2f}T"
        elif abs_val >= 1e9:
            return f"{prefix}{val / 1e9:.2f}B"
        elif abs_val >= 1e6:
            return f"{prefix}{val / 1e6:.2f}M"
        elif abs_val >= 1e3:
            return f"{prefix}{val / 1e3:.1f}K"
        else:
            return f"{prefix}{val:,.0f}"

    return f"{val:,.2f}".rstrip('0').rstrip('.')
