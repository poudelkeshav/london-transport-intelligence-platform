# ============================================================
# LONDON TRANSPORT INTELLIGENCE PLATFORM
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import psycopg2
import requests
import plotly.graph_objects as go

from pathlib import Path
from datetime import datetime
import base64
import html
from zoneinfo import ZoneInfo
import joblib

def get_london_time():
    return datetime.now(
        ZoneInfo("Europe/London")
    )


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="London Transport Intelligence Platform",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "image"
MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"


# ============================================================
# FIND BANNER AUTOMATICALLY
# ============================================================

def find_banner():
    if not IMAGE_DIR.exists():
        return None

    image_files = [
        p for p in IMAGE_DIR.iterdir()
        if p.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]
    ]

    if not image_files:
        return None

    # Prefer an image containing "banner" in its filename
    banner_files = [
        p for p in image_files
        if "banner" in p.name.lower()
    ]

    if banner_files:
        return banner_files[0]

    return image_files[0]


BANNER_PATH = find_banner()


# ============================================================
# POSTGRESQL SETTINGS
# ============================================================

DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "london_transport_intelligence"
DB_USER = "postgres"

# ============================================================
# CHANGE ONLY THIS PASSWORD
# ============================================================

DB_PASSWORD = "your_db_password"


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
"""
<style>

/* =========================================================
   GLOBAL
========================================================= */

html, body, [class*="css"] {
    font-family: "Segoe UI", Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 75% 0%, rgba(24,88,143,0.11), transparent 30%),
        linear-gradient(180deg, #06111e 0%, #071320 50%, #06101b 100%);
    color: #ffffff;
}

.block-container {
    max-width: 1600px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}


/* =========================================================
   SIDEBAR
========================================================= */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #091a2d 0%,
            #081725 60%,
            #071521 100%
        );

    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] > div {
    padding-top: 0.5rem;
}

.sidebar-brand {
    text-align: center;
    padding: 8px 6px 18px 6px;
}

.sidebar-icon {
    font-size: 46px;
}

.sidebar-title {
    color: white;
    font-size: 19px;
    font-weight: 800;
    line-height: 1.25;
    margin-top: 7px;
}

.sidebar-subtitle {
    color: #8094aa;
    font-size: 11px;
    margin-top: 7px;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 4px;
}

[data-testid="stSidebar"] label {
    padding-top: 6px;
    padding-bottom: 6px;
}


/* =========================================================
   HERO BANNER
========================================================= */

.hero-banner {
    position: relative;
    min-height: 205px;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 18px;

    background-size: cover;
    background-position: center;

    border: 1px solid rgba(255,255,255,0.09);

    box-shadow:
        0 16px 35px rgba(0,0,0,0.28);
}

.hero-overlay {
    position: absolute;
    inset: 0;

    background:
        linear-gradient(
            90deg,
            rgba(3,16,31,0.98) 0%,
            rgba(4,19,36,0.91) 31%,
            rgba(5,18,32,0.48) 60%,
            rgba(4,12,23,0.15) 100%
        );
}

.hero-content {
    position: relative;
    z-index: 2;
    padding: 28px 31px;
    max-width: 900px;
}

.hero-title {
    font-size: 41px;
    font-weight: 850;
    color: #ffffff;
    line-height: 1.08;
    letter-spacing: -0.7px;
}

.hero-subtitle {
    color: #d0d9e5;
    font-size: 14px;
    margin-top: 10px;
}

.hero-live {
    display: inline-block;
    margin-top: 16px;

    padding: 6px 11px;

    border-radius: 50px;

    background: rgba(29, 206, 131, 0.12);

    border:
        1px solid rgba(29, 206, 131, 0.34);

    color: #52e6a1;

    font-size: 12px;
    font-weight: 600;
}


/* =========================================================
   KPI CARDS
========================================================= */

.kpi-card {
    background:
        linear-gradient(
            145deg,
            rgba(15,41,67,0.97),
            rgba(8,26,45,0.97)
        );

    border:
        1px solid rgba(255,255,255,0.08);

    border-radius: 15px;

    padding: 16px;

    min-height: 115px;

    box-shadow:
        0 7px 19px rgba(0,0,0,0.18);
}

.kpi-label {
    color: #9aabba;
    font-size: 12px;
}

.kpi-number {
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}

.kpi-note {
    color: #6f8498;
    font-size: 11px;
    margin-top: 4px;
}

.blue {
    color: #57b9ff;
}

.green {
    color: #3ee099;
}

.red {
    color: #ff6278;
}

.yellow {
    color: #ffd052;
}

.purple {
    color: #bf94ff;
}

.cyan {
    color: #51dde7;
}


/* =========================================================
   SECTION TITLES
========================================================= */

.section-title {
    color: #ffffff;
    font-size: 20px;
    font-weight: 780;
    margin-top: 6px;
    margin-bottom: 3px;
}

.section-subtitle {
    color: #72869a;
    font-size: 11px;
    margin-bottom: 8px;
}


/* =========================================================
   ALERT CARDS
========================================================= */

.alert-card {
    background:
        linear-gradient(
            90deg,
            rgba(255,71,92,0.08),
            rgba(9,28,47,0.93)
        );

    border-left:
        4px solid #ff536c;

    border-top:
        1px solid rgba(255,255,255,0.06);

    border-right:
        1px solid rgba(255,255,255,0.06);

    border-bottom:
        1px solid rgba(255,255,255,0.06);

    border-radius: 10px;

    padding: 11px 13px;

    margin-bottom: 8px;
}

.alert-title {
    color: #ffffff;
    font-size: 13px;
    font-weight: 750;
}

.alert-body {
    color: #9aabba;
    font-size: 11px;
    line-height: 1.45;
    margin-top: 4px;
}


/* =========================================================
   INSIGHT CARDS
========================================================= */

.insight-card {
    background: #0d2135;

    border:
        1px solid rgba(255,255,255,0.07);

    border-radius: 10px;

    padding: 11px;

    margin-bottom: 7px;

    color: #b9c7d6;

    font-size: 12px;
}


/* =========================================================
   LIFT CARDS
========================================================= */

.lift-card {
    background:
        linear-gradient(
            120deg,
            rgba(133,79,255,0.08),
            rgba(10,28,47,0.94)
        );

    border:
        1px solid rgba(255,255,255,0.07);

    border-radius: 11px;

    padding: 12px;

    margin-bottom: 8px;
}

.lift-title {
    color: #c3a1ff;
    font-weight: 700;
    font-size: 13px;
}

.lift-body {
    color: #9eabba;
    font-size: 11px;
    margin-top: 5px;
    line-height: 1.45;
}


/* =========================================================
   FOOTER
========================================================= */

.footer {
    border-top:
        1px solid rgba(255,255,255,0.06);

    color: #6f8297;

    font-size: 11px;

    margin-top: 25px;

    padding-top: 13px;

    display: flex;

    justify-content: space-between;
}


/* =========================================================
   STREAMLIT ELEMENTS
========================================================= */

[data-testid="stDataFrame"] {
    border:
        1px solid rgba(255,255,255,0.08);

    border-radius: 12px;

    overflow: hidden;
}

div[data-baseweb="select"] > div {
    background-color: #0c2034;
}

div[data-baseweb="input"] > div {
    background-color: #0c2034;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent;
}

</style>
""",
unsafe_allow_html=True
)


# ============================================================
# HTML HELPER
# ============================================================

def html_block(value):
    """
    Render HTML safely as one continuous line.
    Prevents Streamlit from showing raw <div> tags.
    """

    cleaned = " ".join(
        line.strip()
        for line in value.splitlines()
        if line.strip()
    )

    st.markdown(
        cleaned,
        unsafe_allow_html=True
    )


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_connection():

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    # Read-only dashboard queries should not leave
    # PostgreSQL in an aborted transaction state.
    connection.autocommit = True

    return connection
try:

    conn = get_connection()

except Exception as error:

    st.error(
        f"PostgreSQL connection failed: {error}"
    )

    st.stop()


# ============================================================
# DATABASE LOADERS
# ============================================================

@st.cache_data(ttl=30)
def load_line_status():

    query = """
    SELECT
        collected_at,
        line_name,
        status_description,
        reason,
        is_disrupted
    FROM live_line_status
    WHERE collected_at = (
        SELECT MAX(collected_at)
        FROM live_line_status
    )
    ORDER BY line_name, status_description;
    """

    return pd.read_sql(
        query,
        conn
    )


@st.cache_data(ttl=30)
def load_bus_snapshot():

    query = """
    SELECT
        collected_at,
        stop_id,
        stop_name,
        route,
        vehicle_id,
        destination,
        direction,
        minutes_to_arrival
    FROM live_bus_arrivals
    WHERE collected_at = (
        SELECT MAX(collected_at)
        FROM live_bus_arrivals
    )
    ORDER BY minutes_to_arrival;
    """

    return pd.read_sql(
        query,
        conn
    )


@st.cache_data(ttl=30)
def load_lifts():

    query = """
    SELECT
        collected_at,
        station_unique_id,
        disrupted_lift_unique_id,
        message
    FROM live_disruptions
    WHERE collected_at = (
        SELECT MAX(collected_at)
        FROM live_disruptions
    )
    ORDER BY station_unique_id;
    """

    return pd.read_sql(
        query,
        conn
    )


# ============================================================
# TFL API FUNCTIONS
# ============================================================

@st.cache_data(ttl=3600)
def load_tfl_stations():

    modes = [
        "tube",
        "dlr",
        "overground",
        "elizabeth-line"
    ]

    records = []

    for mode in modes:

        url = (
            "https://api.tfl.gov.uk/"
            f"StopPoint/Mode/{mode}"
        )

        try:

            response = requests.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            for stop in data.get(
                "stopPoints",
                []
            ):

                latitude = stop.get("lat")
                longitude = stop.get("lon")

                if (
                    latitude is None
                    or longitude is None
                ):
                    continue

                records.append({

                    "station_id":
                        stop.get("naptanId"),

                    "station_name":
                        stop.get("commonName"),

                    "mode":
                        mode,

                    "lat":
                        latitude,

                    "lon":
                        longitude
                })

        except Exception:
            continue

    df = pd.DataFrame(records)

    if not df.empty:

        df = (
            df
            .drop_duplicates(
                subset=["station_id"]
            )
            .reset_index(drop=True)
        )

    return df


@st.cache_data(ttl=20)
def get_station_arrivals(
    station_id
):

    url = (
        "https://api.tfl.gov.uk/"
        f"StopPoint/{station_id}/Arrivals"
    )

    try:

        response = requests.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        records = []

        for x in data:

            seconds = (
                x.get("timeToStation")
                or 0
            )

            records.append({

                "Line":
                    x.get("lineName"),

                "Platform":
                    x.get("platformName"),

                "Destination":
                    x.get("destinationName"),

                "Due (min)":
                    round(
                        seconds / 60,
                        1
                    ),

                "Vehicle":
                    x.get("vehicleId")
            })

        df = pd.DataFrame(records)

        if not df.empty:

            df = (
                df
                .sort_values(
                    "Due (min)"
                )
                .reset_index(
                    drop=True
                )
            )

        return df

    except Exception:

        return pd.DataFrame()


@st.cache_data(ttl=60)
def search_bus_stops(
    search_text
):

    if not search_text:
        return pd.DataFrame()

    url = (
        "https://api.tfl.gov.uk/"
        f"StopPoint/Search/{search_text}"
    )

    params = {
        "modes": "bus",
        "maxResults": 30
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        records = []

        for match in data.get(
            "matches",
            []
        ):

            records.append({

                "stop_id":
                    match.get("id"),

                "stop_name":
                    match.get("name"),

                "lat":
                    match.get("lat"),

                "lon":
                    match.get("lon")
            })

        return pd.DataFrame(
            records
        )

    except Exception:

        return pd.DataFrame()


@st.cache_data(ttl=15)
def get_bus_arrivals_live(
    stop_id
):

    url = (
        "https://api.tfl.gov.uk/"
        f"StopPoint/{stop_id}/Arrivals"
    )

    try:

        response = requests.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        records = []

        for x in data:

            seconds = (
                x.get("timeToStation")
                or 0
            )

            records.append({

                "Route":
                    x.get("lineName"),

                "Destination":
                    x.get(
                        "destinationName"
                    ),

                "Due (min)":
                    round(
                        seconds / 60,
                        1
                    ),

                "Vehicle":
                    x.get("vehicleId"),

                "Towards":
                    x.get("towards")
            })

        df = pd.DataFrame(
            records
        )

        if not df.empty:

            df = (
                df
                .sort_values(
                    "Due (min)"
                )
                .reset_index(
                    drop=True
                )
            )

        return df

    except Exception:

        return pd.DataFrame()


# ============================================================
# LOAD MAIN DATA
# ============================================================

line_df = load_line_status()
bus_snapshot_df = load_bus_snapshot()
lift_df = load_lifts()
station_df = load_tfl_stations()


# ============================================================
# CALCULATIONS
# ============================================================

status_count = len(
    line_df
)

disrupted_count = (
    int(
        line_df[
            "is_disrupted"
        ].sum()
    )
    if not line_df.empty
    else 0
)

good_count = (
    status_count
    -
    disrupted_count
)

bus_snapshot_count = len(
    bus_snapshot_df
)

station_count = (
    station_df[
        "station_id"
    ].nunique()
    if not station_df.empty
    else 0
)

latest_time = (
    line_df[
        "collected_at"
    ].max()
    if not line_df.empty
    else None
)


# ============================================================
# BANNER BASE64
# ============================================================

def banner_base64():

    if (
        BANNER_PATH is None
        or not BANNER_PATH.exists()
    ):
        return None

    with open(
        BANNER_PATH,
        "rb"
    ) as image_file:

        return base64.b64encode(
            image_file.read()
        ).decode()


BANNER_BASE64 = (
    banner_base64()
)


# ============================================================
# HERO
# ============================================================

def show_hero():

    if BANNER_BASE64:

        hero_style = (
            "background-image:"
            f"url(data:image/png;base64,{BANNER_BASE64});"
        )

    else:

        hero_style = (
            "background:"
            "linear-gradient("
            "110deg,"
            "#071426,"
            "#19304c,"
            "#2b1930"
            ");"
        )

    content = (
        f'<div class="hero-banner" style="{hero_style}">'
        '<div class="hero-overlay"></div>'
        '<div class="hero-content">'
        '<div class="hero-title">'
        'London Transport Intelligence Platform'
        '</div>'
        '<div class="hero-subtitle">'
        'Real-time TfL data &nbsp; | &nbsp; '
        'Historical transport analytics &nbsp; | &nbsp; '
        'Machine-learning demand intelligence'
        '</div>'
        '<div class="hero-live">'
        '● LIVE TRANSPORT INTELLIGENCE'
        '</div>'
        '</div>'
        '</div>'
    )

    html_block(content)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    brand = (
        '<div class="sidebar-brand">'
        '<div class="sidebar-icon">🚇</div>'
        '<div class="sidebar-title">'
        'London Transport<br>'
        'Intelligence Platform'
        '</div>'
        '<div class="sidebar-subtitle">'
        'Live • Historical • Predictive'
        '</div>'
        '</div>'
    )

    html_block(
        brand
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🚦 Line Status",
            "🚌 Bus Arrivals",
            "📍 Station Information",
            "♿ Lift Disruptions",
            "📈 Demand Forecasting",
            "📊 Network Analytics",
            "ℹ️ About"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.caption(
        "London transport data intelligence"
    )

    st.caption(
        "Python • PostgreSQL • Streamlit • TfL API"
    )


# ============================================================
# KPI CARD FUNCTION
# ============================================================

def kpi_card(
    label,
    value,
    note,
    icon,
    colour
):

    content = (
        '<div class="kpi-card">'
        f'<div class="kpi-label">{icon} {label}</div>'
        f'<div class="kpi-number {colour}">{value}</div>'
        f'<div class="kpi-note">{note}</div>'
        '</div>'
    )

    html_block(
        content
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    show_hero()

    st.title("🏠 London Transport Intelligence Dashboard")

    st.caption(
        "Live TfL operations, historical passenger analytics "
        "and machine-learning insights in one view."
    )

    # =====================================================
    # CURRENT TIME
    # =====================================================

    now_london = get_london_time()

    # =====================================================
    # PREPARE LINE STATUS DATA
    # =====================================================

    if not line_df.empty:

        dashboard_line_df = line_df.copy()

        dashboard_line_df[
            "status_description"
        ] = (
            dashboard_line_df[
                "status_description"
            ]
            .fillna("Unknown")
        )

        dashboard_line_df[
            "reason"
        ] = (
            dashboard_line_df[
                "reason"
            ]
            .fillna("")
        )

        total_lines = (
            dashboard_line_df[
                "line_name"
            ]
            .nunique()
        )

        disrupted_line_names = (
            dashboard_line_df[
                dashboard_line_df[
                    "is_disrupted"
                ] == True
            ][
                "line_name"
            ]
            .dropna()
            .unique()
        )

        disrupted_lines = (
            len(
                disrupted_line_names
            )
        )

        good_lines = (
            total_lines
            -
            disrupted_lines
        )

        latest_line_snapshot = (
            dashboard_line_df[
                "collected_at"
            ]
            .max()
        )

    else:

        total_lines = 0
        disrupted_lines = 0
        good_lines = 0
        latest_line_snapshot = None

    # =====================================================
    # BUS SNAPSHOT METRICS
    # =====================================================

    if not bus_snapshot_df.empty:

        live_bus_predictions = (
            len(
                bus_snapshot_df
            )
        )

        live_bus_routes = (
            bus_snapshot_df[
                "line_name"
            ]
            .nunique()
            if "line_name"
            in bus_snapshot_df.columns
            else 0
        )

    else:

        live_bus_predictions = 0
        live_bus_routes = 0

    # =====================================================
    # STATION METRICS
    # =====================================================

    active_stations = (
        station_df[
            "station_name"
        ]
        .nunique()
        if not station_df.empty
        else 0
    )

    # =====================================================
    # KPI ROW
    # =====================================================

    k1, k2, k3, k4, k5, k6 = (
        st.columns(6)
    )

    with k1:

        kpi_card(
            "TfL Lines",
            total_lines,
            "Latest network snapshot",
            "🚇",
            "blue"
        )

    with k2:

        kpi_card(
            "Good Service",
            good_lines,
            "Lines without disruption",
            "✅",
            "green"
        )

    with k3:

        kpi_card(
            "Disrupted",
            disrupted_lines,
            "Lines with active issues",
            "⚠️",
            "red"
        )

    with k4:

        kpi_card(
            "Bus Predictions",
            live_bus_predictions,
            f"{live_bus_routes} routes",
            "🚌",
            "purple"
        )

    with k5:

        kpi_card(
            "Active Stations",
            active_stations,
            "TfL rail network",
            "📍",
            "cyan"
        )

    with k6:

        kpi_card(
            "London Time",
            now_london.strftime(
                "%H:%M"
            ),
            now_london.strftime(
                "%d %b %Y"
            ),
            "🕒",
            "cyan"
        )

    st.write("")

    # =====================================================
    # TOP ROW
    # =====================================================

    left, right = (
        st.columns(
            [1.45, 0.85],
            gap="medium"
        )
    )

    # -----------------------------------------------------
    # LINE STATUS TABLE
    # -----------------------------------------------------

    with left:

        st.subheader(
            "🚦 Live TfL Line Status"
        )

        if line_df.empty:

            st.info(
                "No line-status snapshot is currently available."
            )

        else:

            line_display = (
                line_df[
                    [
                        "line_name",
                        "status_description",
                        "reason"
                    ]
                ]
                .copy()
            )

            line_display[
                "reason"
            ] = (
                line_display[
                    "reason"
                ]
                .fillna("")
            )

            line_display.columns = [
                "Line",
                "Status",
                "Reason"
            ]

            st.dataframe(
                line_display,
                use_container_width=True,
                hide_index=True,
                height=400
            )

    # -----------------------------------------------------
    # STATUS DONUT
    # -----------------------------------------------------

    with right:

        st.subheader(
            "📊 Network Status"
        )

        status_overview = pd.DataFrame(
            {
                "Category": [
                    "Good Service",
                    "Disrupted"
                ],
                "Lines": [
                    good_lines,
                    disrupted_lines
                ]
            }
        )

        fig_network_status = (
            go.Figure(
                data=[
                    go.Pie(
                        labels=status_overview[
                            "Category"
                        ],
                        values=status_overview[
                            "Lines"
                        ],
                        hole=0.65
                    )
                ]
            )
        )

        fig_network_status.update_layout(
            height=330,
            paper_bgcolor=(
                "rgba(0,0,0,0)"
            ),
            font=dict(
                color="#d5deea"
            ),
            legend=dict(
                orientation="h"
            ),
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=20
            )
        )

        st.plotly_chart(
            fig_network_status,
            use_container_width=True
        )

        if latest_line_snapshot is not None:

            st.caption(
                "Latest status snapshot: "
                + latest_line_snapshot.strftime(
                    "%d %b %Y • %H:%M:%S"
                )
            )

    # =====================================================
    # MIDDLE ROW
    # =====================================================

    st.write("")

    middle_left, middle_right = (
        st.columns(
            [1, 1],
            gap="medium"
        )
    )

    # -----------------------------------------------------
    # BUS SNAPSHOT
    # -----------------------------------------------------

    with middle_left:

        st.subheader(
            "🚌 Latest Bus Arrival Snapshot"
        )

        if bus_snapshot_df.empty:

            st.info(
                "No stored bus-arrival snapshot is available."
            )

        else:

            bus_display_cols = []

            preferred_bus_cols = [
                "line_name",
                "destination_name",
                "station_name",
                "time_to_station"
            ]

            for col in preferred_bus_cols:

                if col in bus_snapshot_df.columns:

                    bus_display_cols.append(
                        col
                    )

            if bus_display_cols:

                dashboard_bus_df = (
                    bus_snapshot_df[
                        bus_display_cols
                    ]
                    .copy()
                )

                rename_map = {
                    "line_name": "Route",
                    "destination_name": "Destination",
                    "station_name": "Stop",
                    "time_to_station": "Seconds Away"
                }

                dashboard_bus_df.rename(
                    columns=rename_map,
                    inplace=True
                )

                st.dataframe(
                    dashboard_bus_df.head(15),
                    use_container_width=True,
                    hide_index=True,
                    height=350
                )

            else:

                st.dataframe(
                    bus_snapshot_df.head(15),
                    use_container_width=True,
                    hide_index=True,
                    height=350
                )

    # -----------------------------------------------------
    # STATION MAP
    # -----------------------------------------------------

    with middle_right:

        st.subheader(
            "📍 TfL Station Locations"
        )

        if station_df.empty:

            st.info(
                "No station-location data is currently available."
            )

        else:

            map_df = (
                station_df.copy()
            )

            possible_lat = [
                "lat",
                "latitude"
            ]

            possible_lon = [
                "lon",
                "longitude"
            ]

            lat_col = next(
                (
                    col
                    for col in possible_lat
                    if col in map_df.columns
                ),
                None
            )

            lon_col = next(
                (
                    col
                    for col in possible_lon
                    if col in map_df.columns
                ),
                None
            )

            if (
                lat_col is not None
                and lon_col is not None
            ):

                station_map = (
                    map_df[
                        [
                            lat_col,
                            lon_col
                        ]
                    ]
                    .dropna()
                    .rename(
                        columns={
                            lat_col: "lat",
                            lon_col: "lon"
                        }
                    )
                )

                st.map(
                    station_map
                )

            else:

                st.info(
                    "Station coordinates are not available "
                    "in the current station dataset."
                )

    # =====================================================
    # ACTIVE DISRUPTIONS
    # =====================================================

    st.write("")

    st.subheader(
        "🚨 Current Operational Alerts"
    )

    if line_df.empty:

        st.info(
            "No line-status data available."
        )

    else:

        active_alerts = (
            dashboard_line_df[
                dashboard_line_df[
                    "is_disrupted"
                ] == True
            ]
        )

        if active_alerts.empty:

            st.success(
                "No current TfL rail disruptions "
                "in the latest stored snapshot."
            )

        else:

            for _, row in (
                active_alerts.head(8).iterrows()
            ):

                line_name = html.escape(
                    str(
                        row.get(
                            "line_name",
                            "Unknown Line"
                        )
                    )
                )

                status_text = html.escape(
                    str(
                        row.get(
                            "status_description",
                            "Unknown Status"
                        )
                    )
                )

                reason_text = row.get(
                    "reason",
                    ""
                )

                if pd.isna(
                    reason_text
                ) or not str(
                    reason_text
                ).strip():

                    reason_text = (
                        "No additional reason supplied."
                    )

                reason_text = html.escape(
                    str(
                        reason_text
                    )
                )

                alert_card = (
                    '<div style="'
                    'background:#0d2135;'
                    'border-left:4px solid #ff536c;'
                    'border-radius:10px;'
                    'padding:13px;'
                    'margin-bottom:9px;'
                    '">'
                    '<div style="'
                    'font-size:14px;'
                    'font-weight:750;'
                    'color:white;'
                    '">'
                    f'⚠️ {line_name}'
                    '</div>'
                    '<div style="'
                    'font-size:12px;'
                    'color:#ff9aaa;'
                    'margin-top:4px;'
                    '">'
                    f'{status_text}'
                    '</div>'
                    '<div style="'
                    'font-size:11px;'
                    'color:#8fa5ba;'
                    'margin-top:5px;'
                    'line-height:1.45;'
                    '">'
                    f'{reason_text}'
                    '</div>'
                    '</div>'
                )

                html_block(
                    alert_card
                )

    # =====================================================
    # DEMAND FORECAST SUMMARY
    # =====================================================

    st.write("")

    st.subheader(
        "🤖 Machine-Learning Demand Forecast"
    )

    f1, f2, f3, f4 = (
        st.columns(4)
    )

    with f1:

        kpi_card(
            "Best Model",
            "XGBoost",
            "Network demand forecasting",
            "🤖",
            "purple"
        )

    with f2:

        kpi_card(
            "R²",
            "0.9207",
            "Test performance",
            "📈",
            "green"
        )

    with f3:

        kpi_card(
            "RMSE",
            "335,575",
            "Passenger journeys",
            "📊",
            "blue"
        )

    with f4:

        kpi_card(
            "Forecast Horizon",
            "1–30 Days",
            "Recursive daily prediction",
            "🔮",
            "cyan"
        )

    st.caption(
        "Open Demand Forecasting from the sidebar "
        "to generate future passenger-demand predictions."
    )

    # =====================================================
    # QUICK INSIGHTS
    # =====================================================

    st.write("")

    st.subheader(
        "💡 Quick Network Insights"
    )

    q1, q2, q3 = (
        st.columns(3)
    )

    with q1:

        if total_lines > 0:

            availability_rate = (
                good_lines
                /
                total_lines
                *
                100
            )

            st.info(
                f"{availability_rate:.1f}% of monitored TfL "
                f"lines currently have no disruption records."
            )

        else:

            st.info(
                "Current line availability cannot be calculated."
            )

    with q2:

        st.info(
            f"{live_bus_predictions} live bus-arrival predictions "
            f"are stored in the latest snapshot."
        )

    with q3:

        st.info(
            f"The station layer currently contains "
            f"{active_stations:,} TfL rail stations."
        )

    # =====================================================
    # FOOTER
    # =====================================================

    html_block(
        '<div class="footer">'
        '<span>London Transport Intelligence Platform</span>'
        '<span>Live TfL Data • PostgreSQL • Machine Learning</span>'
        '</div>'
    )
# ============================================================
# LINE STATUS PAGE
# ============================================================
elif page == "🚦 Line Status":

    show_hero()

    st.title("🚦 Live TfL Line Status")

    st.caption(
        "Monitor current service conditions, disruptions and operational status "
        "across TfL rail lines."
    )

    # =====================================================
    # REFRESH CONTROL
    # =====================================================

    refresh_col, info_col = st.columns([1, 4])

    with refresh_col:

        if st.button(
            "🔄 Refresh Status",
            use_container_width=True
        ):
            st.cache_data.clear()
            st.rerun()

    with info_col:

        if not line_df.empty:

            latest_status_time = (
                line_df[
                    "collected_at"
                ].max()
            )

            if pd.notna(latest_status_time):

                st.caption(
                    "Latest stored snapshot: "
                    + latest_status_time.strftime(
                        "%d %b %Y • %H:%M:%S"
                    )
                )

    # =====================================================
    # CHECK DATA
    # =====================================================

    if line_df.empty:

        st.warning(
            "No live line-status data is currently available."
        )

    else:

        # =====================================================
        # PREPARE DATA
        # =====================================================

        status_page_df = (
            line_df.copy()
        )

        status_page_df[
            "status_description"
        ] = (
            status_page_df[
                "status_description"
            ]
            .fillna(
                "Unknown"
            )
        )

        status_page_df[
            "reason"
        ] = (
            status_page_df[
                "reason"
            ]
            .fillna(
                "No additional information."
            )
        )

        unique_lines = (
            status_page_df[
                "line_name"
            ]
            .nunique()
        )

        disrupted_lines = (
            status_page_df[
                status_page_df[
                    "is_disrupted"
                ] == True
            ][
                "line_name"
            ]
            .nunique()
        )

        good_lines = (
            unique_lines
            -
            disrupted_lines
        )

        status_types = (
            status_page_df[
                "status_description"
            ]
            .nunique()
        )

        # =====================================================
        # KPI CARDS
        # =====================================================

        k1, k2, k3, k4 = (
            st.columns(4)
        )

        with k1:

            kpi_card(
                "TfL Lines",
                unique_lines,
                "Current snapshot",
                "🚇",
                "blue"
            )

        with k2:

            kpi_card(
                "Good Service",
                good_lines,
                "Lines without disruption",
                "✅",
                "green"
            )

        with k3:

            kpi_card(
                "Disrupted Lines",
                disrupted_lines,
                "Current operational issues",
                "⚠️",
                "red"
            )

        with k4:

            kpi_card(
                "Status Types",
                status_types,
                "Current service conditions",
                "📡",
                "purple"
            )

        st.write("")

        # =====================================================
        # FILTERS
        # =====================================================

        st.subheader(
            "🔎 Filter Network Status"
        )

        f1, f2, f3 = (
            st.columns(
                [1.2, 1.2, 1.6]
            )
        )

        with f1:

            line_options = sorted(
                status_page_df[
                    "line_name"
                ]
                .dropna()
                .unique()
            )

            selected_lines = (
                st.multiselect(
                    "Line",
                    options=line_options
                )
            )

        with f2:

            status_options = sorted(
                status_page_df[
                    "status_description"
                ]
                .dropna()
                .unique()
            )

            selected_status = (
                st.multiselect(
                    "Service status",
                    options=status_options
                )
            )

        with f3:

            search_reason = (
                st.text_input(
                    "Search disruption details",
                    placeholder=(
                        "Example: signal failure, delays, "
                        "engineering works"
                    )
                )
            )

        filtered_status = (
            status_page_df.copy()
        )

        if selected_lines:

            filtered_status = (
                filtered_status[
                    filtered_status[
                        "line_name"
                    ].isin(
                        selected_lines
                    )
                ]
            )

        if selected_status:

            filtered_status = (
                filtered_status[
                    filtered_status[
                        "status_description"
                    ].isin(
                        selected_status
                    )
                ]
            )

        if search_reason:

            filtered_status = (
                filtered_status[
                    filtered_status[
                        "reason"
                    ]
                    .str.contains(
                        search_reason,
                        case=False,
                        na=False
                    )
                ]
            )

        # =====================================================
        # STATUS OVERVIEW
        # =====================================================

        left, right = (
            st.columns(
                [1.15, 0.85],
                gap="medium"
            )
        )

        # -----------------------------------------------------
        # TABLE
        # -----------------------------------------------------

        with left:

            st.subheader(
                "🚇 Current Line Status"
            )

            display_df = (
                filtered_status[
                    [
                        "line_name",
                        "status_description",
                        "reason"
                    ]
                ]
                .copy()
            )

            display_df.columns = [
                "Line",
                "Status",
                "Reason"
            ]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=470
            )

        # -----------------------------------------------------
        # STATUS DISTRIBUTION
        # -----------------------------------------------------

        with right:

            st.subheader(
                "📊 Service Status Distribution"
            )

            status_summary = (
                filtered_status[
                    "status_description"
                ]
                .value_counts()
                .reset_index()
            )

            status_summary.columns = [
                "Status",
                "Count"
            ]

            if not status_summary.empty:

                fig_status = (
                    go.Figure(
                        data=[
                            go.Pie(
                                labels=status_summary[
                                    "Status"
                                ],
                                values=status_summary[
                                    "Count"
                                ],
                                hole=0.62
                            )
                        ]
                    )
                )

                fig_status.update_layout(
                    height=370,
                    paper_bgcolor=(
                        "rgba(0,0,0,0)"
                    ),
                    font=dict(
                        color="#d5deea"
                    ),
                    legend=dict(
                        orientation="h"
                    ),
                    margin=dict(
                        l=10,
                        r=10,
                        t=20,
                        b=20
                    )
                )

                st.plotly_chart(
                    fig_status,
                    use_container_width=True
                )

            # -------------------------------------------------
            # DISRUPTION RATE
            # -------------------------------------------------

            if unique_lines > 0:

                disruption_rate = (
                    disrupted_lines
                    /
                    unique_lines
                    *
                    100
                )

                st.metric(
                    "Network Disruption Rate",
                    f"{disruption_rate:.1f}%"
                )

        # =====================================================
        # LIVE LINE CARDS
        # =====================================================

        st.subheader(
            "📡 Line-by-Line Operational Status"
        )

        if filtered_status.empty:

            st.info(
                "No records match the selected filters."
            )

        else:

            for line_name in (
                filtered_status[
                    "line_name"
                ]
                .dropna()
                .unique()
            ):

                line_records = (
                    filtered_status[
                        filtered_status[
                            "line_name"
                        ] == line_name
                    ]
                )

                line_is_disrupted = (
                    line_records[
                        "is_disrupted"
                    ].any()
                )

                icon = (
                    "⚠️"
                    if line_is_disrupted
                    else "✅"
                )

                border_colour = (
                    "#ff536c"
                    if line_is_disrupted
                    else "#3ee099"
                )

                statuses = (
                    line_records[
                        "status_description"
                    ]
                    .dropna()
                    .unique()
                )

                status_text = (
                    " • ".join(
                        statuses
                    )
                )

                reason_values = (
                    line_records[
                        "reason"
                    ]
                    .dropna()
                    .unique()
                )

                reason_values = [
                    x
                    for x in reason_values
                    if str(x).strip()
                    and str(x).strip()
                    != "No additional information."
                ]

                if reason_values:

                    reason_text = (
                        " | ".join(
                            reason_values
                        )
                    )

                else:

                    reason_text = (
                        "No additional disruption information."
                    )

                card = (
                    f'<div style="'
                    f'background:#0d2135;'
                    f'border-left:4px solid {border_colour};'
                    f'border-top:1px solid rgba(255,255,255,0.07);'
                    f'border-right:1px solid rgba(255,255,255,0.07);'
                    f'border-bottom:1px solid rgba(255,255,255,0.07);'
                    f'border-radius:11px;'
                    f'padding:14px;'
                    f'margin-bottom:10px;'
                    f'">'
                    f'<div style="'
                    f'font-size:15px;'
                    f'font-weight:750;'
                    f'color:white;'
                    f'">'
                    f'{icon} {html.escape(str(line_name))}'
                    f'</div>'
                    f'<div style="'
                    f'font-size:12px;'
                    f'color:#9db0c3;'
                    f'margin-top:5px;'
                    f'">'
                    f'<b>Status:</b> '
                    f'{html.escape(str(status_text))}'
                    f'</div>'
                    f'<div style="'
                    f'font-size:11px;'
                    f'color:#7f93a7;'
                    f'margin-top:5px;'
                    f'line-height:1.45;'
                    f'">'
                    f'{html.escape(str(reason_text))}'
                    f'</div>'
                    f'</div>'
                )

                html_block(
                    card
                )

        # =====================================================
        # DISRUPTION DETAILS
        # =====================================================

        st.subheader(
            "🚨 Active Disruption Details"
        )

        active_disruptions = (
            filtered_status[
                filtered_status[
                    "is_disrupted"
                ] == True
            ]
        )

        if active_disruptions.empty:

            st.success(
                "No active disruptions in the current filtered view."
            )

        else:

            disruption_summary = (
                active_disruptions[
                    [
                        "line_name",
                        "status_description",
                        "reason"
                    ]
                ]
                .copy()
            )

            disruption_summary.columns = [
                "Line",
                "Status",
                "Details"
            ]

            st.dataframe(
                disruption_summary,
                use_container_width=True,
                hide_index=True
            )

        # =====================================================
        # QUICK INSIGHTS
        # =====================================================

        st.subheader(
            "💡 Live Network Insights"
        )

        i1, i2, i3 = (
            st.columns(3)
        )

        with i1:

            st.info(
                f"{good_lines} of {unique_lines} lines "
                f"currently have no disruption records."
            )

        with i2:

            st.info(
                f"{disrupted_lines} lines currently "
                f"have at least one disruption status."
            )

        with i3:

            if not status_summary.empty:

                most_common_status = (
                    status_summary.iloc[0][
                        "Status"
                    ]
                )

                st.info(
                    f"The most common current service status "
                    f"is {most_common_status}."
                )
# ============================================================
# BUS ARRIVALS PAGE
# ============================================================

elif page == "🚌 Bus Arrivals":

    show_hero()

    st.title("🚌 Live London Bus Arrivals")

    st.caption(
        "Search any London bus stop and view live TfL arrival predictions."
    )

    # =====================================================
    # SEARCH
    # =====================================================

    search_col, refresh_col = st.columns([4, 1])

    with search_col:

        search_text = st.text_input(
            "Search bus stop",
            placeholder="Example: Oxford Circus, Stratford, Abbeville Road"
        )

    with refresh_col:

        st.write("")
        st.write("")

        refresh_bus = st.button(
            "🔄 Refresh",
            use_container_width=True
        )

        if refresh_bus:
            st.cache_data.clear()
            st.rerun()

    # =====================================================
    # SEARCH RESULTS
    # =====================================================

    if search_text:

        bus_stops = search_bus_stops(search_text)

        if bus_stops.empty:

            st.warning("No matching bus stops found.")

        else:

            bus_stops["display"] = (
                bus_stops["stop_name"]
                + " | "
                + bus_stops["stop_id"]
            )

            selected_display = st.selectbox(
                "Select stop",
                bus_stops["display"]
            )

            selected_row = (
                bus_stops[
                    bus_stops["display"] == selected_display
                ]
                .iloc[0]
            )

            stop_id = selected_row["stop_id"]
            stop_name = selected_row["stop_name"]

            arrivals = get_bus_arrivals_live(stop_id)

            # =================================================
            # STOP HEADER
            # =================================================

            st.markdown(
                f"""
                ### 📍 {stop_name}
                **Stop ID:** `{stop_id}`  
                🔴 Live TfL API data
                """
            )

            # =================================================
            # KPIs
            # =================================================

            if not arrivals.empty:

                next_bus = arrivals["Due (min)"].min()

                active_routes = arrivals["Route"].nunique()

                active_vehicles = arrivals["Vehicle"].nunique()

                k1, k2, k3, k4 = st.columns(4)

                k1.metric(
                    "Next Bus",
                    f"{next_bus:.1f} min"
                )

                k2.metric(
                    "Routes",
                    active_routes
                )

                k3.metric(
                    "Vehicles",
                    active_vehicles
                )

                k4.metric(
                    "Live Predictions",
                    len(arrivals)
                )

                st.write("")

                # =============================================
                # FILTER
                # =============================================

                route_options = sorted(
                    arrivals["Route"]
                    .dropna()
                    .unique()
                )

                selected_routes = st.multiselect(
                    "Filter by route",
                    options=route_options,
                    default=[]
                )

                filtered_arrivals = arrivals.copy()

                if selected_routes:

                    filtered_arrivals = (
                        filtered_arrivals[
                            filtered_arrivals["Route"].isin(
                                selected_routes
                            )
                        ]
                    )

                # =============================================
                # MAIN CONTENT
                # =============================================

                left, right = st.columns(
                    [1.3, 0.7],
                    gap="medium"
                )

                # ---------------------------------------------
                # ARRIVALS TABLE
                # ---------------------------------------------

                with left:

                    st.subheader("🚌 Upcoming Arrivals")

                    display_df = (
                        filtered_arrivals[
                            [
                                "Route",
                                "Destination",
                                "Due (min)",
                                "Vehicle",
                                "Towards"
                            ]
                        ]
                        .copy()
                    )

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        height=430
                    )

                # ---------------------------------------------
                # MAP
                # ---------------------------------------------

                with right:

                    st.subheader("📍 Stop Location")

                    if (
                        pd.notna(selected_row["lat"])
                        and pd.notna(selected_row["lon"])
                    ):

                        stop_map = pd.DataFrame({
                            "lat": [selected_row["lat"]],
                            "lon": [selected_row["lon"]]
                        })

                        st.map(
                            stop_map,
                            zoom=15
                        )

                    else:

                        st.info(
                            "Location coordinates are unavailable "
                            "for this stop."
                        )

                # =============================================
                # ARRIVAL CHART
                # =============================================

                st.subheader("📊 Next Bus Arrival Times")

                chart_df = (
                    filtered_arrivals
                    .head(10)
                    .copy()
                )

                if not chart_df.empty:

                    chart_df["Bus"] = (
                        chart_df["Route"].astype(str)
                        + " → "
                        + chart_df["Destination"].fillna("")
                    )

                    fig = go.Figure()

                    fig.add_trace(
                        go.Bar(
                            x=chart_df["Bus"],
                            y=chart_df["Due (min)"],
                            text=chart_df["Due (min)"],
                            textposition="outside",
                            marker_color="#4db8ff"
                        )
                    )

                    fig.update_layout(
                        height=360,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(
                            color="#d5deea"
                        ),
                        xaxis_title="Bus",
                        yaxis_title="Minutes",
                        margin=dict(
                            l=30,
                            r=20,
                            t=20,
                            b=80
                        )
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                # =============================================
                # QUICK INFO
                # =============================================

                st.subheader("💡 Live Bus Insights")

                i1, i2, i3 = st.columns(3)

                with i1:

                    fastest = filtered_arrivals.iloc[0]

                    st.info(
                        f"Next service: Route "
                        f"{fastest['Route']} to "
                        f"{fastest['Destination']} "
                        f"in {fastest['Due (min)']} min."
                    )

                with i2:

                    busiest_route = (
                        filtered_arrivals["Route"]
                        .value_counts()
                        .idxmax()
                    )

                    st.info(
                        f"Most frequent route in the current "
                        f"feed: {busiest_route}."
                    )

                with i3:

                    st.info(
                        f"{len(filtered_arrivals)} live arrival "
                        f"predictions currently available."
                    )

            else:

                st.info(
                    "No live arrival predictions are currently "
                    "available for this stop."
                )

    else:

        st.info(
            "Search for a London bus stop above to view "
            "live arrival information."
        )
# ============================================================
# STATION INFORMATION PAGE
# ============================================================
elif page == "📍 Station Information":

    show_hero()

    st.title("📍 Station Intelligence")

    st.caption(
        "Explore TfL stations, view station location and inspect live rail arrivals."
    )

    if station_df.empty:

        st.warning(
            "Station information could not be loaded from TfL."
        )

    else:

        # =====================================================
        # STATION SEARCH
        # =====================================================

        station_names = sorted(
            station_df[
                "station_name"
            ]
            .dropna()
            .unique()
        )

        selected_name = st.selectbox(
            "Select station",
            station_names
        )

        # If multiple stop points share the same station name,
        # keep all matching records available
        selected_matches = (
            station_df[
                station_df[
                    "station_name"
                ] == selected_name
            ]
            .copy()
        )

        # Use first stop point as main station record
        station_record = selected_matches.iloc[0]

        station_id = station_record["station_id"]
        station_mode = (
            str(station_record["mode"])
            .replace("-", " ")
            .title()
        )

        latitude = station_record["lat"]
        longitude = station_record["lon"]

        # =====================================================
        # LIVE ARRIVALS
        # =====================================================

        arrivals = get_station_arrivals(
            station_id
        )

        # =====================================================
        # KPI CALCULATIONS
        # =====================================================

        if not arrivals.empty:

            next_train = arrivals["Due (min)"].min()

            active_lines = (
                arrivals["Line"]
                .dropna()
                .nunique()
            )

            destinations = (
                arrivals["Destination"]
                .dropna()
                .nunique()
            )

            vehicles = (
                arrivals["Vehicle"]
                .dropna()
                .nunique()
            )

        else:

            next_train = None
            active_lines = 0
            destinations = 0
            vehicles = 0

        # =====================================================
        # STATION HEADER
        # =====================================================

        st.markdown(
            f"""
            ### 🚉 {selected_name}

            **Station ID:** `{station_id}`  
            **Mode:** {station_mode}  
            🔴 Live TfL API data
            """
        )

        # =====================================================
        # KPI CARDS
        # =====================================================

        k1, k2, k3, k4 = st.columns(4)

        with k1:

            st.metric(
                "Next Train",
                (
                    f"{next_train:.1f} min"
                    if next_train is not None
                    else "N/A"
                )
            )

        with k2:

            st.metric(
                "Active Lines",
                active_lines
            )

        with k3:

            st.metric(
                "Destinations",
                destinations
            )

        with k4:

            st.metric(
                "Vehicles",
                vehicles
            )

        st.write("")

        # =====================================================
        # MAIN CONTENT
        # =====================================================

        left, right = st.columns(
            [0.75, 1.25],
            gap="medium"
        )

        # -----------------------------------------------------
        # MAP + STATION INFO
        # -----------------------------------------------------

        with left:

            st.subheader("📍 Station Location")

            if (
                pd.notna(latitude)
                and pd.notna(longitude)
            ):

                station_map = pd.DataFrame(
                    {
                        "lat": [latitude],
                        "lon": [longitude]
                    }
                )

                st.map(
                    station_map,
                    zoom=14
                )

            else:

                st.info(
                    "Coordinates are unavailable for this station."
                )

            st.subheader("ℹ️ Station Details")

            st.write(
                f"**Station:** {selected_name}"
            )

            st.write(
                f"**Mode:** {station_mode}"
            )

            st.write(
                f"**Stop ID:** `{station_id}`"
            )

            if len(selected_matches) > 1:

                modes_here = sorted(
                    selected_matches[
                        "mode"
                    ]
                    .dropna()
                    .unique()
                )

                modes_here = [
                    str(x)
                    .replace("-", " ")
                    .title()
                    for x in modes_here
                ]

                st.write(
                    "**Available modes:** "
                    + ", ".join(modes_here)
                )

        # -----------------------------------------------------
        # ARRIVALS TABLE
        # -----------------------------------------------------

        with right:

            st.subheader("🚆 Live Arrivals")

            if arrivals.empty:

                st.info(
                    "No live arrival predictions are currently available "
                    "for this station."
                )

            else:

                display_arrivals = arrivals[
                    [
                        "Line",
                        "Platform",
                        "Destination",
                        "Due (min)",
                        "Vehicle"
                    ]
                ].copy()

                st.dataframe(
                    display_arrivals,
                    use_container_width=True,
                    hide_index=True,
                    height=470
                )

        # =====================================================
        # LINE FILTER
        # =====================================================

        if not arrivals.empty:

            st.subheader("🔎 Filter Arrivals")

            line_options = sorted(
                arrivals[
                    "Line"
                ]
                .dropna()
                .unique()
            )

            selected_lines = st.multiselect(
                "Filter by line",
                options=line_options,
                default=[]
            )

            filtered_arrivals = arrivals.copy()

            if selected_lines:

                filtered_arrivals = filtered_arrivals[
                    filtered_arrivals[
                        "Line"
                    ].isin(
                        selected_lines
                    )
                ]

            # =================================================
            # ARRIVAL CHART
            # =================================================

            st.subheader("📊 Upcoming Train Times")

            chart_df = (
                filtered_arrivals
                .head(12)
                .copy()
            )

            if not chart_df.empty:

                chart_df["Train"] = (
                    chart_df["Line"].fillna("")
                    + " → "
                    + chart_df[
                        "Destination"
                    ].fillna("")
                )

                fig_station = go.Figure()

                fig_station.add_trace(
                    go.Bar(
                        x=chart_df["Train"],
                        y=chart_df["Due (min)"],
                        text=chart_df["Due (min)"],
                        textposition="outside",
                        marker_color="#8f7cff"
                    )
                )

                fig_station.update_layout(
                    height=370,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(
                        color="#d5deea"
                    ),
                    xaxis_title="Service",
                    yaxis_title="Minutes",
                    margin=dict(
                        l=30,
                        r=20,
                        t=20,
                        b=100
                    )
                )

                st.plotly_chart(
                    fig_station,
                    use_container_width=True
                )

            # =================================================
            # QUICK INSIGHTS
            # =================================================

            st.subheader("💡 Station Insights")

            i1, i2, i3 = st.columns(3)

            with i1:

                first_service = (
                    filtered_arrivals.iloc[0]
                    if not filtered_arrivals.empty
                    else None
                )

                if first_service is not None:

                    st.info(
                        f"Next service: "
                        f"{first_service['Line']} to "
                        f"{first_service['Destination']} "
                        f"in {first_service['Due (min)']} min."
                    )

            with i2:

                if not filtered_arrivals.empty:

                    busiest_line = (
                        filtered_arrivals[
                            "Line"
                        ]
                        .value_counts()
                        .idxmax()
                    )

                    st.info(
                        f"Most frequent line in the current feed: "
                        f"{busiest_line}."
                    )

            with i3:

                st.info(
                    f"{len(filtered_arrivals)} live arrival "
                    f"predictions currently available."
                )
# ============================================================
# LIFT DISRUPTIONS
# ============================================================

elif page == "♿ Lift Disruptions":

    show_hero()

    st.title("♿ Accessibility & Lift Disruptions")

    st.caption(
        "Monitor current TfL lift disruptions and step-free access issues."
    )

    if lift_df.empty:

        st.success(
            "No current lift disruption records are available."
        )

    else:

        # =====================================================
        # PREPARE DATA
        # =====================================================

        lift_page_df = lift_df.copy()

        lift_page_df["station_unique_id"] = (
            lift_page_df["station_unique_id"]
            .fillna("Unknown")
        )

        lift_page_df["disrupted_lift_unique_id"] = (
            lift_page_df["disrupted_lift_unique_id"]
            .fillna("Unknown")
        )

        lift_page_df["message"] = (
            lift_page_df["message"]
            .fillna("No disruption message available.")
        )

        latest_lift_time = (
            lift_page_df["collected_at"].max()
        )

        affected_stations = (
            lift_page_df["station_unique_id"]
            .nunique()
        )

        affected_lifts = (
            lift_page_df["disrupted_lift_unique_id"]
            .nunique()
        )

        total_records = len(
            lift_page_df
        )

        # =====================================================
        # KPI CARDS
        # =====================================================

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            kpi_card(
                "Affected Stations",
                affected_stations,
                "Current network snapshot",
                "📍",
                "red"
            )

        with k2:
            kpi_card(
                "Disrupted Lifts",
                affected_lifts,
                "Accessibility assets",
                "♿",
                "purple"
            )

        with k3:
            kpi_card(
                "Disruption Records",
                total_records,
                "Latest TfL feed",
                "⚠️",
                "yellow"
            )

        with k4:

            latest_text = (
                latest_lift_time.strftime("%H:%M")
                if pd.notna(latest_lift_time)
                else "-"
            )

            kpi_card(
                "Latest Update",
                latest_text,
                (
                    latest_lift_time.strftime("%d %b %Y")
                    if pd.notna(latest_lift_time)
                    else "No timestamp"
                ),
                "📡",
                "cyan"
            )

        st.write("")

        # =====================================================
        # FILTERS
        # =====================================================

        filter_left, filter_right = st.columns([2, 1])

        with filter_left:

            station_options = sorted(
                lift_page_df[
                    "station_unique_id"
                ].unique()
            )

            selected_stations = st.multiselect(
                "Filter affected stations",
                options=station_options,
                default=[]
            )

        with filter_right:

            search_text = st.text_input(
                "Search disruption message",
                placeholder="Example: step free, Victoria, Waterloo"
            )

        filtered_lifts = (
            lift_page_df.copy()
        )

        if selected_stations:

            filtered_lifts = filtered_lifts[
                filtered_lifts[
                    "station_unique_id"
                ].isin(
                    selected_stations
                )
            ]

        if search_text:

            filtered_lifts = filtered_lifts[
                filtered_lifts[
                    "message"
                ]
                .str.contains(
                    search_text,
                    case=False,
                    na=False
                )
            ]

        # =====================================================
        # MAIN CONTENT
        # =====================================================

        left, right = st.columns(
            [1.25, 0.75],
            gap="medium"
        )

        # -----------------------------------------------------
        # TABLE
        # -----------------------------------------------------

        with left:

            st.subheader("♿ Current Lift Disruptions")

            display_lifts = (
                filtered_lifts[
                    [
                        "station_unique_id",
                        "disrupted_lift_unique_id",
                        "message"
                    ]
                ]
                .copy()
            )

            display_lifts.columns = [
                "Station ID",
                "Lift ID",
                "Disruption"
            ]

            st.dataframe(
                display_lifts,
                use_container_width=True,
                hide_index=True,
                height=520
            )

        # -----------------------------------------------------
        # SUMMARY / ALERT CARDS
        # -----------------------------------------------------

        with right:

            st.subheader("🚨 Accessibility Alerts")

            if filtered_lifts.empty:

                st.info(
                    "No disruptions match the selected filters."
                )

            else:

                for _, row in (
                    filtered_lifts
                    .head(6)
                    .iterrows()
                ):

                    station_id = html.escape(
                        str(
                            row["station_unique_id"]
                        )
                    )

                    lift_id = html.escape(
                        str(
                            row["disrupted_lift_unique_id"]
                        )
                    )

                    message = html.escape(
                        str(
                            row["message"]
                        )
                    )

                    content = (
                        '<div class="lift-card">'
                        f'<div class="lift-title">'
                        f'♿ {station_id}'
                        '</div>'
                        f'<div class="lift-body">'
                        f'<b>{lift_id}</b><br>'
                        f'{message}'
                        '</div>'
                        '</div>'
                    )

                    html_block(
                        content
                    )

        # =====================================================
        # AFFECTED STATIONS CHART
        # =====================================================

        st.subheader(
            "📊 Disruptions by Station"
        )

        station_summary = (
            filtered_lifts[
                "station_unique_id"
            ]
            .value_counts()
            .reset_index()
        )

        station_summary.columns = [
            "Station",
            "Disruptions"
        ]

        station_summary = (
            station_summary
            .head(15)
        )

        if not station_summary.empty:

            fig_lifts = go.Figure()

            fig_lifts.add_trace(
                go.Bar(
                    x=station_summary["Station"],
                    y=station_summary["Disruptions"],
                    text=station_summary["Disruptions"],
                    textposition="outside",
                    marker_color="#b08cff"
                )
            )

            fig_lifts.update_layout(
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    color="#d5deea"
                ),
                xaxis_title="Station",
                yaxis_title="Disrupted lifts / records",
                margin=dict(
                    l=30,
                    r=20,
                    t=20,
                    b=100
                )
            )

            st.plotly_chart(
                fig_lifts,
                use_container_width=True
            )

        # =====================================================
        # QUICK INSIGHTS
        # =====================================================

        st.subheader(
            "💡 Accessibility Insights"
        )

        i1, i2, i3 = st.columns(3)

        with i1:

            st.info(
                f"{affected_stations} stations are represented "
                f"in the latest lift-disruption snapshot."
            )

        with i2:

            st.info(
                f"{affected_lifts} unique lifts currently have "
                f"reported disruption records."
            )

        with i3:

            if not station_summary.empty:

                highest_station = (
                    station_summary.iloc[0]["Station"]
                )

                highest_count = (
                    station_summary.iloc[0]["Disruptions"]
                )

                st.info(
                    f"{highest_station} has the highest number "
                    f"of disruption records in this snapshot "
                    f"({highest_count})."
                )

        # =====================================================
        # OPTIONAL STATION LOCATION MATCH
        # =====================================================

        st.subheader(
            "🗺️ Affected Station Locations"
        )

        st.caption(
            "Map points are shown where lift-disruption station IDs "
            "can be matched to available TfL station IDs."
        )

        if not station_df.empty:

            mapped_lifts = (
                filtered_lifts.merge(
                    station_df[
                        [
                            "station_id",
                            "station_name",
                            "lat",
                            "lon"
                        ]
                    ],
                    left_on="station_unique_id",
                    right_on="station_id",
                    how="inner"
                )
            )

            mapped_lifts = (
                mapped_lifts[
                    [
                        "station_name",
                        "lat",
                        "lon"
                    ]
                ]
                .dropna()
                .drop_duplicates()
            )

            if not mapped_lifts.empty:

                st.map(
                    mapped_lifts[
                        [
                            "lat",
                            "lon"
                        ]
                    ],
                    zoom=9
                )

                st.caption(
                    f"{len(mapped_lifts)} affected station locations "
                    f"could be matched directly."
                )

            else:

                st.info(
                    "None of the current disruption station IDs "
                    "matched the station coordinate table directly."
                )
# ============================================================
# DEMAND FORECASTING
# ============================================================

elif page == "📈 Demand Forecasting":

    show_hero()

    st.title("📈 Network Demand Forecasting")

    st.caption(
        "Machine-learning analysis of daily London Tube and Bus passenger demand."
    )

    # =====================================================
    # LOAD HISTORICAL JOURNEY DATA
    # =====================================================

    @st.cache_data(ttl=300)
    def load_forecast_history():

        query = """
        SELECT
            travel_date,
            tube_journey_count,
            bus_journey_count,
            total_journey_count
        FROM fact_journeys
        ORDER BY travel_date;
        """

        return pd.read_sql(query, conn)


    try:

        forecast_df = load_forecast_history()

    except Exception as error:

        try:
            conn.rollback()
        except Exception:
            pass

        st.error(
            f"Demand data could not be loaded: {error}"
        )

        st.stop()


    if forecast_df.empty:

        st.warning(
            "Historical demand data is not available."
        )

    else:

        forecast_df["travel_date"] = pd.to_datetime(
            forecast_df["travel_date"]
        )

        # =====================================================
        # MODEL RESULTS
        # =====================================================

        model_results = pd.DataFrame(
            {
                "Model": [
                    "7-Day Baseline",
                    "Linear Regression",
                    "Random Forest",
                    "XGBoost",
                    "LightGBM"
                ],

                "MAE": [
                    446718,
                    395691,
                    227872,
                    208955,
                    222110
                ],

                "RMSE": [
                    757960,
                    598336,
                    362910,
                    335575,
                    348128
                ],

                "R2": [
                    0.5955,
                    0.7480,
                    0.9073,
                    0.9207,
                    0.9147
                ]
            }
        )


        # =====================================================
        # KPI CARDS
        # =====================================================

        start_date = (
            forecast_df["travel_date"]
            .min()
            .strftime("%d %b %Y")
        )

        end_date = (
            forecast_df["travel_date"]
            .max()
            .strftime("%d %b %Y")
        )

        latest_demand = (
            forecast_df[
                "total_journey_count"
            ].iloc[-1]
        )

        average_demand = (
            forecast_df[
                "total_journey_count"
            ].mean()
        )

        k1, k2, k3, k4 = st.columns(4)

        with k1:

            kpi_card(
                "Best Model",
                "XGBoost",
                "Network demand model",
                "🏆",
                "green"
            )

        with k2:

            kpi_card(
                "Model R²",
                "0.9207",
                "Test-set performance",
                "📊",
                "blue"
            )

        with k3:

            kpi_card(
                "RMSE",
                "335,575",
                "XGBoost test RMSE",
                "🎯",
                "purple"
            )

        with k4:

            kpi_card(
                "Historical Period",
                f"{len(forecast_df):,} days",
                f"{start_date} → {end_date}",
                "📅",
                "yellow"
            )

        st.write("")


        # =====================================================
        # DEMAND TREND
        # =====================================================

        st.subheader(
            "📈 Historical Network Demand"
        )

        fig_history = go.Figure()

        fig_history.add_trace(
            go.Scatter(
                x=forecast_df["travel_date"],
                y=forecast_df["total_journey_count"],
                mode="lines",
                name="Total Demand"
            )
        )

        fig_history.update_layout(
            height=430,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#d5deea"
            ),
            xaxis_title="Date",
            yaxis_title="Daily Journeys",
            hovermode="x unified",
            margin=dict(
                l=40,
                r=20,
                t=20,
                b=40
            )
        )

        st.plotly_chart(
            fig_history,
            use_container_width=True
        )


        # =====================================================
        # TUBE VS BUS
        # =====================================================

        st.subheader(
            "🚇 Tube vs 🚌 Bus Demand"
        )

        fig_modes = go.Figure()

        fig_modes.add_trace(
            go.Scatter(
                x=forecast_df["travel_date"],
                y=forecast_df["tube_journey_count"],
                mode="lines",
                name="Tube"
            )
        )

        fig_modes.add_trace(
            go.Scatter(
                x=forecast_df["travel_date"],
                y=forecast_df["bus_journey_count"],
                mode="lines",
                name="Bus"
            )
        )

        fig_modes.update_layout(
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#d5deea"
            ),
            xaxis_title="Date",
            yaxis_title="Daily Journeys",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                y=1.08
            )
        )

        st.plotly_chart(
            fig_modes,
            use_container_width=True
        )


        # =====================================================
        # MODEL COMPARISON
        # =====================================================

        st.subheader(
            "🤖 Machine-Learning Model Comparison"
        )

        left, right = st.columns(
            [1.25, 0.75]
        )

        with left:

            fig_models = go.Figure()

            fig_models.add_trace(
                go.Bar(
                    x=model_results["Model"],
                    y=model_results["R2"],
                    text=model_results["R2"],
                    textposition="outside"
                )
            )

            fig_models.update_layout(
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    color="#d5deea"
                ),
                xaxis_title="Model",
                yaxis_title="R²",
                yaxis=dict(
                    range=[0, 1]
                ),
                margin=dict(
                    l=40,
                    r=20,
                    t=20,
                    b=80
                )
            )

            st.plotly_chart(
                fig_models,
                use_container_width=True
            )

        with right:

            st.dataframe(
                model_results.style.format(
                    {
                        "MAE": "{:,.0f}",
                        "RMSE": "{:,.0f}",
                        "R2": "{:.4f}"
                    }
                ),
                use_container_width=True,
                hide_index=True,
                height=300
            )


        # =====================================================
        # RECENT DEMAND
        # =====================================================

        st.subheader(
            "📅 Recent Passenger Demand"
        )

        recent_df = (
            forecast_df
            .tail(30)
            .copy()
        )

        fig_recent = go.Figure()

        fig_recent.add_trace(
            go.Bar(
                x=recent_df["travel_date"],
                y=recent_df["total_journey_count"],
                name="Daily Demand"
            )
        )

        fig_recent.update_layout(
            height=370,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#d5deea"
            ),
            xaxis_title="Date",
            yaxis_title="Journeys"
        )

        st.plotly_chart(
            fig_recent,
            use_container_width=True
        )


        # =====================================================
        # QUICK ML INSIGHTS
        # =====================================================

        st.subheader(
            "💡 Forecasting Insights"
        )

        i1, i2, i3 = st.columns(3)

        with i1:

            st.info(
                "XGBoost achieved the strongest test performance "
                "with R² = 0.9207."
            )

        with i2:

            st.info(
                "Tree-based ensemble models substantially "
                "outperformed Linear Regression and the "
                "7-day seasonal baseline."
            )

        with i3:

            st.info(
                "The model was evaluated chronologically, with "
                "2026 observations reserved as unseen test data."
            )


        # =====================================================
        # MODEL INFORMATION
        # =====================================================

        with st.expander(
            "🤖 View model details"
        ):

            st.write(
                "**Target:** Total daily passenger journeys"
            )

            st.write(
                "**Best model:** XGBoost"
            )

            st.write(
                "**Training period:** Historical observations "
                "through 31 December 2025"
            )

            st.write(
                "**Test period:** 1 January 2026 onward"
            )

            st.write(
                "**Best test R²:** 0.9207"
            )

            st.write(
                "**Best test RMSE:** 335,575 journeys"
            )

            st.write(
                "**Best test MAE:** 208,955 journeys"
            )

        # =====================================================
        # FUTURE DEMAND FORECAST
        # =====================================================

        st.subheader("🔮 Future Network Demand Forecast")

        st.caption(
            "Generate future daily passenger-demand predictions "
            "using the trained XGBoost model."
        )

        # -----------------------------------------------------
        # LOAD SAVED MODEL
        # -----------------------------------------------------

        @st.cache_resource
        def load_xgboost_demand_model():

            model_path = (
                MODEL_DIR
                / "xgboost_network_demand_model.pkl"
            )

            return joblib.load(model_path)


        try:

            demand_model = (
                load_xgboost_demand_model()
            )

        except Exception as error:

            demand_model = None

            st.error(
                f"XGBoost model could not be loaded: {error}"
            )


        # -----------------------------------------------------
        # FORECAST FUNCTION
        # -----------------------------------------------------

        def generate_future_forecast(
            model,
            history,
            forecast_days
        ):

            history = (
                history[
                    [
                        "travel_date",
                        "total_journey_count"
                    ]
                ]
                .dropna()
                .sort_values(
                    "travel_date"
                )
                .copy()
            )

            historical_values = (
                history[
                    "total_journey_count"
                ]
                .astype(float)
                .tolist()
            )

            last_date = (
                history[
                    "travel_date"
                ]
                .max()
            )

            predictions = []

            # Exact feature order used during training
            feature_columns = [
                "DayOfWeekNum",
                "DayOfYear",
                "WeekOfYear",
                "Month",
                "Year",
                "IsWeekend",
                "Lag_1",
                "Lag_7",
                "Lag_14",
                "Lag_28",
                "RollingMean_7",
                "RollingMean_28"
            ]

            for day_number in range(
                1,
                forecast_days + 1
            ):

                forecast_date = (
                    last_date
                    + pd.Timedelta(
                        days=day_number
                    )
                )

                # ---------------------------------------------
                # CALENDAR FEATURES
                # ---------------------------------------------

                day_of_week = (
                    forecast_date.weekday()
                )

                day_of_year = (
                    forecast_date.dayofyear
                )

                week_of_year = int(
                    forecast_date.isocalendar().week
                )

                month = (
                    forecast_date.month
                )

                year = (
                    forecast_date.year
                )

                is_weekend = int(
                    day_of_week >= 5
                )

                # ---------------------------------------------
                # LAG FEATURES
                # ---------------------------------------------

                lag_1 = (
                    historical_values[-1]
                )

                lag_7 = (
                    historical_values[-7]
                )

                lag_14 = (
                    historical_values[-14]
                )

                lag_28 = (
                    historical_values[-28]
                )

                # ---------------------------------------------
                # ROLLING FEATURES
                # ---------------------------------------------

                rolling_mean_7 = (
                    sum(
                        historical_values[-7:]
                    )
                    / 7
                )

                rolling_mean_28 = (
                    sum(
                        historical_values[-28:]
                    )
                    / 28
                )

                # ---------------------------------------------
                # MODEL INPUT
                # ---------------------------------------------

                input_row = pd.DataFrame(
                    [
                        {
                            "DayOfWeekNum":
                                day_of_week,

                            "DayOfYear":
                                day_of_year,

                            "WeekOfYear":
                                week_of_year,

                            "Month":
                                month,

                            "Year":
                                year,

                            "IsWeekend":
                                is_weekend,

                            "Lag_1":
                                lag_1,

                            "Lag_7":
                                lag_7,

                            "Lag_14":
                                lag_14,

                            "Lag_28":
                                lag_28,

                            "RollingMean_7":
                                rolling_mean_7,

                            "RollingMean_28":
                                rolling_mean_28
                        }
                    ]
                )

                input_row = (
                    input_row[
                        feature_columns
                    ]
                )

                # ---------------------------------------------
                # PREDICT
                # ---------------------------------------------

                predicted_demand = float(
                    model.predict(
                        input_row
                    )[0]
                )

                # Demand cannot realistically be negative
                predicted_demand = max(
                    predicted_demand,
                    0
                )

                predictions.append(
                    {
                        "Date":
                            forecast_date,

                        "Predicted Demand":
                            round(
                                predicted_demand
                            ),

                        "Day":
                            forecast_date.strftime(
                                "%A"
                            )
                    }
                )

                # Add prediction back into history so
                # later forecasts can use it as lag data.
                historical_values.append(
                    predicted_demand
                )

            return pd.DataFrame(
                predictions
            )


        # -----------------------------------------------------
        # FORECAST CONTROLS
        # -----------------------------------------------------

        if demand_model is not None:

            control1, control2 = st.columns(
                [1, 3]
            )

            with control1:

                forecast_days = st.slider(
                    "Forecast horizon",
                    min_value=1,
                    max_value=30,
                    value=7,
                    step=1,
                    help=(
                        "Number of future days "
                        "to predict."
                    )
                )

            with control2:

                st.write("")
                st.write("")

                run_forecast = st.button(
                    "🔮 Generate Forecast",
                    use_container_width=True
                )


            # -------------------------------------------------
            # RUN FORECAST
            # -------------------------------------------------

            if run_forecast:

                try:

                    future_df = (
                        generate_future_forecast(
                            demand_model,
                            forecast_df,
                            forecast_days
                        )
                    )

                    st.success(
                        f"{forecast_days}-day demand "
                        f"forecast generated successfully."
                    )


                    # =========================================
                    # FORECAST KPIs
                    # =========================================

                    avg_prediction = (
                        future_df[
                            "Predicted Demand"
                        ]
                        .mean()
                    )

                    peak_prediction = (
                        future_df[
                            "Predicted Demand"
                        ]
                        .max()
                    )

                    peak_row = (
                        future_df.loc[
                            future_df[
                                "Predicted Demand"
                            ].idxmax()
                        ]
                    )

                    minimum_prediction = (
                        future_df[
                            "Predicted Demand"
                        ]
                        .min()
                    )

                    f1, f2, f3, f4 = (
                        st.columns(4)
                    )

                    with f1:

                        kpi_card(
                            "Forecast Days",
                            forecast_days,
                            "Prediction horizon",
                            "📅",
                            "blue"
                        )

                    with f2:

                        kpi_card(
                            "Average Demand",
                            f"{avg_prediction:,.0f}",
                            "Predicted journeys/day",
                            "📊",
                            "green"
                        )

                    with f3:

                        kpi_card(
                            "Peak Demand",
                            f"{peak_prediction:,.0f}",
                            peak_row[
                                "Date"
                            ].strftime(
                                "%d %b"
                            ),
                            "📈",
                            "purple"
                        )

                    with f4:

                        kpi_card(
                            "Lowest Demand",
                            f"{minimum_prediction:,.0f}",
                            "Forecast period",
                            "📉",
                            "yellow"
                        )

                    st.write("")


                    # =========================================
                    # FORECAST CHART
                    # =========================================

                    st.subheader(
                        "📈 Predicted Passenger Demand"
                    )

                    # Last 28 actual days
                    actual_recent = (
                        forecast_df[
                            [
                                "travel_date",
                                "total_journey_count"
                            ]
                        ]
                        .tail(28)
                        .copy()
                    )

                    forecast_chart = go.Figure()

                    forecast_chart.add_trace(
                        go.Scatter(
                            x=actual_recent[
                                "travel_date"
                            ],
                            y=actual_recent[
                                "total_journey_count"
                            ],
                            mode="lines+markers",
                            name="Actual Demand"
                        )
                    )

                    forecast_chart.add_trace(
                        go.Scatter(
                            x=future_df["Date"],
                            y=future_df[
                                "Predicted Demand"
                            ],
                            mode="lines+markers",
                            name="XGBoost Forecast"
                        )
                    )

                    forecast_chart.update_layout(
                        height=430,
                        paper_bgcolor=(
                            "rgba(0,0,0,0)"
                        ),
                        plot_bgcolor=(
                            "rgba(0,0,0,0)"
                        ),
                        font=dict(
                            color="#d5deea"
                        ),
                        xaxis_title="Date",
                        yaxis_title=(
                            "Passenger Journeys"
                        ),
                        hovermode="x unified",
                        legend=dict(
                            orientation="h",
                            y=1.08
                        ),
                        margin=dict(
                            l=40,
                            r=20,
                            t=30,
                            b=40
                        )
                    )

                    st.plotly_chart(
                        forecast_chart,
                        use_container_width=True
                    )


                    # =========================================
                    # FORECAST TABLE
                    # =========================================

                    st.subheader(
                        "📋 Forecast Results"
                    )

                    forecast_display = (
                        future_df.copy()
                    )

                    forecast_display[
                        "Date"
                    ] = (
                        forecast_display[
                            "Date"
                        ]
                        .dt.strftime(
                            "%d %b %Y"
                        )
                    )

                    st.dataframe(
                        forecast_display,
                        use_container_width=True,
                        hide_index=True
                    )


                    # =========================================
                    # FORECAST INSIGHTS
                    # =========================================

                    st.subheader(
                        "💡 Forecast Insights"
                    )

                    c1, c2, c3 = (
                        st.columns(3)
                    )

                    with c1:

                        st.info(
                            f"Average predicted demand "
                            f"is {avg_prediction:,.0f} "
                            f"journeys per day."
                        )

                    with c2:

                        st.info(
                            f"Highest predicted demand "
                            f"is {peak_prediction:,.0f} "
                            f"journeys on "
                            f"{peak_row['Date'].strftime('%A, %d %b')}."
                        )

                    with c3:

                        weekend_avg = (
                            future_df[
                                future_df[
                                    "Date"
                                ].dt.weekday >= 5
                            ][
                                "Predicted Demand"
                            ]
                            .mean()
                        )

                        weekday_avg = (
                            future_df[
                                future_df[
                                    "Date"
                                ].dt.weekday < 5
                            ][
                                "Predicted Demand"
                            ]
                            .mean()
                        )

                        if (
                            pd.notna(weekend_avg)
                            and
                            pd.notna(weekday_avg)
                        ):

                            st.info(
                                f"Weekday average: "
                                f"{weekday_avg:,.0f}. "
                                f"Weekend average: "
                                f"{weekend_avg:,.0f}."
                            )

                        else:

                            st.info(
                                "Increase the forecast "
                                "horizon to compare weekday "
                                "and weekend demand."
                            )


                    # =========================================
                    # IMPORTANT MODEL NOTE
                    # =========================================

                    st.caption(
                        "Forecasts beyond the first day are recursive: "
                        "earlier predictions are reused to construct "
                        "lag and rolling-average features for later days. "
                        "Uncertainty therefore increases as the forecast "
                        "horizon becomes longer."
                    )

                except Exception as error:

                    st.error(
                        f"Forecast generation failed: {error}"
                    )

elif page == "📊 Network Analytics":

    show_hero()

    st.title("📊 Network Analytics")

    st.caption(
        "Analyse historical London transport demand, "
        "mode patterns, station activity and temporal behaviour."
    )

    # =====================================================
    # LOAD NETWORK DATA
    # =====================================================

    @st.cache_data(ttl=300)
    def load_network_journeys():

        query = """
        SELECT
            travel_date,
            tube_journey_count,
            bus_journey_count,
            total_journey_count
        FROM fact_journeys
        ORDER BY travel_date;
        """

        return pd.read_sql(
            query,
            conn
        )


    @st.cache_data(ttl=300)
    def load_network_stations():

        query = """
        SELECT
            station,
            SUM(entry_tap_count) AS total_entries,
            SUM(exit_tap_count) AS total_exits,
            SUM(total_tap_count) AS total_taps
        FROM fact_station_footfall
        WHERE station IS NOT NULL
        GROUP BY station
        ORDER BY total_taps DESC;
        """

        return pd.read_sql(
            query,
            conn
        )


    # =====================================================
    # READ DATA
    # =====================================================

    try:

        network_df = (
            load_network_journeys()
        )

        station_usage_df = (
            load_network_stations()
        )

    except Exception as error:

        try:
            conn.rollback()
        except Exception:
            pass

        st.error(
            f"Network analytics data could not be loaded: {error}"
        )

        st.stop()


    if network_df.empty:

        st.warning(
            "Historical journey data is unavailable."
        )

    else:

        # =====================================================
        # PREPARE DATA
        # =====================================================

        network_df["travel_date"] = (
            pd.to_datetime(
                network_df["travel_date"]
            )
        )

        network_df["year"] = (
            network_df[
                "travel_date"
            ].dt.year
        )

        network_df["month"] = (
            network_df[
                "travel_date"
            ].dt.to_period(
                "M"
            ).astype(str)
        )

        network_df["day_name"] = (
            network_df[
                "travel_date"
            ].dt.day_name()
        )

        network_df["day_number"] = (
            network_df[
                "travel_date"
            ].dt.weekday
        )

        network_df["day_type"] = (
            network_df[
                "day_number"
            ].apply(
                lambda x:
                "Weekend"
                if x >= 5
                else "Weekday"
            )
        )

        # =====================================================
        # KPI VALUES
        # =====================================================

        total_days = len(
            network_df
        )

        total_network_journeys = (
            network_df[
                "total_journey_count"
            ].sum()
        )

        average_daily_demand = (
            network_df[
                "total_journey_count"
            ].mean()
        )

        peak_index = (
            network_df[
                "total_journey_count"
            ].idxmax()
        )

        peak_row = (
            network_df.loc[
                peak_index
            ]
        )

        peak_demand = (
            peak_row[
                "total_journey_count"
            ]
        )

        peak_date = (
            peak_row[
                "travel_date"
            ].strftime(
                "%d %b %Y"
            )
        )

        # =====================================================
        # KPI CARDS
        # =====================================================

        k1, k2, k3, k4 = (
            st.columns(4)
        )

        with k1:

            kpi_card(
                "Historical Days",
                f"{total_days:,}",
                "Daily observations",
                "📅",
                "blue"
            )

        with k2:

            kpi_card(
                "Network Journeys",
                f"{total_network_journeys / 1_000_000_000:.2f}B",
                "Tube + Bus",
                "🚇",
                "green"
            )

        with k3:

            kpi_card(
                "Average Daily Demand",
                f"{average_daily_demand / 1_000_000:.2f}M",
                "Journeys per day",
                "📊",
                "purple"
            )

        with k4:

            kpi_card(
                "Peak Daily Demand",
                f"{peak_demand / 1_000_000:.2f}M",
                peak_date,
                "🔥",
                "yellow"
            )

        st.write("")

        # =====================================================
        # NETWORK DEMAND TREND
        # =====================================================

        st.subheader(
            "📈 London Transport Demand Over Time"
        )

        monthly_network = (
            network_df
            .groupby(
                "month",
                as_index=False
            )
            .agg(
                tube_journeys=(
                    "tube_journey_count",
                    "sum"
                ),
                bus_journeys=(
                    "bus_journey_count",
                    "sum"
                ),
                total_journeys=(
                    "total_journey_count",
                    "sum"
                )
            )
        )

        fig_network = (
            go.Figure()
        )

        fig_network.add_trace(
            go.Scatter(
                x=monthly_network[
                    "month"
                ],
                y=monthly_network[
                    "tube_journeys"
                ],
                mode="lines",
                name="Tube"
            )
        )

        fig_network.add_trace(
            go.Scatter(
                x=monthly_network[
                    "month"
                ],
                y=monthly_network[
                    "bus_journeys"
                ],
                mode="lines",
                name="Bus"
            )
        )

        fig_network.update_layout(
            height=430,
            paper_bgcolor=(
                "rgba(0,0,0,0)"
            ),
            plot_bgcolor=(
                "rgba(0,0,0,0)"
            ),
            font=dict(
                color="#d5deea"
            ),
            xaxis_title="Month",
            yaxis_title="Passenger Journeys",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                y=1.08
            ),
            margin=dict(
                l=40,
                r=20,
                t=30,
                b=50
            )
        )

        st.plotly_chart(
            fig_network,
            use_container_width=True
        )

        # =====================================================
        # WEEKDAY VS WEEKEND
        # =====================================================

        left1, right1 = (
            st.columns(2)
        )

        with left1:

            st.subheader(
                "📅 Weekday vs Weekend Demand"
            )

            day_type_df = (
                network_df
                .groupby(
                    "day_type",
                    as_index=False
                )
                .agg(
                    average_demand=(
                        "total_journey_count",
                        "mean"
                    )
                )
            )

            fig_day_type = (
                go.Figure()
            )

            fig_day_type.add_trace(
                go.Bar(
                    x=day_type_df[
                        "day_type"
                    ],
                    y=day_type_df[
                        "average_demand"
                    ],
                    text=(
                        day_type_df[
                            "average_demand"
                        ]
                        / 1_000_000
                    ).round(2),
                    texttemplate=(
                        "%{text}M"
                    ),
                    textposition="outside"
                )
            )

            fig_day_type.update_layout(
                height=370,
                paper_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                plot_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                font=dict(
                    color="#d5deea"
                ),
                xaxis_title="Day Type",
                yaxis_title=(
                    "Average Daily Journeys"
                ),
                margin=dict(
                    l=40,
                    r=20,
                    t=20,
                    b=40
                )
            )

            st.plotly_chart(
                fig_day_type,
                use_container_width=True
            )

        # =====================================================
        # DAY OF WEEK
        # =====================================================

        with right1:

            st.subheader(
                "🗓️ Demand by Day of Week"
            )

            day_order = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ]

            weekday_df = (
                network_df
                .groupby(
                    "day_name",
                    as_index=False
                )
                .agg(
                    average_demand=(
                        "total_journey_count",
                        "mean"
                    )
                )
            )

            weekday_df[
                "day_name"
            ] = pd.Categorical(
                weekday_df[
                    "day_name"
                ],
                categories=day_order,
                ordered=True
            )

            weekday_df = (
                weekday_df
                .sort_values(
                    "day_name"
                )
            )

            fig_weekday = (
                go.Figure()
            )

            fig_weekday.add_trace(
                go.Bar(
                    x=weekday_df[
                        "day_name"
                    ],
                    y=weekday_df[
                        "average_demand"
                    ]
                )
            )

            fig_weekday.update_layout(
                height=370,
                paper_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                plot_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                font=dict(
                    color="#d5deea"
                ),
                xaxis_title="Day",
                yaxis_title=(
                    "Average Journeys"
                ),
                margin=dict(
                    l=40,
                    r=20,
                    t=20,
                    b=70
                )
            )

            st.plotly_chart(
                fig_weekday,
                use_container_width=True
            )

        # =====================================================
        # YEARLY NETWORK COMPARISON
        # =====================================================

        st.subheader(
            "📊 Annual Passenger Demand"
        )

        yearly_df = (
            network_df
            .groupby(
                "year",
                as_index=False
            )
            .agg(
                tube_journeys=(
                    "tube_journey_count",
                    "sum"
                ),
                bus_journeys=(
                    "bus_journey_count",
                    "sum"
                )
            )
        )

        fig_year = (
            go.Figure()
        )

        fig_year.add_trace(
            go.Bar(
                x=yearly_df[
                    "year"
                ],
                y=yearly_df[
                    "tube_journeys"
                ],
                name="Tube"
            )
        )

        fig_year.add_trace(
            go.Bar(
                x=yearly_df[
                    "year"
                ],
                y=yearly_df[
                    "bus_journeys"
                ],
                name="Bus"
            )
        )

        fig_year.update_layout(
            height=400,
            barmode="group",
            paper_bgcolor=(
                "rgba(0,0,0,0)"
            ),
            plot_bgcolor=(
                "rgba(0,0,0,0)"
            ),
            font=dict(
                color="#d5deea"
            ),
            xaxis_title="Year",
            yaxis_title="Passenger Journeys",
            legend=dict(
                orientation="h",
                y=1.08
            )
        )

        st.plotly_chart(
            fig_year,
            use_container_width=True
        )

        # =====================================================
        # STATION ANALYTICS
        # =====================================================

        st.subheader(
            "🚉 Station Network Intelligence"
        )

        if not station_usage_df.empty:

            station_left, station_right = (
                st.columns(
                    [1.3, 0.7]
                )
            )

            # -------------------------------------------------
            # TOP STATIONS
            # -------------------------------------------------

            with station_left:

                st.markdown(
                    "#### Top 15 Stations by Passenger Footfall"
                )

                top_station_df = (
                    station_usage_df
                    .head(15)
                    .sort_values(
                        "total_taps",
                        ascending=True
                    )
                )

                fig_station = (
                    go.Figure()
                )

                fig_station.add_trace(
                    go.Bar(
                        x=top_station_df[
                            "total_taps"
                        ],
                        y=top_station_df[
                            "station"
                        ],
                        orientation="h"
                    )
                )

                fig_station.update_layout(
                    height=500,
                    paper_bgcolor=(
                        "rgba(0,0,0,0)"
                    ),
                    plot_bgcolor=(
                        "rgba(0,0,0,0)"
                    ),
                    font=dict(
                        color="#d5deea"
                    ),
                    xaxis_title=(
                        "Total Tap Activity"
                    ),
                    yaxis_title="",
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=40
                    )
                )

                st.plotly_chart(
                    fig_station,
                    use_container_width=True
                )

            # -------------------------------------------------
            # ENTRY / EXIT SHARE
            # -------------------------------------------------

            with station_right:

                st.markdown(
                    "#### Network Entry vs Exit Activity"
                )

                total_entries = (
                    station_usage_df[
                        "total_entries"
                    ].sum()
                )

                total_exits = (
                    station_usage_df[
                        "total_exits"
                    ].sum()
                )

                fig_entry_exit = (
                    go.Figure(
                        data=[
                            go.Pie(
                                labels=[
                                    "Entries",
                                    "Exits"
                                ],
                                values=[
                                    total_entries,
                                    total_exits
                                ],
                                hole=0.65
                            )
                        ]
                    )
                )

                fig_entry_exit.update_layout(
                    height=370,
                    paper_bgcolor=(
                        "rgba(0,0,0,0)"
                    ),
                    font=dict(
                        color="#d5deea"
                    ),
                    legend=dict(
                        orientation="h"
                    ),
                    margin=dict(
                        l=10,
                        r=10,
                        t=20,
                        b=20
                    )
                )

                st.plotly_chart(
                    fig_entry_exit,
                    use_container_width=True
                )

                station_count_history = (
                    station_usage_df[
                        "station"
                    ].nunique()
                )

                busiest_station = (
                    station_usage_df.iloc[0][
                        "station"
                    ]
                )

                busiest_taps = (
                    station_usage_df.iloc[0][
                        "total_taps"
                    ]
                )

                st.info(
                    f"{station_count_history:,} stations "
                    f"are represented in the historical "
                    f"footfall dataset."
                )

                st.info(
                    f"Highest recorded footfall: "
                    f"{busiest_station} with "
                    f"{busiest_taps:,.0f} taps."
                )

        # =====================================================
        # NETWORK INSIGHTS
        # =====================================================

        st.subheader(
            "💡 Network Insights"
        )

        weekday_average = (
            network_df[
                network_df[
                    "day_type"
                ] == "Weekday"
            ][
                "total_journey_count"
            ].mean()
        )

        weekend_average = (
            network_df[
                network_df[
                    "day_type"
                ] == "Weekend"
            ][
                "total_journey_count"
            ].mean()
        )

        busiest_day = (
            weekday_df.loc[
                weekday_df[
                    "average_demand"
                ].idxmax(),
                "day_name"
            ]
        )

        busiest_day_value = (
            weekday_df[
                "average_demand"
            ].max()
        )

        tube_total = (
            network_df[
                "tube_journey_count"
            ].sum()
        )

        bus_total = (
            network_df[
                "bus_journey_count"
            ].sum()
        )

        dominant_mode = (
            "Tube"
            if tube_total > bus_total
            else "Bus"
        )

        i1, i2, i3, i4 = (
            st.columns(4)
        )

        with i1:

            st.info(
                f"Average weekday demand is "
                f"{weekday_average / 1_000_000:.2f}M "
                f"journeys per day."
            )

        with i2:

            st.info(
                f"Average weekend demand is "
                f"{weekend_average / 1_000_000:.2f}M "
                f"journeys per day."
            )

        with i3:

            st.info(
                f"{busiest_day} has the highest "
                f"average demand at "
                f"{busiest_day_value / 1_000_000:.2f}M "
                f"journeys."
            )

        with i4:

            st.info(
                f"{dominant_mode} accounts for the "
                f"larger journey volume across the "
                f"historical dataset."
            )

        # =====================================================
        # DATA EXPLORER
        # =====================================================

        with st.expander(
            "🔎 Explore Network Data"
        ):

            tab1, tab2, tab3 = (
                st.tabs(
                    [
                        "Monthly Demand",
                        "Yearly Demand",
                        "Station Usage"
                    ]
                )
            )

            with tab1:

                st.dataframe(
                    monthly_network,
                    use_container_width=True,
                    hide_index=True
                )

            with tab2:

                st.dataframe(
                    yearly_df,
                    use_container_width=True,
                    hide_index=True
                )

            with tab3:

                st.dataframe(
                    station_usage_df.head(
                        100
                    ),
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About":

    show_hero()

    st.title("ℹ️ About This Platform")

    st.caption(
        "A data-driven London transport intelligence platform "
        "combining live operations, historical analytics and machine learning."
    )

    # =====================================================
    # PROJECT OVERVIEW
    # =====================================================

    st.subheader("🚇 Project Overview")

    st.write(
        """
        The London Transport Intelligence Platform brings together
        historical passenger-demand data, live Transport for London
        operational information and machine-learning forecasting
        within a single interactive application.

        The platform is designed to support transport monitoring,
        demand analysis, station intelligence and operational insight
        across London's public transport network.
        """
    )

    # =====================================================
    # PLATFORM CAPABILITIES
    # =====================================================

    st.subheader("🧭 Platform Capabilities")

    c1, c2, c3 = st.columns(3)

    with c1:

        kpi_card(
            "Live Operations",
            "TfL API",
            "Status, arrivals and disruptions",
            "📡",
            "blue"
        )

    with c2:

        kpi_card(
            "Historical Analytics",
            "2019–2026",
            "Passenger demand and station usage",
            "📊",
            "green"
        )

    with c3:

        kpi_card(
            "Machine Learning",
            "XGBoost",
            "Daily passenger-demand forecasting",
            "🤖",
            "purple"
        )

    st.write("")

    # =====================================================
    # MAIN FEATURES
    # =====================================================

    st.subheader("✨ Main Features")

    feature_left, feature_right = st.columns(2)

    with feature_left:

        st.markdown(
            """
            ### 📡 Live Transport Intelligence

            - Current TfL line status
            - Bus arrival predictions
            - Rail arrival predictions
            - Lift disruption monitoring
            - Station lookup and locations
            - Live disruption details
            """
        )

    with feature_right:

        st.markdown(
            """
            ### 📊 Historical & Predictive Analytics

            - Tube and Bus demand trends
            - Station passenger footfall
            - Weekday and weekend analysis
            - Annual transport comparisons
            - Network-level XGBoost forecasting
            - Multi-day passenger-demand prediction
            """
        )

    # =====================================================
    # DATA SOURCES
    # =====================================================

    st.subheader("🗂️ Data Sources")

    data_sources = pd.DataFrame(
        {
            "Source": [
                "TfL Unified API",
                "TfL Journey Data",
                "TfL Station Footfall",
                "NUMBAT",
                "PTAL"
            ],
            "Purpose": [
                "Live line status, arrivals, stations and disruptions",
                "Historical Tube and Bus passenger demand",
                "Station entry and exit activity",
                "Station-level demand profiles",
                "Public transport accessibility analysis"
            ]
        }
    )

    st.dataframe(
        data_sources,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # TECHNOLOGY STACK
    # =====================================================

    st.subheader("🛠️ Technology Stack")

    t1, t2, t3, t4 = st.columns(4)

    with t1:

        st.info(
            "🐍 **Python**\n\n"
            "Data processing, APIs and machine learning"
        )

    with t2:

        st.info(
            "🐘 **PostgreSQL**\n\n"
            "Historical and live transport data storage"
        )

    with t3:

        st.info(
            "📊 **Streamlit**\n\n"
            "Interactive web application"
        )

    with t4:

        st.info(
            "📈 **Plotly**\n\n"
            "Interactive transport visualisation"
        )

    # =====================================================
    # MACHINE LEARNING
    # =====================================================

    st.subheader("🤖 Machine-Learning Model")

    ml_left, ml_right = st.columns(
        [1, 1]
    )

    with ml_left:

        st.markdown(
            """
            ### Network Demand Forecasting

            The forecasting component predicts total daily
            Tube and Bus passenger demand.

            Models evaluated:

            - 7-Day Seasonal Baseline
            - Linear Regression
            - Random Forest
            - XGBoost
            - LightGBM
            """
        )

    with ml_right:

        model_about = pd.DataFrame(
            {
                "Metric": [
                    "Best Model",
                    "R²",
                    "RMSE",
                    "MAE"
                ],
                "Result": [
                    "XGBoost",
                    "0.9207",
                    "335,575",
                    "208,955"
                ]
            }
        )

        st.dataframe(
            model_about,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # SYSTEM ARCHITECTURE
    # =====================================================

    st.subheader("🏗️ Platform Architecture")

    st.code(
        """
Historical TfL Data             Live TfL API
        │                           │
        └────────────┬──────────────┘
                     │
                  Python ETL
                     │
                     ▼
                PostgreSQL
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
 Historical Analytics     Live Operations
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
              Machine Learning
                     │
                     ▼
               Streamlit App
        """,
        language="text"
    )

    # =====================================================
    # PROJECT PURPOSE
    # =====================================================

    st.subheader("🎯 Project Purpose")

    st.write(
        """
        The aim of this project is to demonstrate how transport data
        engineering, SQL, machine learning and interactive analytics
        can be integrated into a single practical intelligence system.

        The platform can support exploration of passenger demand,
        station activity, service disruption and future network demand,
        while providing a foundation for further transport analytics
        and operational decision-support applications.
        """
    )

    # =====================================================
    # CURRENT SCOPE
    # =====================================================

    st.subheader("🌍 Current Network Scope")

    scope_df = pd.DataFrame(
        {
            "Transport Mode": [
                "London Underground",
                "Elizabeth line",
                "London Overground",
                "DLR",
                "London Buses"
            ],
            "Status": [
                "Included",
                "Included",
                "Included",
                "Included",
                "Included"
            ]
        }
    )

    st.dataframe(
        scope_df,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # FUTURE DEVELOPMENT
    # =====================================================

    st.subheader("🚀 Future Development")

    st.markdown(
        """
        Possible future extensions include:

        - automated scheduled TfL API ingestion
        - historical disruption modelling
        - spatial station-demand analysis
        - additional anomaly-detection methods
        - FastAPI model-serving layer
        - Docker deployment
        - cloud-hosted PostgreSQL
        - additional transport modes and datasets
        """
    )

    # =====================================================
    # FOOTER
    # =====================================================

    html_block(
        '<div class="footer">'
        '<span>London Transport Intelligence Platform</span>'
        '<span>Python • PostgreSQL • Machine Learning • TfL Open Data</span>'
        '</div>'
    )
