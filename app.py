"""
E-Commerce Sales & Customer Behavior Analytics
Streamlit dashboard | run from the project root with: streamlit run app.py

Expected files:
    data/processed/ecommerce_cleaned.csv     (required)
    data/processed/customer_segments.csv    (optional, used for RFM segments)
"""

import html
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CLEANED_PATH = PROCESSED_DIR / "ecommerce_cleaned.csv"
SEGMENTS_PATH = PROCESSED_DIR / "customer_segments.csv"

CURRENCY = ""  # e.g. "₹" or "$". Left empty because the dataset does not name a currency.


# ----------------------------------------------------------------------------
# Visual identity — Executive Indigo / Lavender
# ----------------------------------------------------------------------------

PRIMARY = "#586BC0"
LAVENDER = "#8C97E0"
INK = "#17224D"
MUTED = "#69739A"
GRID = "#E5E8F2"

FONT = "Inter, 'Segoe UI', system-ui, -apple-system, sans-serif"

PALETTE = [
    "#586BC0",
    "#8C97E0",
    "#B8C1ED",
    "#D9DDF7",
    "#3F4C8C",
    "#7180D0",
    "#AAB4E8",
    "#C8CEF2",
]

PLOT_CONFIG = {"displayModeBar": False}


# If auto-detection picks a wrong column, set it here.
# Keys:
# date, order_id, customer_id, revenue, category, city, state, country,
# device, delivery, rating, payment, gender, age_group, segment

COLUMN_OVERRIDES: dict = {}


# Possible names for each field.
# The first match found in your file is used.

ALIASES = {
    "date": [
        "order_date",
        "orderdate",
        "purchase_date",
        "order_datetime",
        "order_timestamp",
        "date",
        "timestamp",
    ],

    "order_id": [
        "order_id",
        "orderid",
        "transaction_id",
        "invoice_id",
        "invoice_no",
    ],

    "customer_id": [
        "customer_id",
        "customerid",
        "cust_id",
        "user_id",
        "client_id",
    ],

    "revenue": [
        "total_amount",
        "final_amount",
        "revenue",
        "total_price",
        "order_value",
        "order_total",
        "total_sales",
        "sales",
        "net_amount",
        "amount",
    ],

    "category": [
        "product_category",
        "category",
        "category_name",
        "item_category",
    ],

    "city": [
        "city",
        "customer_city",
        "shipping_city",
    ],

    "state": [
        "state",
        "region",
        "customer_state",
        "province",
    ],

    "country": [
        "country",
        "customer_country",
    ],

    "device": [
        "device_type",
        "device",
        "platform",
        "device_used",
        "order_device",
    ],

    "delivery": [
        "delivery_time_days",
        "delivery_days",
        "delivery_time",
        "delivery_duration",
        "days_to_deliver",
        "shipping_days",
    ],

    "rating": [
        "rating",
        "customer_rating",
        "review_rating",
        "review_score",
        "product_rating",
    ],

    "payment": [
        "payment_method",
        "payment_type",
        "payment_mode",
    ],

    "gender": [
        "gender",
        "customer_gender",
    ],

    "age_group": [
        "age_group",
        "customer_age_group",
        "age_band",
    ],

    "segment": [
        "customer_segment",
        "rfm_segment",
        "segment",
        "segment_name",
    ],
}


SEGMENT_FILE_ALIASES = {
    "customer_id": ALIASES["customer_id"],
    "segment": ALIASES["segment"],
    "recency": [
        "recency",
        "recency_days",
        "days_since_last_purchase",
    ],
    "frequency": [
        "frequency",
        "frequency_count",
        "order_count",
        "num_orders",
    ],
    "monetary": [
        "monetary",
        "monetary_value",
        "total_spent",
        "total_spend",
    ],
}


SEG_COL = "Customer Segment"


# ----------------------------------------------------------------------------
# Navigation
# ----------------------------------------------------------------------------

PAGES = [
    "Dashboard",
    "Product & Category",
    "Geography",
    "Customer Segments",
    "Customer Behavior",
    "Delivery & Ratings",
]

PAGE_ICONS = {
    "Dashboard": "dashboard",
    "Product & Category": "category",
    "Geography": "public",
    "Customer Segments": "groups",
    "Customer Behavior": "insights",
    "Delivery & Ratings": "local_shipping",
}


# ----------------------------------------------------------------------------
# Page setup + theme
# ----------------------------------------------------------------------------

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------------------------
# Executive Dashboard CSS
# ----------------------------------------------------------------------------

st.markdown(
    """
    <style>

    /* ============================================================
       EXECUTIVE DASHBOARD — INDIGO / LAVENDER THEME
       ============================================================ */


    /* ---------- Base ---------- */

    .stApp,
    .stApp p,
    .stApp label,
    .stApp li,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp button,
    .stApp input,
    .stApp textarea {
        font-family: Inter, 'Segoe UI', system-ui, -apple-system, sans-serif;
    }

    .stApp {
        background: #F5F6FA;
        color: #17224D;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer {
        display: none !important;
    }

    .block-container {
        max-width: 1600px;
        padding: 1.15rem 1.5rem 2.25rem 1.5rem;
    }

    h1,
    h2,
    h3 {
        color: #17224D;
    }

    [data-testid="stCaptionContainer"] {
        color: #69739A;
    }


    /* ============================================================
       HERO HEADER
       ============================================================ */

    .st-key-hero {
        background: #3F4C8C;
        border-radius: 20px;
        padding: 22px 26px 20px 26px;
        box-shadow: 0 8px 24px rgba(63, 76, 140, 0.16);
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        line-height: 1.08;
        color: #FFFFFF;
        margin: 0;
    }

    .hero-sub {
        font-size: 1.05rem;
        font-weight: 600;
        color: #E9ECFF;
        margin-top: 7px;
    }

    .hero-desc {
        font-size: 0.84rem;
        color: #C9D0F2;
        margin-top: 5px;
        line-height: 1.45;
    }

    .st-key-hero [data-baseweb="input"],
    .st-key-hero [data-baseweb="base-input"] {
        background: #FFFFFF !important;
        border-radius: 10px;
        border: 0 !important;
    }

    .st-key-hero input {
        color: #17224D !important;
        font-weight: 600;
    }

    .st-key-hero [data-testid="stDateInput"] svg {
        fill: #586BC0;
    }


    /* ---------- Sales / Orders toggle ---------- */

    .st-key-metric [role="radiogroup"] {
        gap: 6px;
        justify-content: flex-end;
        flex-wrap: nowrap;
    }

    .st-key-metric label {
        background: rgba(23, 34, 77, 0.34);
        border-radius: 10px;
        padding: 7px 18px;
        margin: 0;
        cursor: pointer;
        border: 1px solid rgba(255, 255, 255, 0.10);
    }

    .st-key-metric label > div:first-child {
        display: none;
    }

    .st-key-metric label p {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 0.88rem;
        margin: 0;
    }

    .st-key-metric label:has(input:checked) {
        background: #8C97E0;
        border-color: #8C97E0;
    }


    /* ============================================================
       SIDEBAR
       ============================================================ */

    section[data-testid="stSidebar"] {
        background: #3F4C8C;
        border-right: 0;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 0.65rem;
    }

    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #E9ECFF;
        font-size: 0.82rem;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #C9D0F2;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15);
    }


    /* ---------- Sidebar logo ---------- */

    .logo-box {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: #E9ECFF;
        color: #3F4C8C;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 4px 0 14px 4px;
    }

    .logo-box svg,
    .side-h svg {
        width: 23px;
        height: 23px;
        stroke: currentColor;
        fill: none;
        stroke-width: 1.8;
        stroke-linecap: round;
        stroke-linejoin: round;
    }


    /* ---------- Sidebar section heading ---------- */

    .side-h {
        display: flex;
        align-items: center;
        gap: 9px;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.78rem;
        letter-spacing: 0.09em;
        margin: 6px 0 5px 4px;
    }

    .side-h svg {
        width: 17px;
        height: 17px;
    }


    /* ---------- Navigation ---------- */

    .st-key-nav [role="radiogroup"] {
        gap: 3px;
        flex-direction: column;
        align-items: stretch;
    }

    .st-key-nav label {
        border-radius: 10px;
        padding: 9px 12px;
        margin: 0;
        cursor: pointer;
        width: 100%;
    }

    .st-key-nav label > div:first-child {
        display: none;
    }

    .st-key-nav label p {
        color: #E9ECFF;
        font-weight: 500;
        font-size: 0.90rem;
        margin: 0;
    }

    .st-key-nav label:hover {
        background: rgba(255, 255, 255, 0.08);
    }

    .st-key-nav label:has(input:checked) {
        background: #E9ECFF;
        box-shadow: 0 3px 10px rgba(23, 34, 77, 0.12);
    }

    .st-key-nav label:has(input:checked) p {
        color: #3F4C8C;
        font-weight: 700;
    }


    /* ---------- Sidebar filters ---------- */

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #FFFFFF;
        border: 0;
        border-radius: 9px;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #17224D;
    }

    section[data-testid="stSidebar"] span[data-baseweb="tag"] {
        background: #E9ECFF;
        border-radius: 7px;
    }

    section[data-testid="stSidebar"] span[data-baseweb="tag"] span {
        color: #3F4C8C !important;
    }


    /* ---------- Data check ---------- */

    section[data-testid="stSidebar"] [data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 10px;
        background: transparent;
    }

    section[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary span {
        color: #E9ECFF;
    }


    /* ---------- Download button ---------- */

    section[data-testid="stSidebar"] .stDownloadButton button {
        width: 100%;
        background: #586BC0;
        color: #FFFFFF;
        border: 0;
        border-radius: 10px;
        padding: 0.62rem 0.9rem;
        font-weight: 600;
    }

    section[data-testid="stSidebar"] .stDownloadButton button:hover {
        background: #7180D0;
        color: #FFFFFF;
    }

    section[data-testid="stSidebar"] .stDownloadButton button p {
        color: #FFFFFF;
    }


    /* ============================================================
       WHITE CONTENT CARDS
       ============================================================ */

    [class*="st-key-card_"] {
        background: #FFFFFF;
        border: 1px solid #E7E9F1;
        border-radius: 16px;
        padding: 16px 19px 13px 19px;
        box-shadow: 0 2px 8px rgba(23, 34, 77, 0.045);
        margin-bottom: 12px;
    }

    .card-title {
        display: flex;
        align-items: center;
        gap: 9px;
        font-size: 0.98rem;
        font-weight: 700;
        color: #17224D;
        margin-bottom: 2px;
    }

    .card-title .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #586BC0;
        display: inline-block;
    }


    /* ============================================================
       KPI CARDS
       ============================================================ */

    .kpi {
        position: relative;
        background: #FFFFFF;
        border: 1px solid #E7E9F1;
        border-radius: 15px;
        padding: 13px 14px 11px 14px;
        min-height: 101px;
        display: flex;
        gap: 10px;
        align-items: flex-start;
        box-shadow: 0 2px 8px rgba(23, 34, 77, 0.045);
    }

    .kpi-icon {
        flex: 0 0 40px;
        height: 40px;
        border-radius: 11px;
        background: #E9ECFF;
        color: #586BC0;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .kpi-icon svg {
        width: 21px;
        height: 21px;
        stroke: currentColor;
        fill: none;
        stroke-width: 1.7;
        stroke-linecap: round;
        stroke-linejoin: round;
    }

    .kpi-body {
        flex: 1;
        min-width: 0;
    }

    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #69739A;
    }

    .kpi-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #17224D;
        line-height: 1.15;
    }

    .kpi-note {
        position: absolute;
        left: 65px;
        bottom: 10px;
        font-size: 0.66rem;
        color: #8991B0;
    }

    .kpi-spark {
        position: absolute;
        right: 11px;
        bottom: 9px;
        line-height: 0;
    }


    /* ============================================================
       SERVICE SUMMARY TILES
       ============================================================ */

    .tiles {
        display: flex;
        gap: 10px;
        margin-top: 8px;
    }

    .tile {
        flex: 1;
        background: #E9ECFF;
        border-radius: 13px;
        padding: 11px 8px;
        text-align: center;
    }

    .tile-label {
        font-size: 0.72rem;
        color: #59658F;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }

    .tile-label svg {
        width: 14px;
        height: 14px;
        stroke: #586BC0;
        fill: none;
        stroke-width: 1.8;
        stroke-linecap: round;
        stroke-linejoin: round;
    }

    .tile-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #586BC0;
        line-height: 1.2;
    }

    .tile-unit {
        font-size: 0.76rem;
        color: #59658F;
        font-weight: 600;
    }


    /* ============================================================
       MAIN AREA CONTROLS
       ============================================================ */

    .block-container div[data-baseweb="select"] > div {
        background: #FFFFFF;
        border-color: #DDE1ED;
        border-radius: 9px;
    }

    [data-testid="stDataFrame"] {
        border-radius: 11px;
        overflow: hidden;
        border: 1px solid #E7E9F1;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------

_CARD_N = 0


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def resolve(
    df: pd.DataFrame,
    key: str,
    alias_map: dict,
    overrides: dict | None = None,
):
    """Return the real column name in df for a logical field, or None."""

    if overrides and overrides.get(key) in df.columns:
        return overrides[key]

    lookup = {_norm(col): col for col in df.columns}

    for candidate in alias_map.get(key, []):
        if _norm(candidate) in lookup:
            return lookup[_norm(candidate)]

    return None


def money(x: float) -> str:
    """Compact number for KPI cards."""

    if abs(x) >= 1_000_000:
        return f"{CURRENCY}{x / 1_000_000:,.2f}M"

    if abs(x) >= 1_000:
        return f"{CURRENCY}{x / 1_000:,.1f}K"

    return f"{CURRENCY}{x:,.0f}"


def card(title: str | None = None):
    """
    A rounded white card.

    Usage:
        with card("Title"):
            ...
    """

    global _CARD_N

    _CARD_N += 1

    try:
        box = st.container(key=f"card_{_CARD_N}")
    except TypeError:
        box = st.container(border=True)

    if title:
        with box:
            st.markdown(
                f'<div class="card-title">'
                f'<span class="dot"></span>'
                f'{html.escape(str(title))}'
                f'</div>',
                unsafe_allow_html=True,
            )

    return box


def style_fig(fig, height: int):
    """Shared clean Plotly look."""

    fig.update_layout(
        height=height,
        title=None,
        margin=dict(l=45, r=15, t=10, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family=FONT,
            size=12,
            color="#3B3F63",
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=12,
            font_family=FONT,
        ),
        legend_title_text=None,
    )

    if fig.layout.legend.orientation is None:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.12,
                xanchor="center",
                x=0.5,
                font_size=11,
            )
        )

    horizontal = any(
        getattr(t, "orientation", None) == "h"
        for t in fig.data
    )

    fig.update_xaxes(
        showgrid=horizontal,
        gridcolor=GRID,
        zeroline=False,
        linecolor="#E3E4F0",
        ticks="",
        title_font_size=11,
    )

    fig.update_yaxes(
        showgrid=not horizontal,
        gridcolor=GRID,
        zeroline=False,
        linecolor="rgba(0,0,0,0)",
        ticks="",
        title_font_size=11,
    )

    return fig


def show_chart(fig, height: int = 340):
    style_fig(fig, height)

    try:
        st.plotly_chart(
            fig,
            theme=None,
            width="stretch",
            config=PLOT_CONFIG,
        )
    except TypeError:
        st.plotly_chart(
            fig,
            theme=None,
            use_container_width=True,
            config=PLOT_CONFIG,
        )


def chart_card(
    title: str,
    fig,
    height: int = 340,
    note: str | None = None,
):
    with card(title):
        show_chart(fig, height)

        if note:
            st.caption(note)


def show_table(
    df: pd.DataFrame,
    formats: dict | None = None,
):
    data = df.style.format(
        {
            k: v
            for k, v in (formats or {}).items()
            if k in df.columns
        }
    )

    try:
        st.dataframe(
            data,
            hide_index=True,
            width="stretch",
        )
    except TypeError:
        st.dataframe(
            data,
            hide_index=True,
            use_container_width=True,
        )


def donut(
    data: pd.DataFrame,
    names: str,
    values: str,
    center_value: str,
    center_label: str,
):
    fig = px.pie(
        data,
        names=names,
        values=values,
        hole=0.62,
        color_discrete_sequence=PALETTE,
    )

    fig.update_traces(
        domain=dict(x=[0, 0.6]),
        sort=False,
        textinfo="percent",
        textposition="inside",
        marker=dict(
            line=dict(
                color="#FFFFFF",
                width=2,
            )
        ),
    )

    fig.update_layout(
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=0.66,
            font_size=12,
        )
    )

    fig.add_annotation(
        text=(
            f"<b>{html.escape(center_value)}</b><br>"
            f"<span style='font-size:11px;color:{MUTED}'>"
            f"{html.escape(center_label)}"
            f"</span>"
        ),
        x=0.3,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
        font=dict(
            size=20,
            color=INK,
            family=FONT,
        ),
    )

    return fig


# ----------------------------------------------------------------------------
# KPI card pieces
# ----------------------------------------------------------------------------

ICONS = {
    "revenue": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M14.5 9.2a2.6 2.6 0 0 0-2.5-1.4'
        'c-1.4 0-2.5.8-2.5 2s1 1.7 2.5 2.1'
        ' 2.5.8 2.5 2-1.1 2-2.5 2a2.6 2.6 0 0 1-2.5-1.4'
        'M12 6v1.8M12 16.2V18"/>'
    ),

    "orders": (
        '<path d="M6 7h12l1 13H5L6 7z"/>'
        '<path d="M9 10V6a3 3 0 0 1 6 0v4"/>'
    ),

    "customers": (
        '<circle cx="9" cy="8" r="3.5"/>'
        '<path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/>'
        '<circle cx="17" cy="9" r="2.5"/>'
        '<path d="M17 14c2.6 0 4.5 1.8 4.5 4.5"/>'
    ),

    "aov": (
        '<path d="M3 12V4h8l10 10-8 8L3 12z"/>'
        '<circle cx="7.5" cy="8.5" r="1.2"/>'
    ),

    "repeat": (
        '<path d="M20 11a8 8 0 0 0-14-4L4 9'
        'M4 4v5h5M4 13a8 8 0 0 0 14 4l2-2'
        'M20 20v-5h-5"/>'
    ),

    "truck": (
        '<path d="M2 6h11v10H2zM13 9h4l3 3v4h-7"/>'
        '<circle cx="6.5" cy="17.5" r="1.7"/>'
        '<circle cx="16.5" cy="17.5" r="1.7"/>'
    ),

    "star": (
        '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3'
        ' 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3'
        ' 6.1-.9z"/>'
    ),
}


def svg_icon(name: str) -> str:
    return f'<svg viewBox="0 0 24 24">{ICONS[name]}</svg>'


def sparkline(
    values,
    color: str = PRIMARY,
    w: int = 96,
    h: int = 34,
) -> str:
    """Tiny inline SVG trend line built from real monthly values."""

    v = [
        float(x)
        for x in values
        if pd.notna(x)
    ]

    if len(v) < 2:
        return ""

    lo = min(v)
    hi = max(v)
    span = (hi - lo) or 1.0
    pad = 3

    pts = [
        (
            pad + i * (w - 2 * pad) / (len(v) - 1),
            pad + (h - 2 * pad) * (1 - (x - lo) / span),
        )
        for i, x in enumerate(v)
    ]

    line = " ".join(
        f"{x:.1f},{y:.1f}"
        for x, y in pts
    )

    area = (
        f"{pts[0][0]:.1f},{h} "
        f"{line} "
        f"{pts[-1][0]:.1f},{h}"
    )

    return (
        f'<svg width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<polygon points="{area}" '
        f'fill="{color}" fill-opacity="0.10"/>'
        f'<polyline points="{line}" fill="none" '
        f'stroke="{color}" stroke-width="2" '
        f'stroke-linejoin="round" '
        f'stroke-linecap="round"/>'
        f'</svg>'
    )


def kpi_card(
    icon: str,
    label: str,
    value: str,
    series=None,
    help_text: str = "",
) -> str:

    spark = (
        sparkline(series)
        if series is not None
        else ""
    )

    note = (
        "Monthly trend"
        if spark
        else "Selected period"
    )

    value = html.escape(value).replace(
        "$",
        "&#36;",
    )

    return (
        f'<div class="kpi" '
        f'title="{html.escape(help_text)}">'
        f'<div class="kpi-icon">'
        f'{svg_icon(icon)}'
        f'</div>'
        f'<div class="kpi-body">'
        f'<div class="kpi-label">'
        f'{html.escape(label)}'
        f'</div>'
        f'<div class="kpi-value">'
        f'{value}'
        f'</div>'
        f'</div>'
        f'<div class="kpi-note">'
        f'{note}'
        f'</div>'
        f'<div class="kpi-spark">'
        f'{spark}'
        f'</div>'
        f'</div>'
    )


def tile(
    icon: str,
    label: str,
    value: str,
    unit: str = "",
) -> str:

    unit_html = (
        f'<div class="tile-unit">'
        f'{html.escape(unit)}'
        f'</div>'
        if unit
        else ""
    )

    return (
        f'<div class="tile">'
        f'<div class="tile-label">'
        f'{svg_icon(icon)}'
        f'{html.escape(label)}'
        f'</div>'
        f'<div class="tile-value">'
        f'{html.escape(value)}'
        f'</div>'
        f'{unit_html}'
        f'</div>'
    )


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------

@st.cache_data(show_spinner="Loading data...")
def load_data():

    if not CLEANED_PATH.exists():
        return None, None, None, None

    df = pd.read_csv(CLEANED_PATH)

    cols = {
        key: resolve(
            df,
            key,
            ALIASES,
            COLUMN_OVERRIDES,
        )
        for key in ALIASES
    }

    needed = (
        "date",
        "revenue",
        "customer_id",
    )

    if any(cols[k] is None for k in needed):
        return df, cols, None, None

    # Types
    df[cols["date"]] = pd.to_datetime(
        df[cols["date"]],
        errors="coerce",
    )

    df[cols["revenue"]] = pd.to_numeric(
        df[cols["revenue"]],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            cols["date"],
            cols["revenue"],
        ]
    ).copy()

    df[cols["customer_id"]] = (
        df[cols["customer_id"]]
        .astype(str)
    )

    # If there is no order id column,
    # treat each row as one order.
    if cols["order_id"] is None:

        df["__order_id"] = range(len(df))

        cols["order_id"] = "__order_id"

    # ------------------------------------------------------------
    # RFM segment file — optional
    # ------------------------------------------------------------

    seg_std = None

    if SEGMENTS_PATH.exists():

        seg_raw = pd.read_csv(
            SEGMENTS_PATH
        )

        sc = {
            key: resolve(
                seg_raw,
                key,
                SEGMENT_FILE_ALIASES,
            )
            for key in SEGMENT_FILE_ALIASES
        }

        if sc["customer_id"]:

            key = cols["customer_id"]

            seg_std = pd.DataFrame(
                {
                    key: seg_raw[
                        sc["customer_id"]
                    ].astype(str)
                }
            )

            for std_name, field in (
                (
                    SEG_COL,
                    "segment",
                ),
                (
                    "Recency",
                    "recency",
                ),
                (
                    "Frequency",
                    "frequency",
                ),
                (
                    "Monetary",
                    "monetary",
                ),
            ):

                if sc[field]:
                    seg_std[std_name] = (
                        seg_raw[sc[field]]
                    )

            seg_std = seg_std.drop_duplicates(
                key
            )

    # Make sure main table has segment column
    if (
        cols["segment"] is None
        and seg_std is not None
        and SEG_COL in seg_std.columns
    ):

        df = df.merge(
            seg_std[
                [
                    cols["customer_id"],
                    SEG_COL,
                ]
            ],
            on=cols["customer_id"],
            how="left",
        )

        df[SEG_COL] = (
            df[SEG_COL]
            .fillna("Unassigned")
        )

        cols["segment"] = SEG_COL

    elif (
        cols["segment"] is not None
        and seg_std is not None
        and SEG_COL not in seg_std.columns
    ):

        mapping = (
            df.drop_duplicates(
                cols["customer_id"]
            )
            .set_index(
                cols["customer_id"]
            )[cols["segment"]]
        )

        seg_std[SEG_COL] = (
            seg_std[cols["customer_id"]]
            .map(mapping)
        )

    return df, cols, seg_std, True


# ----------------------------------------------------------------------------
# Summaries
# ----------------------------------------------------------------------------

def summarize(
    d: pd.DataFrame,
    c: dict,
    by: str,
) -> pd.DataFrame:

    """
    Revenue, orders, customers, AOV
    plus rating/delivery if available.
    """

    g = d.groupby(by).agg(
        Revenue=(
            c["revenue"],
            "sum",
        ),
        Orders=(
            c["order_id"],
            "nunique",
        ),
        Customers=(
            c["customer_id"],
            "nunique",
        ),
    )

    g["AOV"] = (
        g["Revenue"]
        / g["Orders"]
    )

    if c["rating"]:
        g["Avg Rating"] = (
            d.groupby(by)[c["rating"]]
            .mean()
        )

    if c["delivery"]:
        g["Avg Delivery (days)"] = (
            d.groupby(by)[c["delivery"]]
            .mean()
        )

    return (
        g.reset_index()
        .sort_values(
            "Revenue",
            ascending=False,
        )
    )


TABLE_FORMATS = {
    "Revenue": "{:,.0f}",
    "Orders": "{:,.0f}",
    "Customers": "{:,.0f}",
    "AOV": "{:,.2f}",
    "Avg Rating": "{:.2f}",
    "Avg Delivery (days)": "{:.2f}",
    "Revenue Share %": "{:.1f}",
    "Recency": "{:,.1f}",
    "Frequency": "{:,.1f}",
    "Monetary": "{:,.0f}",
}


# ----------------------------------------------------------------------------
# Load + validate
# ----------------------------------------------------------------------------

df, c, seg_std, ok = load_data()


if df is None:

    st.error(
        f"Could not find "
        f"`{CLEANED_PATH.relative_to(BASE_DIR)}`. "
        "Run `streamlit run app.py` from the project root, "
        "where the `data/` folder is."
    )

    st.stop()


if not ok:

    missing = [
        k
        for k in (
            "date",
            "revenue",
            "customer_id",
        )
        if c[k] is None
    ]

    st.error(
        "Could not detect these columns: "
        + ", ".join(missing)
        + "."
    )

    st.write(
        "Columns found in the file:",
        list(df.columns),
    )

    st.info(
        "Set the right names in "
        "`COLUMN_OVERRIDES` at the top of `app.py`."
    )

    st.stop()


# ----------------------------------------------------------------------------
# Header banner
# ----------------------------------------------------------------------------

date_min = (
    df[c["date"]]
    .min()
    .date()
)

date_max = (
    df[c["date"]]
    .max()
    .date()
)


with st.container(key="hero"):

    hero_left, hero_right = st.columns(
        [3, 1.6],
        vertical_alignment="top",
    )

    with hero_right:

        date_range = st.date_input(
            "Order date",
            value=(
                date_min,
                date_max,
            ),
            min_value=date_min,
            max_value=date_max,
            label_visibility="collapsed",
        )

        metric_choice = st.radio(
            "Metric",
            [
                "Sales",
                "Orders",
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="metric",
        )


if (
    isinstance(date_range, (tuple, list))
    and len(date_range) == 2
):

    start, end = date_range

else:

    start, end = (
        date_min,
        date_max,
    )


METRIC = (
    "Revenue"
    if metric_choice == "Sales"
    else "Orders"
)


with hero_left:

    st.markdown(
        '<div class="hero-title">'
        'E-Commerce Analytics'
        '</div>'

        '<div class="hero-sub">'
        'Executive Sales &amp; Customer Insights'
        '</div>'

        '<div class="hero-desc">'
        'A comprehensive analysis of sales performance, '
        'customer behavior, product categories, geography '
        'and service quality.<br>'
        f'Showing {start:%d %b %Y} '
        f'to {end:%d %b %Y}'
        '</div>',

        unsafe_allow_html=True,
    )


d = df[
    (
        df[c["date"]]
        .dt.date
        >= start
    )
    &
    (
        df[c["date"]]
        .dt.date
        <= end
    )
]


# ----------------------------------------------------------------------------
# Sidebar: logo, navigation, filters
# ----------------------------------------------------------------------------

st.sidebar.markdown(
    '<div class="logo-box">'
    '<svg viewBox="0 0 24 24">'
    '<circle cx="9" cy="20" r="1.5"/>'
    '<circle cx="18" cy="20" r="1.5"/>'
    '<path d="M2 3h3l2.5 12.5h11L21 7H6"/>'
    '</svg>'
    '</div>',
    unsafe_allow_html=True,
)


page = st.sidebar.radio(
    "Navigation",
    PAGES,
    key="nav",
    label_visibility="collapsed",
    format_func=lambda p:
        f":material/{PAGE_ICONS[p]}: {p}",
)


st.sidebar.divider()


st.sidebar.markdown(
    '<div class="side-h">'
    '<svg viewBox="0 0 24 24">'
    '<path d="M3 4h18l-7 8.5V19l-4 2v-8.5L3 4z"/>'
    '</svg>'
    'FILTERS'
    '</div>',
    unsafe_allow_html=True,
)


def multiselect_filter(
    frame: pd.DataFrame,
    field: str,
    label: str,
) -> pd.DataFrame:

    col = c[field]

    if not col:
        return frame

    options = sorted(
        df[col]
        .dropna()
        .astype(str)
        .unique()
    )

    chosen = st.sidebar.multiselect(
        label,
        options,
        placeholder="All",
    )

    if chosen:

        return frame[
            frame[col]
            .astype(str)
            .isin(chosen)
        ]

    return frame


d = multiselect_filter(
    d,
    "category",
    "Product category",
)

d = multiselect_filter(
    d,
    "city",
    "City",
)

d = multiselect_filter(
    d,
    "device",
    "Device",
)

d = multiselect_filter(
    d,
    "segment",
    "Customer segment",
)


if d.empty:

    st.warning(
        "No data matches the current filters. "
        "Try widening them."
    )

    st.stop()


st.sidebar.caption(
    f"{len(d):,} of {len(df):,} orders selected"
)


st.sidebar.download_button(
    "Download filtered data",
    d.to_csv(index=False).encode("utf-8"),
    file_name="filtered_orders.csv",
    mime="text/csv",
)


with st.sidebar.expander("Data check"):

    st.caption(
        "Columns detected for each field:"
    )

    st.json(
        {
            k: v
            for k, v in c.items()
            if v and v != "__order_id"
        }
    )

    st.caption(
        "Total revenue (all rows): "
        f"{df[c['revenue']].sum():,.2f}"
    )


# ----------------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------------

revenue = d[c["revenue"]].sum()

orders = d[c["order_id"]].nunique()

customers = d[c["customer_id"]].nunique()

aov = (
    revenue / orders
    if orders
    else 0
)


orders_per_customer = (
    d.groupby(
        c["customer_id"]
    )[c["order_id"]]
    .nunique()
)


repeat_rate = (
    (orders_per_customer > 1).mean()
    * 100
    if customers
    else 0
)


d_month = d.assign(
    Month=(
        d[c["date"]]
        .dt.to_period("M")
        .dt.to_timestamp()
    )
)


monthly = (
    d_month
    .groupby("Month")
    .agg(
        Revenue=(
            c["revenue"],
            "sum",
        ),
        Orders=(
            c["order_id"],
            "nunique",
        ),
        Customers=(
            c["customer_id"],
            "nunique",
        ),
    )
    .reset_index()
)


monthly["AOV"] = (
    monthly["Revenue"]
    / monthly["Orders"]
)


_repeat_by_month = (
    d_month
    .groupby(
        [
            "Month",
            c["customer_id"],
        ]
    )[c["order_id"]]
    .nunique()
    .groupby(level="Month")
    .apply(
        lambda s:
            (s > 1).mean() * 100
    )
)


monthly["Repeat"] = (
    monthly["Month"]
    .map(_repeat_by_month)
)


# ----------------------------------------------------------------------------
# KPI row
# ----------------------------------------------------------------------------

kpis = st.columns(5)


kpis[0].markdown(
    kpi_card(
        "revenue",
        "Total Revenue",
        money(revenue),
        monthly["Revenue"],
        f"{revenue:,.2f}",
    ),
    unsafe_allow_html=True,
)


kpis[1].markdown(
    kpi_card(
        "orders",
        "Total Orders",
        f"{orders:,}",
        monthly["Orders"],
    ),
    unsafe_allow_html=True,
)


kpis[2].markdown(
    kpi_card(
        "customers",
        "Customers",
        f"{customers:,}",
        monthly["Customers"],
        "Unique customers per month in the sparkline",
    ),
    unsafe_allow_html=True,
)


kpis[3].markdown(
    kpi_card(
        "aov",
        "Avg Order Value",
        f"{CURRENCY}{aov:,.2f}",
        monthly["AOV"],
    ),
    unsafe_allow_html=True,
)


kpis[4].markdown(
    kpi_card(
        "repeat",
        "Repeat Customer Rate",
        f"{repeat_rate:.2f}%",
        monthly["Repeat"],
        (
            "Share of customers with more than one "
            "order in the selected data. "
            "The sparkline applies the same definition "
            "within each month."
        ),
    ),
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Service tiles
# ----------------------------------------------------------------------------

def service_tiles() -> str:

    items = []

    if c["delivery"]:

        items.append(
            tile(
                "truck",
                "Avg Delivery Time",
                f"{d[c['delivery']].mean():.2f}",
                "days",
            )
        )

    if c["rating"]:

        items.append(
            tile(
                "star",
                "Average Rating",
                f"{d[c['rating']].mean():.2f}",
            )
        )

    if items:

        return (
            '<div class="tiles">'
            + "".join(items)
            + "</div>"
        )

    return ""


# ----------------------------------------------------------------------------
# Segment table
# ----------------------------------------------------------------------------

def segment_table(
    frame: pd.DataFrame,
) -> pd.DataFrame:

    seg_col = c["segment"]

    seg = (
        frame
        .groupby(seg_col)
        .agg(
            Customers=(
                c["customer_id"],
                "nunique",
            ),
            Orders=(
                c["order_id"],
                "nunique",
            ),
            Revenue=(
                c["revenue"],
                "sum",
            ),
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False,
        )
    )

    seg["Revenue Share %"] = (
        seg["Revenue"]
        / seg["Revenue"].sum()
        * 100
    )

    return seg


# ----------------------------------------------------------------------------
# Axis helper
# ----------------------------------------------------------------------------

def si_axis(
    fig,
    axis: str = "y",
):
    """
    Compact number ticks
    e.g. 1.6M, 800k.
    """

    (
        fig.update_yaxes
        if axis == "y"
        else fig.update_xaxes
    )(
        tickformat="~s"
    )


# ============================================================================
# PAGES
# ============================================================================


# ----------------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------------

if page == "Dashboard":

    # --------------------------------------------------------
    # Top charts
    # --------------------------------------------------------

    left, right = st.columns(2)


    with left:

        fig = px.line(
            monthly,
            x="Month",
            y="Revenue",
            markers=True,
        )

        fig.update_traces(
            line_color=PRIMARY,
            fill="tozeroy",
            fillcolor="rgba(88,107,192,0.10)",
            marker=dict(size=6),
        )

        fig.update_layout(
            yaxis_title=None,
            xaxis_title=None,
        )
        fig.update_xaxes(
            showticklabels=True,
            dtick="M1",
            tickformat="%b %Y",
            tickangle=-45,
            automargin=True,
        )
        si_axis(
            fig,
            "y",
        )

        best = monthly.loc[
            monthly["Revenue"].idxmax()
        ]

        chart_card(
            "Revenue Trend Over Time",
            fig,
            height=300,
            note=(
                f"Best month: "
                f"**{best['Month']:%B %Y}** "
                f"with "
                f"{CURRENCY}"
                f"{best['Revenue']:,.0f} "
                f"in revenue."
            ),
        )


    with right:

        fig = px.bar(
            monthly,
            x="Month",
            y="Orders",
        )

        fig.update_traces(
            marker_color=LAVENDER
        )

        fig.update_layout(
            yaxis_title=None,
            xaxis_title=None,
        )
        fig.update_xaxes(
            showticklabels=True,
            dtick="M1",
            tickformat="%b %Y",
            tickangle=-45,
            automargin=True,
)
        chart_card(
            "Monthly Orders",
            fig,
            height=300,
        )


    # --------------------------------------------------------
    # Category + Geography
    # --------------------------------------------------------

    left, right = st.columns(2)


    with left:

        if c["category"]:

            cat = summarize(
                d,
                c,
                c["category"],
            )

            share = cat[
                [
                    c["category"],
                    "Revenue",
                ]
            ].copy()

            share[c["category"]] = (
                share[c["category"]]
                .astype(str)
            )

            if len(share) > 8:

                share = pd.concat(
                    [
                        share.iloc[:7],

                        pd.DataFrame(
                            {
                                c["category"]:
                                    ["Others"],

                                "Revenue":
                                    [
                                        share.iloc[7:]
                                        ["Revenue"]
                                        .sum()
                                    ],
                            }
                        ),
                    ]
                )

            chart_card(
                "Revenue by Product Category",
                donut(
                    share,
                    c["category"],
                    "Revenue",
                    money(revenue),
                    "Total Revenue",
                ),
                height=320,
            )

        else:

            with card(
                "Revenue by Product Category"
            ):

                st.info(
                    "No product category column "
                    "was found in the data."
                )


    with right:

        geo_field = next(
            (
                k
                for k in (
                    "city",
                    "state",
                    "country",
                )
                if c[k]
            ),
            None,
        )

        if geo_field:

            geo_col = c[geo_field]

            geo_label = {
                "city": "Cities",
                "state": "States / Regions",
                "country": "Countries",
            }[geo_field]

            geo = (
                summarize(
                    d,
                    c,
                    geo_col,
                )
                .sort_values(
                    METRIC,
                    ascending=False,
                )
                .head(10)
            )

            fig = px.bar(
                geo.sort_values(METRIC),
                x=METRIC,
                y=geo_col,
                orientation="h",
            )

            fig.update_traces(
                marker_color=LAVENDER
            )

            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
            )
            fig.update_xaxes(
                showticklabels=True,
                dtick="M1",
                tickformat="%b %Y",
                tickangle=-45,
                automargin=True,
)

            if METRIC == "Revenue":
                si_axis(
                    fig,
                    "x",
                )

            chart_card(
                f"Top 10 {geo_label} by {METRIC}",
                fig,
                height=320,
            )

        else:

            with card("Top Locations"):

                st.info(
                    "No city, state or country "
                    "column was found in the data."
                )


    # --------------------------------------------------------
    # Segments / Device / Service
    # --------------------------------------------------------

    left, mid, right = st.columns(
        [2.2, 1.5, 1.1]
    )


    with left:

        if c["segment"]:

            seg = (
                segment_table(d)
                .sort_values(
                    "Customers",
                    ascending=False,
                )
            )

            fig = px.bar(
                seg,
                x=c["segment"],
                y="Customers",
                color=c["segment"],
                color_discrete_sequence=PALETTE,
            )

            fig.update_traces(
                texttemplate="%{y:,}",
                textposition="outside",
                cliponaxis=False,
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
            )

            chart_card(
                "Customer Segments (RFM)",
                fig,
                height=280,
            )

        else:

            with card(
                "Customer Segments (RFM)"
            ):

                st.info(
                    "No customer segment column "
                    "was found."
                )


    with mid:

        if c["device"]:

            dev = (
                summarize(
                    d,
                    c,
                    c["device"],
                )
                .sort_values(
                    "Orders",
                    ascending=False,
                )
            )

            dev[c["device"]] = (
                dev[c["device"]]
                .astype(str)
            )

            chart_card(
                "Orders by Device Type",
                donut(
                    dev,
                    c["device"],
                    "Orders",
                    f"{orders:,}",
                    "Total Orders",
                ),
                height=280,
            )

        else:

            with card(
                "Orders by Device Type"
            ):

                st.info(
                    "No device column "
                    "was found."
                )


    with right:

        with card(
            "Delivery Time & Ratings"
        ):

            tiles_html = service_tiles()

            if tiles_html:

                st.markdown(
                    tiles_html,
                    unsafe_allow_html=True,
                )

            else:

                st.info(
                    "No delivery time or rating "
                    "column was found."
                )


# ----------------------------------------------------------------------------
# Product & Category
# ----------------------------------------------------------------------------

elif page == "Product & Category":

    if not c["category"]:

        st.info(
            "No product category column "
            "was found in the data."
        )

    else:

        cat = summarize(
            d,
            c,
            c["category"],
        )

        left, right = st.columns(2)


        with left:

            fig = px.bar(
                cat.sort_values(METRIC),
                x=METRIC,
                y=c["category"],
                orientation="h",
            )

            fig.update_traces(
                marker_color=PRIMARY
            )

            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
            )

            if METRIC == "Revenue":
                si_axis(
                    fig,
                    "x",
                )

            chart_card(
                f"{METRIC} by Category",
                fig,
            )


        with right:

            fig = px.treemap(
                cat,
                path=[c["category"]],
                values="Revenue",
                color_discrete_sequence=PALETTE,
            )

            chart_card(
                "Revenue Share",
                fig,
            )


        with card(
            "Category Performance"
        ):

            show_table(
                cat,
                TABLE_FORMATS,
            )


# ----------------------------------------------------------------------------
# Geography
# ----------------------------------------------------------------------------

elif page == "Geography":

    levels = {
        label: c[key]
        for label, key in (
            ("City", "city"),
            ("State / Region", "state"),
            ("Country", "country"),
        )
        if c[key]
    }

    if not levels:

        st.info(
            "No city, state or country "
            "column was found in the data."
        )

    else:

        top_l, top_r = st.columns([1, 2])


        with top_l:

            level_label = st.selectbox(
                "Group by",
                list(levels),
            )


        geo_col = levels[level_label]


        geo = summarize(
            d,
            c,
            geo_col,
        )


        if len(geo) > 5:

            with top_r:

                top_n = st.slider(
                    "Number of locations to show",
                    5,
                    min(30, len(geo)),
                    min(10, len(geo)),
                )

        else:

            top_n = len(geo)


        top = (
            geo
            .sort_values(
                METRIC,
                ascending=False,
            )
            .head(top_n)
        )


        left, right = st.columns(2)


        with left:

            fig = px.bar(
                top.sort_values(METRIC),
                x=METRIC,
                y=geo_col,
                orientation="h",
            )

            fig.update_traces(
                marker_color=PRIMARY
            )

            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
            )

            if METRIC == "Revenue":

                si_axis(
                    fig,
                    "x",
                )

            chart_card(
                f"Top {top_n} by {METRIC}",
                fig,
                height=420,
            )


        with right:

            fig = px.bar(
                top.sort_values("AOV"),
                x="AOV",
                y=geo_col,
                orientation="h",
            )

            fig.update_traces(
                marker_color=LAVENDER
            )

            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
            )

            chart_card(
                f"Average Order Value "
                f"(same {top_n})",
                fig,
                height=420,
            )


        with card(
            "Location Performance"
        ):

            show_table(
                geo,
                TABLE_FORMATS,
            )


# ----------------------------------------------------------------------------
# Customer Segments — RFM
# ----------------------------------------------------------------------------

elif page == "Customer Segments":

    seg_col = c["segment"]


    if not seg_col:

        st.info(
            "No customer segment column was found. "
            "Check that `customer_segments.csv` "
            "has a customer id and a segment column."
        )

    else:

        seg = segment_table(d)


        left, right = st.columns(2)


        with left:

            fig = px.bar(
                seg.sort_values("Customers"),
                x="Customers",
                y=seg_col,
                orientation="h",
                color=seg_col,
                color_discrete_sequence=PALETTE,
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
            )

            chart_card(
                "Customers per Segment",
                fig,
            )


        with right:

            fig = px.pie(
                seg,
                names=seg_col,
                values="Revenue",
                hole=0.5,
                color_discrete_sequence=PALETTE,
            )

            fig.update_traces(
                marker=dict(
                    line=dict(
                        color="#FFFFFF",
                        width=2,
                    )
                )
            )

            chart_card(
                "Revenue by Segment",
                fig,
            )


        # --------------------------------------------------------
        # RFM summary
        # --------------------------------------------------------

        rfm_cols = [
            x
            for x in (
                "Recency",
                "Frequency",
                "Monetary",
            )
            if (
                seg_std is not None
                and x in seg_std.columns
            )
        ]


        if (
            rfm_cols
            and seg_std is not None
            and SEG_COL in seg_std.columns
        ):

            view = seg_std[
                seg_std[
                    c["customer_id"]
                ].isin(
                    d[
                        c["customer_id"]
                    ].unique()
                )
            ]

            avg = (
                view
                .groupby(SEG_COL)[rfm_cols]
                .mean()
                .reset_index()
                .rename(
                    columns={
                        SEG_COL: seg_col
                    }
                )
            )

            seg_table = seg.merge(
                avg,
                on=seg_col,
                how="left",
            )

        else:

            seg_table = seg


        with card(
            "Segment Summary"
        ):

            show_table(
                seg_table,
                TABLE_FORMATS,
            )

            if rfm_cols:

                st.caption(
                    "Recency, Frequency and Monetary "
                    "columns show the average per segment."
                )


        # --------------------------------------------------------
        # RFM scatter
        # --------------------------------------------------------

        if (
            {"Recency", "Monetary"}
            .issubset(rfm_cols)
            and SEG_COL in seg_std.columns
        ):

            plot = view.dropna(
                subset=[
                    "Recency",
                    "Monetary",
                    SEG_COL,
                ]
            )

            kwargs = (
                {
                    "size": "Frequency"
                }
                if (
                    "Frequency" in plot.columns
                    and plot["Frequency"]
                    .notna()
                    .all()
                    and (
                        plot["Frequency"]
                        >= 0
                    ).all()
                )
                else {}
            )

            fig = px.scatter(
                plot,
                x="Recency",
                y="Monetary",
                color=SEG_COL,
                opacity=0.6,
                color_discrete_sequence=PALETTE,
                hover_name=c["customer_id"],
                **kwargs,
            )

            chart_card(
                "Customers: Recency vs Monetary",
                fig,
                height=450,
            )


# ----------------------------------------------------------------------------
# Customer Behavior
# ----------------------------------------------------------------------------

elif page == "Customer Behavior":

    dims = {
        label: c[key]
        for label, key in (
            ("Device", "device"),
            ("Payment method", "payment"),
            ("Gender", "gender"),
            ("Age group", "age_group"),
        )
        if c[key]
    }


    if dims:

        label = st.selectbox(
            "Analyze by",
            list(dims),
        )

        dim_col = dims[label]

        dim = summarize(
            d,
            c,
            dim_col,
        )


        left, right = st.columns(2)


        with left:

            fig = px.pie(
                dim,
                names=dim_col,
                values="Revenue",
                hole=0.5,
                color_discrete_sequence=PALETTE,
            )

            fig.update_traces(
                marker=dict(
                    line=dict(
                        color="#FFFFFF",
                        width=2,
                    )
                )
            )

            chart_card(
                f"Revenue Share by {label}",
                fig,
            )


        with right:

            fig = px.bar(
                dim,
                x=dim_col,
                y="AOV",
                color=dim_col,
                color_discrete_sequence=PALETTE,
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
            )

            chart_card(
                f"Average Order Value by {label}",
                fig,
            )


        with card(
            f"Performance by {label}"
        ):

            show_table(
                dim,
                TABLE_FORMATS,
            )


        # --------------------------------------------------------
        # Category x Device heatmap
        # --------------------------------------------------------

        if (
            c["device"]
            and c["category"]
        ):

            heat = d.pivot_table(
                index=c["category"],
                columns=c["device"],
                values=c["revenue"],
                aggfunc="sum",
                fill_value=0,
            )

            fig = px.imshow(
                heat,
                aspect="auto",
                color_continuous_scale=[
                    "#F1F2FC",
                    "#8C97E0",
                    "#3F4C8C",
                ],
            )

            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
            )

            chart_card(
                "Revenue: Category × Device",
                fig,
                height=420,
            )


    else:

        st.info(
            "No device, payment, gender or age "
            "group column was found in the data."
        )


    # --------------------------------------------------------
    # Orders per customer
    # --------------------------------------------------------

    freq = (
        orders_per_customer
        .value_counts()
        .sort_index()
        .reset_index()
    )

    freq.columns = [
        "Orders per customer",
        "Customers",
    ]


    fig = px.bar(
        freq,
        x="Orders per customer",
        y="Customers",
    )

    fig.update_traces(
        marker_color=PRIMARY
    )

    fig.update_xaxes(
        type="category"
    )

    chart_card(
        "How Many Orders Do Customers Place?",
        fig,
    )


# ----------------------------------------------------------------------------
# Delivery & Ratings
# ----------------------------------------------------------------------------

elif page == "Delivery & Ratings":

    if not (
        c["delivery"]
        or c["rating"]
    ):

        st.info(
            "No delivery time or rating "
            "column was found in the data."
        )

    else:

        # --------------------------------------------------------
        # Service summary
        # --------------------------------------------------------

        with card(
            "Service Summary"
        ):

            st.markdown(
                service_tiles(),
                unsafe_allow_html=True,
            )


        # --------------------------------------------------------
        # Distribution charts
        # --------------------------------------------------------

        left, right = st.columns(2)


        if c["delivery"]:

            with left:

                fig = px.histogram(
                    d,
                    x=c["delivery"],
                    nbins=30,
                )

                fig.update_traces(
                    marker_color=PRIMARY
                )

                fig.update_layout(
                    xaxis_title="Days",
                    yaxis_title="Orders",
                )

                chart_card(
                    "Delivery Time Distribution",
                    fig,
                )


        if c["rating"]:

            with right:

                n_unique = (
                    d[c["rating"]]
                    .nunique()
                )

                fig = px.histogram(
                    d,
                    x=c["rating"],
                    nbins=min(
                        max(
                            n_unique,
                            5,
                        ),
                        10,
                    ),
                )

                fig.update_traces(
                    marker_color=LAVENDER
                )

                fig.update_layout(
                    xaxis_title="Rating",
                    yaxis_title="Orders",
                )

                chart_card(
                    "Rating Distribution",
                    fig,
                )


        # --------------------------------------------------------
        # Rating vs delivery time
        # --------------------------------------------------------

        if (
            c["delivery"]
            and c["rating"]
        ):

            by_days = (
                d.assign(
                    Days=d[
                        c["delivery"]
                    ]
                    .round()
                    .astype("Int64")
                )
                .groupby("Days")
                .agg(
                    AvgRating=(
                        c["rating"],
                        "mean",
                    ),
                    Orders=(
                        c["order_id"],
                        "nunique",
                    ),
                )
                .reset_index()
            )


            by_days = by_days[
                by_days["Orders"] >= 10
            ]


            fig = px.line(
                by_days,
                x="Days",
                y="AvgRating",
                markers=True,
                hover_data=[
                    "Orders"
                ],
            )

            fig.update_traces(
                line_color=PRIMARY
            )

            fig.update_layout(
                xaxis_title="Delivery days",
                yaxis_title="Average rating",
            )

            chart_card(
                "Average Rating by Delivery Time "
                "(groups with 10+ orders)",
                fig,
            )


        # --------------------------------------------------------
        # Compare service quality
        # --------------------------------------------------------

        group_options = {
            label: c[key]
            for label, key in (
                ("Category", "category"),
                ("City", "city"),
                ("Device", "device"),
            )
            if c[key]
        }


        if group_options:

            label = st.selectbox(
                "Compare service quality by",
                list(group_options),
            )

            g = summarize(
                d,
                c,
                group_options[label],
            )

            note = None


            if label == "City":

                g = g.head(15)

                note = (
                    "Showing the 15 cities "
                    "with the highest revenue."
                )


            metric = (
                "Avg Delivery (days)"
                if c["delivery"]
                else "Avg Rating"
            )


            fig = px.bar(
                g.sort_values(metric),
                x=metric,
                y=group_options[label],
                orientation="h",
                color=(
                    "Avg Rating"
                    if c["rating"]
                    else None
                ),
                color_continuous_scale=[
                    "#DAD6F5",
                    "#8C97E0",
                    "#3F4C8C",
                ],
            )

            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
            )

            chart_card(
                f"{metric} by {label}",
                fig,
                height=420,
                note=note,
            )


# ----------------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------------

st.caption(
    "Built with Python, Pandas, Plotly and Streamlit."
)