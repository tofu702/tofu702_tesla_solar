import csv
import datetime
import dataclasses
import pydantic


class DailyData(pydantic.BaseModel):
  date: datetime.date = None
  home_kwh: float = None
  from_powerwall_kwh: float = None
  solar_energy_kwh: float = None
  from_grid_kwh: float = None
  to_grid_kwh: float = None


def parse_datetime_str_to_date(datetime_str: str) -> datetime.date:
  date_str = datetime_str.split("T")[0]
  dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
  return dt.date()


def parse_csv_file(file_path: str) -> list[DailyData]:
  """Parse a CSV file and return a list of EnergyReading objects"""
  parsed_daily_data = []

  with open(file_path, 'r') as csvfile:
    # Skip the first line (header line with line numbers)
    next(csvfile)

    reader = csv.reader(csvfile)

    for row in reader:
      date = parse_datetime_str_to_date(row[0])
      home_kwh = float(row[1])
      from_powerwall_kwh = float(row[2])
      solar_energy_kwh = float(row[3])
      from_grid_kwh = float(row[4])
      to_grid_kwh = float(row[5])

      reading = DailyData(date=date, home_kwh=home_kwh, from_powerwall_kwh=from_powerwall_kwh,
                          solar_energy_kwh=solar_energy_kwh, from_grid_kwh=from_grid_kwh, to_grid_kwh=to_grid_kwh)
      parsed_daily_data.append(reading)
  return parsed_daily_data