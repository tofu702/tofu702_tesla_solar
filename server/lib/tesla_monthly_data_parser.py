import csv
import datetime
import dataclasses
import itertools
import os.path

import pydantic


class DailyData(pydantic.BaseModel):
  date: datetime.date = None
  home_kwh: float = None
  from_powerwall_kwh: float = None
  solar_energy_kwh: float = None
  from_grid_kwh: float = None
  to_grid_kwh: float = None


class TeslaDataParser:
  def __init__(self, data_file_dirpath: str):
    self.data_file_dirpath = data_file_dirpath

  @classmethod
  def _parse_datetime_str_to_date(cls, datetime_str: str) -> datetime.date:
    date_str = datetime_str.split("T")[0]
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return dt.date()

  def _parse_csv_file(self, file_path: str) -> list[DailyData]:
    """Parse a CSV file and return a list of EnergyReading objects"""
    parsed_daily_data = []

    with open(file_path, 'r') as csvfile:
      # Skip the first line (header line with line numbers)
      next(csvfile)

      reader = csv.reader(csvfile)

      for row in reader:
        date = self._parse_datetime_str_to_date(row[0])
        home_kwh = float(row[1])
        from_powerwall_kwh = float(row[2])
        solar_energy_kwh = float(row[3])
        from_grid_kwh = float(row[4])
        to_grid_kwh = float(row[5])

        reading = DailyData(date=date, home_kwh=home_kwh, from_powerwall_kwh=from_powerwall_kwh,
                            solar_energy_kwh=solar_energy_kwh, from_grid_kwh=from_grid_kwh, to_grid_kwh=to_grid_kwh)
        parsed_daily_data.append(reading)
    return parsed_daily_data

  def _date_range_to_month_filenames(self, start_date: datetime.date, end_date: datetime.date) -> list[str]:
    """Return list of form ['2025_10', '2025_11'...]"""
    cur_first_day_of_month = start_date.replace(day=1)
    result = []
    while cur_first_day_of_month < end_date:
      cur_month_str = cur_first_day_of_month.strftime("%Y_%m.csv")
      result.append(cur_month_str)
      a_day_next_month = cur_first_day_of_month + datetime.timedelta(days=32)
      cur_first_day_of_month = a_day_next_month.replace(day=1)
    return result

  def data_for_date_range(self, start_date: datetime.date, end_date: datetime.date) -> list[DailyData]:
    month_filenames = self._date_range_to_month_filenames(start_date, end_date)
    month_filepaths = [os.path.join(self.data_file_dirpath, x) for x in month_filenames]
    all_data_for_months_unflattened = [self._parse_csv_file(x) for x in month_filepaths]
    all_data_for_months_flattened = itertools.chain.from_iterable(all_data_for_months_unflattened)
    data_for_relevant_days_only = [x for x in all_data_for_months_flattened \
                                   if (x.date >= start_date and x.date <= end_date)]
    return data_for_relevant_days_only

def main():
  dir_path = "/Volumes/github/tofu702_tesla_solar/example_data/"

  parser = TeslaDataParser(dir_path)
  for x in parser.data_for_date_range(datetime.date(2024, 11, 30),
                                    datetime.date(2025, 3, 15)):
    print(x)


if __name__ == "__main__":
  main()