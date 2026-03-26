import requests
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CITY_NAME = "Warsaw"
LATITUDE = 52.2297
LONGITUDE = 21.0122
TIMEZONE = "Europe/Warsaw"

OUTPUT_DIR = Path("output")
CSV_FILE = OUTPUT_DIR / "forecast.csv"
TXT_FILE = OUTPUT_DIR / "summary.txt"
CHART_FILE = OUTPUT_DIR / "temperature_chart.png"


def fetch_weather_data():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": 7,
        "timezone": TIMEZONE
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def build_dataframe(data):
    daily = data["daily"]

    df = pd.DataFrame({
        "date": daily["time"],
        "temp_min_c": daily["temperature_2m_min"],
        "temp_max_c": daily["temperature_2m_max"],
        "precipitation_sum_mm": daily["precipitation_sum"]
    })

    return df


def save_csv(df):
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_csv(CSV_FILE, index=False)


def save_summary(data, df):
    OUTPUT_DIR.mkdir(exist_ok=True)

    current = data["current"]
    current_temp = current["temperature_2m"]
    current_wind = current["wind_speed_10m"]

    avg_max_temp = df["temp_max_c"].mean()
    avg_min_temp = df["temp_min_c"].mean()

    rainiest_day = df.loc[df["precipitation_sum_mm"].idxmax()]
    warmest_day = df.loc[df["temp_max_c"].idxmax()]

    summary = f"""
Weather report for {CITY_NAME}

Current weather:
- Temperature: {current_temp:.1f} °C
- Wind speed: {current_wind:.1f} km/h

7-day forecast overview:
- Average minimum temperature: {avg_min_temp:.1f} °C
- Average maximum temperature: {avg_max_temp:.1f} °C
- Warmest day: {warmest_day['date']} ({warmest_day['temp_max_c']:.1f} °C)
- Rainiest day: {rainiest_day['date']} ({rainiest_day['precipitation_sum_mm']:.1f} mm)

Detailed daily forecast:
""".strip()

    for _, row in df.iterrows():
        summary += (
            f"\n- {row['date']}: "
            f"min {row['temp_min_c']:.1f} °C, "
            f"max {row['temp_max_c']:.1f} °C, "
            f"precipitation {row['precipitation_sum_mm']:.1f} mm"
        )

    with open(TXT_FILE, "w", encoding="utf-8") as file:
        file.write(summary)


def save_chart(df):
    OUTPUT_DIR.mkdir(exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["temp_min_c"], marker="o", label="Min temperature")
    plt.plot(df["date"], df["temp_max_c"], marker="o", label="Max temperature")

    plt.title(f"7-Day Temperature Forecast for {CITY_NAME}")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close()


def print_console_output(data, df):
    current = data["current"]

    print(f"\nCurrent weather for {CITY_NAME}:")
    print(f"Temperature: {current['temperature_2m']:.1f} °C")
    print(f"Wind speed: {current['wind_speed_10m']:.1f} km/h")

    print("\n7-day forecast:")
    for _, row in df.iterrows():
        print(
            f"{row['date']} | "
            f"min: {row['temp_min_c']:.1f} °C | "
            f"max: {row['temp_max_c']:.1f} °C | "
            f"precipitation: {row['precipitation_sum_mm']:.1f} mm"
        )

    print("\nFiles generated:")
    print(f"- {CSV_FILE}")
    print(f"- {TXT_FILE}")
    print(f"- {CHART_FILE}")


def main():
    try:
        data = fetch_weather_data()
        df = build_dataframe(data)
        save_csv(df)
        save_summary(data, df)
        save_chart(df)
        print_console_output(data, df)
    except requests.exceptions.RequestException as e:
        print(f"Error while connecting to the API: {e}")
    except KeyError as e:
        print(f"Unexpected API response format. Missing field: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
