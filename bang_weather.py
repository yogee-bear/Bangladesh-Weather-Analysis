import pandas as pd

bang = pd.read_csv('bangladesh_weather_2016_2025.csv')

bang['time'] = pd.to_datetime(bang['time'])

bang = bang.rename(columns={
    'temperature_2m': 'temp_c',
    'relative_humidity_2m': 'humidity_pct',
    'rain': 'rain_mm',
    'pressure_msl': 'pressure_hpa',
    'cloud_cover': 'cloud_cover_pct',
    'wind_speed_100m': 'wind_speed_kmh',
    'wind_direction_100m': 'wind_dir_deg',
    'soil_temperature_100_to_255cm': 'soil_temp_c'
})

dupes = bang.duplicated(subset=['time','city'], keep=False).sum()
print(f"Number of duplicate rows based on 'time' and 'city': {dupes}")

for city in bang['city'].unique():
    city_data = bang[bang['city'] == city].sort_values(by = 'time')
    expected_hours = pd.date_range(start=city_data['time'].min(), end=city_data['time'].max(), freq='h')
    missing_hours = expected_hours.difference(city_data['time'])
    print(f"City: {city}, Missing hours: {len(missing_hours)}")

import sqlite3

conn = sqlite3.connect('weather.db')

bang.to_sql('weather_hourly', conn, if_exists='replace', index=False)

count = conn.execute("SELECT COUNT(*) FROM weather_hourly").fetchone()[0]
print(f"Rows loaded into SQL: {count}")

conn.execute("DROP VIEW IF EXISTS weather_monthly")

conn.execute("""
CREATE VIEW weather_monthly AS
SELECT
    city,
    strftime('%Y-%m', time) AS year_month,
    ROUND(AVG(temp_c), 2) AS avg_temp_c,
    ROUND(MIN(temp_c), 2) AS min_temp_c,
    ROUND(MAX(temp_c), 2) AS max_temp_c,
    ROUND(SUM(rain_mm), 2) AS total_rain_mm,
    ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
    ROUND(AVG(cloud_cover_pct), 2) AS avg_cloud_cover_pct,
    ROUND(AVG(wind_speed_kmh), 2) AS avg_wind_speed_kmh
FROM weather_hourly
GROUP BY city, strftime('%Y-%m', time);
""")

conn.commit()  # save the view to the database file

print("View created.")

monthly_bang = pd.read_sql("SELECT * FROM weather_monthly ORDER BY city, year_month", conn)
print(monthly_bang.shape)
print(monthly_bang.head(10))

monthly_bang.to_csv('weather_monthly.csv', index=False)
print("Exported weather_monthly.csv — ready for Tableau")

