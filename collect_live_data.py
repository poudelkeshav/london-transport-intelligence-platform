# ============================================================
# LONDON TRANSPORT INTELLIGENCE PLATFORM
# LIVE TFL DATA COLLECTOR
# ============================================================

import requests
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo


# ============================================================
# POSTGRESQL SETTINGS
# ============================================================

DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "london_transport_intelligence"
DB_USER = "postgres"

# Change only this password
DB_PASSWORD = "your_password"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
# ============================================================
# CURRENT LONDON TIME
# ============================================================

def london_now():

    return datetime.now(
        ZoneInfo("Europe/London")
    )


# ============================================================
# TFL LINE STATUS
# ============================================================

def collect_line_status():

    url = (
        "https://api.tfl.gov.uk/"
        "Line/Mode/"
        "tube,overground,elizabeth-line,dlr/"
        "Status"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    collected_at = london_now()

    records = []

    for line in data:

        line_name = line.get(
            "name"
        )

        for status in line.get(
            "lineStatuses",
            []
        ):

            status_description = (
                status.get(
                    "statusSeverityDescription"
                )
            )

            reason = (
                status.get(
                    "reason"
                )
            )

            is_disrupted = (
                status_description
                != "Good Service"
            )

            records.append(
                (
                    collected_at,
                    line_name,
                    status_description,
                    reason,
                    is_disrupted
                )
            )

    return records


# ============================================================
# TFL LIFT DISRUPTIONS
# ============================================================

def collect_lift_disruptions():

    url = (
        "https://api.tfl.gov.uk/"
        "Disruptions/Lifts/v2/"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    collected_at = london_now()

    records = []

    for item in data:

        station_id = (
            item.get(
                "stationUniqueId"
            )
        )

        message = (
            item.get(
                "message"
            )
        )

        disrupted_lifts = (
            item.get(
                "disruptedLiftUniqueIds"
            )
            or []
        )

        for lift_id in disrupted_lifts:

            records.append(
                (
                    collected_at,
                    station_id,
                    lift_id,
                    message
                )
            )

    return records


# ============================================================
# SAVE LINE STATUS
# ============================================================

def save_line_status(
    connection,
    records
):

    if not records:

        print(
            "No line-status records returned."
        )

        return

    query = """
    INSERT INTO live_line_status
    (
        collected_at,
        line_name,
        status_description,
        reason,
        is_disrupted
    )
    VALUES
    (
        %s,
        %s,
        %s,
        %s,
        %s
    );
    """

    with connection.cursor() as cursor:

        cursor.executemany(
            query,
            records
        )

    connection.commit()

    print(
        f"Line-status rows inserted: "
        f"{len(records)}"
    )


# ============================================================
# SAVE LIFT DISRUPTIONS
# ============================================================

def save_lift_disruptions(
    connection,
    records
):

    if not records:

        print(
            "No lift disruptions returned."
        )

        return

    query = """
    INSERT INTO live_disruptions
    (
        collected_at,
        station_unique_id,
        disrupted_lift_unique_id,
        message
    )
    VALUES
    (
        %s,
        %s,
        %s,
        %s
    );
    """

    with connection.cursor() as cursor:

        cursor.executemany(
            query,
            records
        )

    connection.commit()

    print(
        f"Lift-disruption rows inserted: "
        f"{len(records)}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "London Transport Intelligence Platform"
    )

    print(
        "Live TfL Data Collector"
    )

    print(
        "=" * 60
    )

    print(
        "Collection time:",
        london_now().strftime(
            "%d %b %Y %H:%M:%S"
        )
    )

    connection = None

    try:

        # ----------------------------------------------------
        # API COLLECTION
        # ----------------------------------------------------

        print(
            "\nCollecting TfL line status..."
        )

        line_records = (
            collect_line_status()
        )

        print(
            "Records received:",
            len(line_records)
        )

        print(
            "\nCollecting TfL lift disruptions..."
        )

        lift_records = (
            collect_lift_disruptions()
        )

        print(
            "Records received:",
            len(lift_records)
        )

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        print(
            "\nConnecting to PostgreSQL..."
        )

        connection = (
            get_connection()
        )

        print(
            "PostgreSQL connected."
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_line_status(
            connection,
            line_records
        )

        save_lift_disruptions(
            connection,
            lift_records
        )

        print(
            "\n✅ Live TfL collection completed successfully."
        )

    except Exception as error:

        if connection is not None:

            connection.rollback()

        print(
            "\n❌ Collection failed:"
        )

        print(
            error
        )

    finally:

        if connection is not None:

            connection.close()

        print(
            "\nDatabase connection closed."
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()