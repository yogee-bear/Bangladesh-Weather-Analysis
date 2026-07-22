# Bangladesh Weather Dashboard (2016–2025)

A Python → SQL → Tableau pipeline that turns 10 years of hourly weather data into an interactive dashboard.

[Link to Tableau Public
](https://public.tableau.com/views/bang-weather-dashboard/TemperatureWaterImpacts?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Data Source

[Bangladesh Weather Dataset 2016-2025](https://www.kaggle.com/datasets/faizahossain/bangladesh-weather-dataset2016-2025) (Kaggle)

- **350,880 hourly rows** across 4 cities: Dhaka, Chittagong, Sylhet, Rajshahi
- Date range: 2015-12-31 to 2026-01-01
- Fields: temperature, humidity, rainfall, pressure, cloud cover, wind speed/direction, soil temperature

## Pipeline Overview

```
CSV (Kaggle) → pandas (clean) → SQLite (aggregate) → CSV export → Tableau (visualize)
```

### 1. Clean the data (Python / pandas)

- Loaded `bangladesh_weather_2016_2025.csv`
- Converted the `time` column from text to a proper `datetime` type
- Renamed columns to be shorter and self-explanatory, e.g. `temperature_2m` → `temp_c`,
  `relative_humidity_2m` → `humidity_pct`
- Verified data integrity: 0 duplicate rows, 0 missing hours per city

### 2. Aggregate the data (SQL / SQLite)

- Loaded the cleaned hourly data into a SQLite database (`weather.db`) as the table `weather_hourly`
- Built a `weather_monthly` view that rolls hourly readings up to one row per city per month:
  - `avg_temp_c`, `min_temp_c`, `max_temp_c`
  - `total_rain_mm`
  - `avg_humidity_pct`, `avg_cloud_cover_pct`, `avg_wind_speed_kmh`
- Used `strftime('%Y-%m', time)` to group by calendar month, and `DROP VIEW IF EXISTS` before
  `CREATE VIEW` so the script can be safely re-run
- Result: **480 rows** (4 cities × ~120 months) — a dashboard-friendly size, down from 350K raw rows

### 3. Export for Tableau

- Pulled the `weather_monthly` view back into pandas with `pd.read_sql(...)`
- Exported to `weather_monthly.csv` for Tableau to connect to directly (no ODBC driver needed)

### 4. Build the dashboard (Tableau)

- Connected Tableau to `weather_monthly.csv`
- Set `year_month` as a **continuous** Date field (critical: the *discrete* version buckets all
  10 years of "Januarys" etc. together and produces a zigzag chart instead of a timeline)
- Built out the sheets and assembled them into one dashboard:
  - **Temp Trend** — `year_month` (continuous, Month) on Columns, `avg_temp_c` on Rows, `city`
    on Color, Line mark — shows 10 years of seasonal temperature cycles per city
  - **Rainfall** — monthly `total_rain_mm` by city
  - **City Comparison** — `city` on Columns, `avg_temp_c` on Rows, Bar mark — average temperature
    side by side across the four cities
  - Combined all sheets onto a single dashboard canvas with a shared `city` filter (applied to
    all worksheets using the data source) so selecting a city updates every chart at once
- Status: **complete**

## Key Findings So Far

- All four cities show a clear annual cycle: cold trough around Dec/Jan, hot peak around Apr/May
- **Rajshahi** has the most extreme swings — highest summer peaks and lowest winter dips
- **Chittagong** (coastal) is the most temperature-moderate of the four, consistent with the
  cooling/moderating effect of coastal water

## Files

| File | Description |
|---|---|
| `bangladesh_weather_2016_2025.csv` | Raw source data from Kaggle |
| `weather.db` | SQLite database with `weather_hourly` table and `weather_monthly` view |
| `weather_monthly.csv` | Aggregated monthly data, exported for Tableau |
| Tableau workbook (`Book1.twb`/`.twbx`) | Finished dashboard: Temp Trend, Rainfall, and City Comparison charts, linked by a shared city filter |

## Tools Used

- **Python** (pandas, sqlite3) — data cleaning and pipeline scripting
- **SQL** (SQLite) — aggregation from hourly to monthly grain
- **Tableau Public** — interactive visualization and dashboard
