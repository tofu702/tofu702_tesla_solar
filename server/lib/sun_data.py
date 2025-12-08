import datetime
import math
import pydantic
import suncalc
import typing
import zoneinfo

class SunStats(pydantic.BaseModel):
    """Pydantic model for basic sun statistics for a day"""
    day_length_hours: typing.Optional[float] = None
    noon_altitude_deg: typing.Optional[float] = None
    sunrise_time: typing.Optional[datetime.time] = None
    noon_time: typing.Optional[datetime.time] = None
    sunset_time: typing.Optional[datetime.time] = None


def rad_to_deg(rad):
  return rad * 180 / math.pi

def compute_noon_altitude_deg(latitude, longitude, sun_times: typing.Dict[str, datetime.datetime]) -> float:
    solar_noon_utc = sun_times["solar_noon"].replace(tzinfo=datetime.UTC)
    solar_noon_position = suncalc.get_position(solar_noon_utc, longitude, latitude)
    noon_alt_deg = rad_to_deg(solar_noon_position["altitude"])
    print("Noon: %s" % solar_noon_utc)
    return noon_alt_deg

def convert_to_tz(dt:datetime.datetime, timezone: datetime.tzinfo) -> datetime.datetime:
    return dt.replace(tzinfo=datetime.UTC).astimezone(timezone)

def convert_time_delta_to_hours(timedelta: datetime.timedelta) -> float:
    whole_hours = timedelta.total_seconds() / 3600
    remaining_sec = timedelta.total_seconds() - whole_hours * 3600
    remaining_part_of_hour = remaining_sec / 3600.0
    return whole_hours + remaining_part_of_hour

def calculate_sun_stats_for_date_str(date_str: str, latitude=37.5585485, longitude=-121.9481288,
                                     timezone_str="America/Los_Angeles") -> SunStats:
    """
    Calculate basic sun statistics for a given date.
    
    Args:
        date_str: Date string in format YYYY-MM-DD
        latitude / longitude: Default Fremont, CA
        timezone_str: Default to America/Los_Angeles
        
    Returns:
        SunStats: Pydantic model with sun statistics
    """
    # Parse the date string
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    return calculate_sun_stats_for_datetime(date, latitude, longitude, timezone_str)


def calculate_sun_stats_for_datetime(date: datetime.date, latitude=37.5585485, longitude=-121.9481288,
                                     timezone_str="America/Los_Angeles") -> SunStats:
    tz = zoneinfo.ZoneInfo(timezone_str)
    # Get sun times for the date
    sun_times = suncalc.get_times(date, longitude, latitude)
    # Calculate day length (difference between sunset and sunrise)
    sunrise = convert_to_tz(sun_times['sunrise'], tz)
    noon = convert_to_tz(sun_times['solar_noon'], tz)
    sunset = convert_to_tz(sun_times['sunset'], tz)
    # Calculate day length in hours and minutes
    day_length = sunset - sunrise
    noon_alt_deg = compute_noon_altitude_deg(latitude, longitude, sun_times)
    return SunStats(
        day_length_hours=convert_time_delta_to_hours(day_length),
        noon_altitude_deg=noon_alt_deg,
        sunrise_time=sunrise.time(),
        noon_time=noon.time(),
        sunset_time=sunset.time()
    )