SELECT current_database();
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    week_of_year INTEGER,
    is_weekend BOOLEAN
);
SELECT *
FROM dim_date;
CREATE TABLE fact_journeys (
    date_id DATE PRIMARY KEY,
    day_of_week VARCHAR(20),
    tube_journeys BIGINT,
    bus_journeys BIGINT,
    total_journeys BIGINT,
    source_file VARCHAR(255),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE fact_station_footfall (
    footfall_id BIGSERIAL PRIMARY KEY,
    travel_date DATE,
    station VARCHAR(255),
    entry_tap_count BIGINT,
    exit_tap_count BIGINT,
    total_tap_count BIGINT,
    source_file VARCHAR(255)
);

CREATE TABLE fact_numbat_entries (
    entry_id BIGSERIAL PRIMARY KEY,
    nlc VARCHAR(20),
    asc_code VARCHAR(20),
    station VARCHAR(255),
    fare_zone VARCHAR(20),
    day_type VARCHAR(20),
    time_interval VARCHAR(20),
    entry_count DOUBLE PRECISION
);

CREATE TABLE fact_numbat_exits (
    exit_id BIGSERIAL PRIMARY KEY,
    nlc VARCHAR(20),
    asc_code VARCHAR(20),
    station VARCHAR(255),
    fare_zone VARCHAR(20),
    day_type VARCHAR(20),
    time_interval VARCHAR(20),
    exit_count DOUBLE PRECISION
);

CREATE TABLE fact_station_annualised_2025 (
    annual_id BIGSERIAL PRIMARY KEY,
    mode VARCHAR(20),
    mnlc VARCHAR(20),
    masc VARCHAR(20),
    station VARCHAR(255),
    coverage VARCHAR(100),
    source VARCHAR(50),

    monday_entry DOUBLE PRECISION,
    midweek_entry DOUBLE PRECISION,
    friday_entry DOUBLE PRECISION,
    saturday_entry DOUBLE PRECISION,
    sunday_entry DOUBLE PRECISION,

    monday_exit DOUBLE PRECISION,
    midweek_exit DOUBLE PRECISION,
    friday_exit DOUBLE PRECISION,
    saturday_exit DOUBLE PRECISION,
    sunday_exit DOUBLE PRECISION,

    weekly_entry_exit DOUBLE PRECISION,
    twelveweek_entry_exit DOUBLE PRECISION,
    annualised_entry_exit DOUBLE PRECISION
);

CREATE TABLE dim_ptal_lsoa (
    lsoa_code VARCHAR(20) PRIMARY KEY,
    lsoa_name VARCHAR(255),
    borough VARCHAR(100),
    mean_ai DOUBLE PRECISION,
    median_ai DOUBLE PRECISION,
    min_ai DOUBLE PRECISION,
    max_ai DOUBLE PRECISION,
    ptal_2023 VARCHAR(10),
    ptal_score INTEGER
);

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;


SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'fact_journeys'
ORDER BY ordinal_position;


COPY fact_journeys (
    travel_date,
    day_of_week,
    tube_journey_count,
    bus_journey_count,
    source_file,
    calculated_day_of_week,
    year,
    month,
    month_name,
    quarter,
    day_of_month,
    week_of_year,
    is_weekend,
    total_journey_count
)
FROM 'C:/Users/User/Documents/UEL/Project/London Public Transport Intelligence Platform/data/processed/journeys_clean.csv'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER ',',
    ENCODING 'UTF8'
);
SELECT COUNT(*) FROM fact_journeys;


DROP TABLE IF EXISTS fact_numbat_entries;

CREATE TABLE fact_numbat_entries (
    nlc VARCHAR(20),
    asc_code VARCHAR(20),
    station VARCHAR(255),
    fare_zone VARCHAR(20),
    total DOUBLE PRECISION,
    early DOUBLE PRECISION,
    am_peak DOUBLE PRECISION,
    midday DOUBLE PRECISION,
    pm_peak DOUBLE PRECISION,
    evening DOUBLE PRECISION,
    late DOUBLE PRECISION,
    day_type VARCHAR(20),
    time_interval VARCHAR(20),
    entry_count DOUBLE PRECISION
);

SELECT COUNT(*)
FROM fact_numbat_entries;


DROP TABLE IF EXISTS fact_numbat_exits;

CREATE TABLE fact_numbat_exits (
    nlc VARCHAR(20),
    asc_code VARCHAR(20),
    station VARCHAR(255),
    fare_zone VARCHAR(20),
    total DOUBLE PRECISION,
    early DOUBLE PRECISION,
    am_peak DOUBLE PRECISION,
    midday DOUBLE PRECISION,
    pm_peak DOUBLE PRECISION,
    evening DOUBLE PRECISION,
    late DOUBLE PRECISION,
    day_type VARCHAR(20),
    time_interval VARCHAR(20),
    exit_count DOUBLE PRECISION
);
SELECT COUNT(*)
FROM fact_numbat_exits;

SELECT COUNT(*)
FROM fact_station_annualised_2025;

DROP TABLE IF EXISTS fact_station_footfall;
DROP TABLE IF EXISTS fact_station_footfall;

CREATE TABLE fact_station_footfall (
    travel_date DATE,
    station VARCHAR(255),
    entry_tap_count BIGINT,
    exit_tap_count BIGINT,
    source_file VARCHAR(255),
    day_of_week VARCHAR(20),
    calculated_day_of_week VARCHAR(20),
    year INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    day_of_month INTEGER,
    week_of_year INTEGER,
    is_weekend INTEGER,
    total_tap_count BIGINT
);
SELECT COUNT(*) FROM fact_station_footfall;

SELECT 'fact_journeys' AS table_name, COUNT(*) AS rows FROM fact_journeys
UNION ALL
SELECT 'fact_numbat_entries', COUNT(*) FROM fact_numbat_entries
UNION ALL
SELECT 'fact_numbat_exits', COUNT(*) FROM fact_numbat_exits
UNION ALL
SELECT 'fact_station_annualised_2025', COUNT(*) FROM fact_station_annualised_2025
UNION ALL
SELECT 'fact_station_footfall', COUNT(*) FROM fact_station_footfall
UNION ALL
SELECT 'dim_ptal_lsoa', COUNT(*) FROM dim_ptal_lsoa;


SELECT
    MIN(travel_date) AS first_date,
    MAX(travel_date) AS last_date,
    COUNT(DISTINCT travel_date) AS unique_dates,
    COUNT(DISTINCT station) AS unique_stations,
    SUM(entry_tap_count) AS total_entries,
    SUM(exit_tap_count) AS total_exits
FROM fact_station_footfall;


INSERT INTO dim_date (
    date_id,
    year,
    month,
    month_name,
    quarter,
    week_of_year,
    is_weekend
)
SELECT DISTINCT
    travel_date,
    year,
    month,
    month_name,
    quarter,
    week_of_year,
    CASE
        WHEN is_weekend = 1 THEN TRUE
        ELSE FALSE
    END
FROM fact_journeys
ORDER BY travel_date
ON CONFLICT (date_id) DO NOTHING;

SELECT
    COUNT(*) AS date_rows,
    MIN(date_id) AS first_date,
    MAX(date_id) AS last_date
FROM dim_date;

SELECT
    'Station Footfall' AS source,
    COUNT(DISTINCT station) AS unique_stations
FROM fact_station_footfall

UNION ALL

SELECT
    'NUMBAT Entries',
    COUNT(DISTINCT station)
FROM fact_numbat_entries

UNION ALL

SELECT
    'NUMBAT Exits',
    COUNT(DISTINCT station)
FROM fact_numbat_exits

UNION ALL

SELECT
    'Annualised 2025',
    COUNT(DISTINCT station)
FROM fact_station_annualised_2025;

SELECT DISTINCT f.station
FROM fact_station_footfall f
WHERE NOT EXISTS (
    SELECT 1
    FROM fact_numbat_entries n
    WHERE LOWER(TRIM(n.station)) = LOWER(TRIM(f.station))
)
ORDER BY f.station;

SELECT COUNT(DISTINCT f.station) AS unmatched_footfall_stations
FROM fact_station_footfall f
WHERE NOT EXISTS (
    SELECT 1
    FROM fact_numbat_entries n
    WHERE LOWER(TRIM(n.station)) = LOWER(TRIM(f.station))
);

SELECT DISTINCT
    f.station AS footfall_station
FROM fact_station_footfall f
WHERE NOT EXISTS (
    SELECT 1
    FROM fact_numbat_entries n
    WHERE LOWER(TRIM(n.station)) = LOWER(TRIM(f.station))
)
ORDER BY f.station;


CREATE EXTENSION IF NOT EXISTS pg_trgm;


WITH unmatched AS (
    SELECT DISTINCT TRIM(f.station) AS footfall_station
    FROM fact_station_footfall f
    WHERE NOT EXISTS (
        SELECT 1
        FROM fact_numbat_entries n
        WHERE LOWER(TRIM(n.station)) = LOWER(TRIM(f.station))
    )
),
numbat_stations AS (
    SELECT DISTINCT TRIM(station) AS numbat_station
    FROM fact_numbat_entries
)
SELECT
    u.footfall_station,
    best.numbat_station AS suggested_numbat_station,
    ROUND(best.similarity_score::numeric, 3) AS similarity
FROM unmatched u
CROSS JOIN LATERAL (
    SELECT
        n.numbat_station,
        similarity(
            LOWER(u.footfall_station),
            LOWER(n.numbat_station)
        ) AS similarity_score
    FROM numbat_stations n
    ORDER BY similarity_score DESC
    LIMIT 1
) best
ORDER BY u.footfall_station;


DROP TABLE IF EXISTS station_name_mapping;

CREATE TABLE station_name_mapping (
    footfall_station VARCHAR(255) PRIMARY KEY,
    numbat_station VARCHAR(255),
    match_type VARCHAR(50),
    notes VARCHAR(255)
);


INSERT INTO station_name_mapping
(footfall_station, numbat_station, match_type, notes)
VALUES
('Abbey Road DLR', 'Abbey Road', 'manual', 'Mode suffix difference'),
('Balham', 'Balham LU', 'manual', 'LU suffix difference'),
('Bethnal Green', 'Bethnal Green LU', 'manual', 'LU suffix difference'),
('Blackfriars', 'Blackfriars LU', 'manual', 'LU suffix difference'),
('Brixton', 'Brixton LU', 'manual', 'LU suffix difference'),
('Burnham Bucks', 'Burnham', 'manual', 'Location suffix difference'),
('Cannon Street', 'Cannon Street LU', 'manual', 'LU suffix difference'),
('Charing Cross', 'Charing Cross LU', 'manual', 'LU suffix difference'),
('Earls Court', 'Earl''s Court', 'manual', 'Punctuation difference'),
('Edgware Road B', 'Edgware Road (Bak)', 'manual', 'Bakerloo naming difference'),
('Edgware Road C&H', 'Edgware Road (DIS)', 'manual', 'District/Hammersmith naming difference'),
('Elephant & Castle', 'Elephant & Castle LU', 'manual', 'LU suffix difference'),
('Euston', 'Euston LU', 'manual', 'LU suffix difference'),
('Finsbury Park', 'Finsbury Park LU', 'manual', 'LU suffix difference'),
('Hammersmith C&H', 'Hammersmith (H&C)', 'manual', 'H&C naming difference'),
('Hammersmith D&P', 'Hammersmith (DIS)', 'manual', 'District/Piccadilly naming difference'),
('Heathrow Terminal 4', 'Heathrow Terminal 4 LU', 'manual', 'LU suffix difference'),
('Kensington Olympia', 'Kensington (Olympia)', 'manual', 'Naming difference'),
('Kings Cross St Pancras', 'King''s Cross St. Pancras', 'manual', 'Punctuation difference'),
('Langley Berks', 'Langley', 'manual', 'Location suffix difference'),
('Liverpool St NR', 'Liverpool Street NR', 'manual', 'Abbreviation difference'),
('Liverpool Street', 'Liverpool Street LU', 'manual', 'LU suffix difference'),
('London Bridge', 'London Bridge LU', 'manual', 'LU suffix difference'),
('Marylebone', 'Marylebone LU', 'manual', 'LU suffix difference'),
('Pontoon Dock DLR', 'Pontoon Dock', 'manual', 'Mode suffix difference'),
('Queens Park', 'Queen''s Park', 'manual', 'Punctuation difference'),
('Queens Rd Peckham', 'Queens Road Peckham', 'manual', 'Abbreviation difference'),
('Regents Park', 'Regent''s Park', 'manual', 'Punctuation difference'),
('Shepherds Bush Market', 'Shepherd''s Bush Market', 'manual', 'Punctuation difference'),
('St James''s Park', 'St. James''s Park', 'manual', 'Punctuation difference'),
('St Johns Wood', 'St. John''s Wood', 'manual', 'Punctuation difference'),
('St Pauls', 'St. Paul''s', 'manual', 'Punctuation difference'),
('Star Lane DLR', 'Star Lane', 'manual', 'Mode suffix difference'),
('Stratford International', 'Stratford International DLR', 'manual', 'DLR suffix difference'),
('Sydenham SR', 'Sydenham', 'manual', 'Rail suffix difference'),
('Tottenham Hale', 'Tottenham Hale LU', 'manual', 'LU suffix difference'),
('Vauxhall', 'Vauxhall LU', 'manual', 'LU suffix difference'),
('Victoria', 'Victoria LU', 'manual', 'LU suffix difference'),
('W Silvertown', 'West Silvertown', 'manual', 'Abbreviation difference'),
('Walthamstow Queens Road', 'Walthamstow Queen''s Road', 'manual', 'Punctuation difference'),
('Waterloo', 'Waterloo LU', 'manual', 'LU suffix difference'),
('Watford Met', 'Watford', 'manual', 'Metropolitan line suffix'),
('West Croydon', 'West Croydon NR', 'manual', 'NR suffix difference'),
('West Hampstead', 'West Hampstead LO', 'manual', 'LO suffix difference'),
('Woolwich Arsenal DLR', 'Woolwich Arsenal', 'manual', 'Mode suffix difference'),
('Woolwich Arsenal NR', 'Woolwich Arsenal', 'manual', 'Mode suffix difference');


SELECT COUNT(*) FROM station_name_mapping;

WITH unmatched AS (
    SELECT DISTINCT TRIM(f.station) AS footfall_station
    FROM fact_station_footfall f
    WHERE NOT EXISTS (
        SELECT 1
        FROM fact_numbat_entries n
        WHERE LOWER(TRIM(n.station)) = LOWER(TRIM(f.station))
    )
)
SELECT u.footfall_station
FROM unmatched u
LEFT JOIN station_name_mapping m
    ON u.footfall_station = m.footfall_station
WHERE m.footfall_station IS NULL
ORDER BY u.footfall_station;


SELECT DISTINCT station
FROM fact_numbat_entries
WHERE
       station ILIKE '%Bank%'
    OR station ILIKE '%Monument%'
    OR station ILIKE '%Bethnal Green%'
    OR station ILIKE '%Canary Wharf%'
    OR station ILIKE '%Custom House%'
    OR station ILIKE '%Heathrow%'
    OR station ILIKE '%Paddington%'
    OR station ILIKE '%Shepherd%'
    OR station ILIKE '%Woolwich%'
ORDER BY station;


INSERT INTO station_name_mapping
(footfall_station, numbat_station, match_type, notes)
VALUES
('Bank', 'Bank and Monument', 'manual', 'NUMBAT combines Bank and Monument'),
('Monument', 'Bank and Monument', 'manual', 'NUMBAT combines Bank and Monument'),

('Bethnal Green NR', 'Bethnal Green LO', 'manual', 'Rail/Overground station'),

('Canary Wharf', 'Canary Wharf LU', 'manual', 'General footfall name mapped to LU station'),
('Canary Wharf Elizabeth Line', 'Canary Wharf EL', 'manual', 'Elizabeth line station'),

('Custom House Elizabeth Line', 'Custom House EL', 'manual', 'Elizabeth line station'),

('Heathrow T2&3 TfL Rail/HEx', 'Heathrow Terminals 2 & 3 EL', 'manual', 'Elizabeth line/TfL Rail naming'),
('Heathrow T4 TfL Rail/HEx', 'Heathrow Terminal 4 EL', 'manual', 'Elizabeth line/TfL Rail naming'),
('Heathrow T5 TfL Rail/HEx', 'Heathrow Terminal 5 EL', 'manual', 'Elizabeth line/TfL Rail naming'),

('Heathrow Terminal 5', 'Heathrow Terminal 5 LU', 'manual', 'Underground station'),
('Heathrow Terminals 2&3', 'Heathrow Terminals 123 LU', 'manual', 'Underground station naming'),

('Paddington', 'Paddington NR', 'manual', 'Mainline/National Rail station'),
('Paddington EL', 'Paddington TfL', 'manual', 'TfL/Elizabeth line station'),

('Shepherds Bush', 'Shepherd''s Bush LU', 'manual', 'Underground station'),
('Shepherds Bush LO', 'Shepherd''s Bush NR', 'manual', 'Overground/National Rail station'),

('Woolwich Elizabeth Line', 'Woolwich EL', 'manual', 'Elizabeth line station');


SELECT COUNT(*) AS total_mappings
FROM station_name_mapping;

WITH unmatched AS (
    SELECT DISTINCT TRIM(f.station) AS footfall_station
    FROM fact_station_footfall f
    WHERE NOT EXISTS (
        SELECT 1
        FROM fact_numbat_entries n
        WHERE LOWER(TRIM(n.station)) = LOWER(TRIM(f.station))
    )
)
SELECT u.footfall_station
FROM unmatched u
LEFT JOIN station_name_mapping m
    ON u.footfall_station = m.footfall_station
WHERE m.footfall_station IS NULL;

DROP TABLE IF EXISTS dim_station CASCADE;

CREATE TABLE dim_station (
    station_id BIGSERIAL PRIMARY KEY,
    station_name VARCHAR(255) NOT NULL UNIQUE,
    nlc VARCHAR(20),
    asc_code VARCHAR(20),
    fare_zone VARCHAR(20)
);

INSERT INTO dim_station (
    station_name,
    nlc,
    asc_code,
    fare_zone
)
SELECT
    TRIM(station) AS station_name,
    MIN(nlc) AS nlc,
    MIN(asc_code) AS asc_code,
    MIN(fare_zone) AS fare_zone
FROM fact_numbat_entries
WHERE station IS NOT NULL
GROUP BY TRIM(station)
ORDER BY TRIM(station);

SELECT COUNT(*) AS station_count
FROM dim_station;

SELECT *
FROM dim_station
ORDER BY station_name
LIMIT 20;

ALTER TABLE fact_station_footfall
ADD COLUMN station_id BIGINT;

UPDATE fact_station_footfall f
SET station_id = d.station_id
FROM dim_station d
WHERE LOWER(TRIM(f.station)) = LOWER(TRIM(d.station_name));

UPDATE fact_station_footfall f
SET station_id = d.station_id
FROM station_name_mapping m
JOIN dim_station d
    ON LOWER(TRIM(m.numbat_station)) = LOWER(TRIM(d.station_name))
WHERE TRIM(f.station) = m.footfall_station
  AND f.station_id IS NULL;

  SELECT
    COUNT(*) AS unmatched_rows
FROM fact_station_footfall
WHERE station_id IS NULL;

SELECT
    station,
    COUNT(*) AS rows
FROM fact_station_footfall
WHERE station_id IS NULL
GROUP BY station;

ALTER TABLE fact_station_footfall
ADD CONSTRAINT fk_footfall_station
FOREIGN KEY (station_id)
REFERENCES dim_station(station_id);

CREATE INDEX idx_footfall_station_id
ON fact_station_footfall(station_id);

CREATE INDEX idx_footfall_travel_date
ON fact_station_footfall(travel_date);

SELECT
    d.station_name,
    SUM(f.entry_tap_count) AS total_entries,
    SUM(f.exit_tap_count) AS total_exits,
    SUM(f.total_tap_count) AS total_taps
FROM fact_station_footfall f
JOIN dim_station d
    ON f.station_id = d.station_id
GROUP BY d.station_name
ORDER BY total_taps DESC
LIMIT 10;

ALTER TABLE fact_numbat_entries
ADD COLUMN station_id BIGINT;

UPDATE fact_numbat_entries n
SET station_id = d.station_id
FROM dim_station d
WHERE TRIM(n.station) = d.station_name;

SELECT
    COUNT(*) AS total_rows,
    COUNT(station_id) AS matched_rows,
    COUNT(*) - COUNT(station_id) AS unmatched_rows
FROM fact_numbat_entries;

ALTER TABLE fact_numbat_exits
ADD COLUMN station_id BIGINT;

UPDATE fact_numbat_exits n
SET station_id = d.station_id
FROM dim_station d
WHERE TRIM(n.station) = d.station_name;

SELECT
    COUNT(*) AS total_rows,
    COUNT(station_id) AS matched_rows,
    COUNT(*) - COUNT(station_id) AS unmatched_rows
FROM fact_numbat_exits;

ALTER TABLE fact_station_annualised_2025
ADD COLUMN station_id BIGINT;

UPDATE fact_station_annualised_2025 a
SET station_id = d.station_id
FROM dim_station d
WHERE TRIM(a.station) = d.station_name;

SELECT
    COUNT(*) AS total_rows,
    COUNT(station_id) AS matched_rows,
    COUNT(*) - COUNT(station_id) AS unmatched_rows
FROM fact_station_annualised_2025;

SELECT
    mode,
    mnlc,
    masc,
    station,
    annualised_entry_exit
FROM fact_station_annualised_2025
WHERE station_id IS NULL
ORDER BY station;


UPDATE fact_station_annualised_2025 a
SET station_id = d.station_id
FROM dim_station d
WHERE
    (a.station = 'Finsbury Park' AND d.station_name = 'Finsbury Park LU')
 OR (a.station = 'Norwood Jn' AND d.station_name = 'Norwood Junction')
 OR (a.station = 'St James''s Park' AND d.station_name = 'St. James''s Park')
 OR (a.station = 'St John''s Wood' AND d.station_name = 'St. John''s Wood')
 OR (a.station = 'St Paul''s' AND d.station_name = 'St. Paul''s');

 SELECT
    COUNT(*) AS total_rows,
    COUNT(station_id) AS matched_rows,
    COUNT(*) - COUNT(station_id) AS unmatched_rows
FROM fact_station_annualised_2025;

ALTER TABLE fact_numbat_entries
ADD CONSTRAINT fk_numbat_entries_station
FOREIGN KEY (station_id)
REFERENCES dim_station(station_id);

ALTER TABLE fact_numbat_exits
ADD CONSTRAINT fk_numbat_exits_station
FOREIGN KEY (station_id)
REFERENCES dim_station(station_id);

ALTER TABLE fact_station_annualised_2025
ADD CONSTRAINT fk_annualised_station
FOREIGN KEY (station_id)
REFERENCES dim_station(station_id);

CREATE INDEX idx_numbat_entries_station_id
ON fact_numbat_entries(station_id);

CREATE INDEX idx_numbat_exits_station_id
ON fact_numbat_exits(station_id);

CREATE INDEX idx_annualised_station_id
ON fact_station_annualised_2025(station_id);


SELECT
    'fact_station_footfall' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(station_id) AS matched_station_rows
FROM fact_station_footfall

UNION ALL

SELECT
    'fact_numbat_entries',
    COUNT(*),
    COUNT(station_id)
FROM fact_numbat_entries

UNION ALL

SELECT
    'fact_numbat_exits',
    COUNT(*),
    COUNT(station_id)
FROM fact_numbat_exits

UNION ALL

SELECT
    'fact_station_annualised_2025',
    COUNT(*),
    COUNT(station_id)
FROM fact_station_annualised_2025;


SELECT
    year,
    SUM(entry_tap_count) AS total_entries,
    SUM(exit_tap_count) AS total_exits,
    SUM(total_tap_count) AS total_taps,
    ROUND(
        AVG(total_tap_count)::numeric,
        2
    ) AS avg_station_daily_taps
FROM fact_station_footfall
WHERE station_id IS NOT NULL
GROUP BY year
ORDER BY year;

WITH yearly_demand AS (
    SELECT
        year,
        SUM(total_tap_count) AS total_taps
    FROM fact_station_footfall
    WHERE station_id IS NOT NULL
    GROUP BY year
)

SELECT
    year,
    total_taps,
    LAG(total_taps) OVER (
        ORDER BY year
    ) AS previous_year_taps,

    ROUND(
        (
            (total_taps - LAG(total_taps) OVER (ORDER BY year))
            * 100.0
            / NULLIF(LAG(total_taps) OVER (ORDER BY year), 0)
        )::numeric,
        2
    ) AS yoy_change_percent

FROM yearly_demand
ORDER BY year;

SELECT
    year,
    MIN(travel_date) AS first_date,
    MAX(travel_date) AS last_date,
    COUNT(DISTINCT travel_date) AS days,
    SUM(total_tap_count) AS ytd_total_taps
FROM fact_station_footfall
WHERE station_id IS NOT NULL
  AND year IN (2025, 2026)
  AND (
        year = 2026
        OR
        (year = 2025 AND travel_date <= DATE '2025-08-29')
      )
GROUP BY year
ORDER BY year;


WITH ytd AS (
    SELECT
        year,
        SUM(total_tap_count) AS total_taps
    FROM fact_station_footfall
    WHERE station_id IS NOT NULL
      AND year IN (2025, 2026)
      AND (
            year = 2026
            OR (year = 2025 AND travel_date <= DATE '2025-08-29')
          )
    GROUP BY year
)

SELECT
    MAX(CASE WHEN year = 2025 THEN total_taps END) AS taps_2025_ytd,
    MAX(CASE WHEN year = 2026 THEN total_taps END) AS taps_2026_ytd,

    MAX(CASE WHEN year = 2026 THEN total_taps END)
    - MAX(CASE WHEN year = 2025 THEN total_taps END)
        AS absolute_change,

    ROUND(
        (
            (
                MAX(CASE WHEN year = 2026 THEN total_taps END)
                - MAX(CASE WHEN year = 2025 THEN total_taps END)
            ) * 100.0
            / MAX(CASE WHEN year = 2025 THEN total_taps END)
        )::numeric,
        2
    ) AS ytd_change_percent
FROM ytd;


SELECT
    d.station_name,
    d.fare_zone,
    SUM(f.entry_tap_count) AS total_entries,
    SUM(f.exit_tap_count) AS total_exits,
    SUM(f.total_tap_count) AS total_taps,
    ROUND(
        AVG(f.total_tap_count)::numeric,
        0
    ) AS avg_daily_taps
FROM fact_station_footfall f
JOIN dim_station d
    ON f.station_id = d.station_id
WHERE f.year = 2025
GROUP BY
    d.station_id,
    d.station_name,
    d.fare_zone
ORDER BY total_taps DESC
LIMIT 15;


WITH station_year AS (
    SELECT
        d.station_id,
        d.station_name,
        f.year,
        SUM(f.total_tap_count) AS total_taps
    FROM fact_station_footfall f
    JOIN dim_station d
        ON f.station_id = d.station_id
    WHERE f.year IN (2019, 2025)
    GROUP BY
        d.station_id,
        d.station_name,
        f.year
),

comparison AS (
    SELECT
        station_id,
        station_name,

        MAX(CASE
            WHEN year = 2019 THEN total_taps
        END) AS taps_2019,

        MAX(CASE
            WHEN year = 2025 THEN total_taps
        END) AS taps_2025

    FROM station_year
    GROUP BY
        station_id,
        station_name
)

SELECT
    station_name,
    taps_2019,
    taps_2025,

    taps_2025 - taps_2019 AS absolute_change,

    ROUND(
        ((taps_2025 - taps_2019) * 100.0
        / NULLIF(taps_2019, 0))::numeric,
        2
    ) AS change_percent

FROM comparison
WHERE taps_2019 IS NOT NULL
  AND taps_2025 IS NOT NULL
  AND taps_2019 > 0
ORDER BY change_percent DESC
LIMIT 20;

WITH station_year AS (
    SELECT
        d.station_id,
        d.station_name,
        f.year,
        SUM(f.total_tap_count) AS total_taps
    FROM fact_station_footfall f
    JOIN dim_station d
        ON f.station_id = d.station_id
    WHERE f.year IN (2019, 2025)
    GROUP BY
        d.station_id,
        d.station_name,
        f.year
),

comparison AS (
    SELECT
        station_id,
        station_name,
        MAX(CASE WHEN year = 2019 THEN total_taps END) AS taps_2019,
        MAX(CASE WHEN year = 2025 THEN total_taps END) AS taps_2025
    FROM station_year
    GROUP BY station_id, station_name
)

SELECT
    station_name,
    taps_2019,
    taps_2025,
    taps_2025 - taps_2019 AS absolute_change,

    ROUND(
        ((taps_2025 - taps_2019) * 100.0 /
        NULLIF(taps_2019, 0))::numeric,
        2
    ) AS change_percent

FROM comparison
WHERE taps_2019 >= 1000000
  AND taps_2025 IS NOT NULL
ORDER BY change_percent DESC
LIMIT 20;


WITH station_year AS (
    SELECT
        d.station_id,
        d.station_name,
        f.year,
        SUM(f.total_tap_count) AS total_taps
    FROM fact_station_footfall f
    JOIN dim_station d
        ON f.station_id = d.station_id
    WHERE f.year IN (2019, 2025)
    GROUP BY
        d.station_id,
        d.station_name,
        f.year
),

comparison AS (
    SELECT
        station_id,
        station_name,
        MAX(CASE WHEN year = 2019 THEN total_taps END) AS taps_2019,
        MAX(CASE WHEN year = 2025 THEN total_taps END) AS taps_2025
    FROM station_year
    GROUP BY station_id, station_name
)

SELECT
    station_name,
    taps_2019,
    taps_2025,
    taps_2025 - taps_2019 AS absolute_change,

    ROUND(
        ((taps_2025 - taps_2019) * 100.0 /
        NULLIF(taps_2019, 0))::numeric,
        2
    ) AS change_percent

FROM comparison
WHERE taps_2019 >= 1000000
  AND taps_2025 IS NOT NULL
ORDER BY change_percent ASC
LIMIT 20;

CREATE OR REPLACE VIEW vw_daily_network_demand AS

SELECT
    f.travel_date,
    f.year,
    f.month,
    f.month_name,
    f.quarter,
    f.week_of_year,
    f.day_of_week,
    f.is_weekend,

    SUM(f.entry_tap_count) AS total_entries,
    SUM(f.exit_tap_count) AS total_exits,
    SUM(f.total_tap_count) AS total_taps,

    COUNT(DISTINCT f.station_id) AS active_stations

FROM fact_station_footfall f

WHERE f.station_id IS NOT NULL

GROUP BY
    f.travel_date,
    f.year,
    f.month,
    f.month_name,
    f.quarter,
    f.week_of_year,
    f.day_of_week,
    f.is_weekend;


	SELECT COUNT(*)
FROM vw_daily_network_demand;


CREATE OR REPLACE VIEW vw_station_daily_demand AS

SELECT
    f.travel_date,
    f.year,
    f.month,
    f.month_name,
    f.quarter,
    f.week_of_year,
    f.day_of_week,
    f.is_weekend,

    d.station_id,
    d.station_name,
    d.nlc,
    d.asc_code,
    d.fare_zone,

    SUM(f.entry_tap_count) AS entry_taps,
    SUM(f.exit_tap_count) AS exit_taps,
    SUM(f.total_tap_count) AS total_taps

FROM fact_station_footfall f

JOIN dim_station d
    ON f.station_id = d.station_id

GROUP BY
    f.travel_date,
    f.year,
    f.month,
    f.month_name,
    f.quarter,
    f.week_of_year,
    f.day_of_week,
    f.is_weekend,
    d.station_id,
    d.station_name,
    d.nlc,
    d.asc_code,
    d.fare_zone;

	SELECT *
FROM vw_station_daily_demand
ORDER BY travel_date, station_name
LIMIT 20;

SELECT
    COUNT(*) AS rows,
    COUNT(DISTINCT station_id) AS stations,
    MIN(travel_date) AS first_date,
    MAX(travel_date) AS last_date
FROM vw_station_daily_demand;

CREATE OR REPLACE VIEW vw_station_recovery AS

WITH station_year AS (
    SELECT
        d.station_id,
        d.station_name,
        d.fare_zone,
        f.year,
        SUM(f.total_tap_count) AS total_taps
    FROM fact_station_footfall f
    JOIN dim_station d
        ON f.station_id = d.station_id
    WHERE f.year IN (2019, 2025)
    GROUP BY
        d.station_id,
        d.station_name,
        d.fare_zone,
        f.year
),

comparison AS (
    SELECT
        station_id,
        station_name,
        fare_zone,

        MAX(CASE WHEN year = 2019
            THEN total_taps END) AS taps_2019,

        MAX(CASE WHEN year = 2025
            THEN total_taps END) AS taps_2025

    FROM station_year

    GROUP BY
        station_id,
        station_name,
        fare_zone
)

SELECT
    station_id,
    station_name,
    fare_zone,
    taps_2019,
    taps_2025,

    taps_2025 - taps_2019 AS absolute_change,

    ROUND(
        ((taps_2025 - taps_2019) * 100.0
        / NULLIF(taps_2019, 0))::numeric,
        2
    ) AS change_percent,

    CASE
        WHEN taps_2025 > taps_2019 THEN 'Above 2019'
        WHEN taps_2025 < taps_2019 THEN 'Below 2019'
        ELSE 'Same as 2019'
    END AS recovery_status

FROM comparison

WHERE taps_2019 IS NOT NULL
  AND taps_2025 IS NOT NULL;

  SELECT *
FROM vw_station_recovery
ORDER BY change_percent DESC
LIMIT 10;

CREATE OR REPLACE VIEW vw_monthly_network_demand AS

SELECT
    year,
    month,
    month_name,

    DATE_TRUNC(
        'month',
        MIN(travel_date)
    )::date AS month_start,

    SUM(entry_tap_count) AS total_entries,
    SUM(exit_tap_count) AS total_exits,
    SUM(total_tap_count) AS total_taps,

    COUNT(DISTINCT travel_date) AS days_recorded,

    ROUND(
        (
            SUM(total_tap_count)::numeric
            / COUNT(DISTINCT travel_date)
        ),
        0
    ) AS avg_daily_taps

FROM fact_station_footfall

WHERE station_id IS NOT NULL

GROUP BY
    year,
    month,
    month_name

ORDER BY
    year,
    month;

	SELECT *
FROM vw_monthly_network_demand
ORDER BY month_start
LIMIT 12;

SELECT
    COUNT(*) AS months,
    MIN(month_start) AS first_month,
    MAX(month_start) AS last_month
FROM vw_monthly_network_demand;

CREATE OR REPLACE VIEW vw_station_yearly_demand AS

SELECT
    d.station_id,
    d.station_name,
    d.fare_zone,
    f.year,

    SUM(f.entry_tap_count) AS total_entries,
    SUM(f.exit_tap_count) AS total_exits,
    SUM(f.total_tap_count) AS total_taps,

    COUNT(DISTINCT f.travel_date) AS days_recorded,

    ROUND(
        (
            SUM(f.total_tap_count)::numeric
            / COUNT(DISTINCT f.travel_date)
        ),
        0
    ) AS avg_daily_taps

FROM fact_station_footfall f

JOIN dim_station d
    ON f.station_id = d.station_id

GROUP BY
    d.station_id,
    d.station_name,
    d.fare_zone,
    f.year;


	SELECT *
FROM vw_station_yearly_demand
WHERE year = 2025
ORDER BY total_taps DESC
LIMIT 10;

SELECT
    COUNT(*) AS rows,
    COUNT(DISTINCT station_id) AS stations,
    MIN(year) AS first_year,
    MAX(year) AS last_year
FROM vw_station_yearly_demand;

CREATE OR REPLACE VIEW vw_numbat_station_time_demand AS

SELECT
    e.station_id,
    d.station_name,
    d.fare_zone,
    e.day_type,
    e.time_interval,

    e.entry_count,
    x.exit_count,

    COALESCE(e.entry_count, 0)
        + COALESCE(x.exit_count, 0) AS total_passenger_activity

FROM fact_numbat_entries e

JOIN fact_numbat_exits x
    ON e.station_id = x.station_id
    AND e.day_type = x.day_type
    AND e.time_interval = x.time_interval

JOIN dim_station d
    ON e.station_id = d.station_id;

	SELECT
    COUNT(*) AS rows,
    COUNT(DISTINCT station_id) AS stations,
    COUNT(DISTINCT day_type) AS day_types,
    COUNT(DISTINCT time_interval) AS time_intervals
FROM vw_numbat_station_time_demand;