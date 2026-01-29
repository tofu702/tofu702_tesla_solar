import fastapi.staticfiles
from fastapi import FastAPI
import server.lib.sun_data
import server.lib.tesla_monthly_data_parser

import datetime
import pydantic


TESLA_DATA_DIR_PATH = "/Volumes/github/tofu702_tesla_solar/example_data/"

# Create FastAPI instance
app = FastAPI(
    title="Tesla Solar Stats Tool",
    description="A Tool For Getting Tesla Solar Related Long Term Stats",
    version="0.1.0"
)

class SunStatsForRangeResponse(pydantic.BaseModel):
    days_to_stats: dict[str, server.lib.sun_data.SunStats]

class DayDataForRangeResponse(pydantic.BaseModel):
    days_to_data: dict[str, server.lib.tesla_monthly_data_parser.DailyData]

# Root endpoint
@app.get("/")
async def read_root():
    return fastapi.responses.RedirectResponse("static/main.html")

app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/sun/range")
async def sun_data_for_range(start_date: str, end_date: str) -> SunStatsForRangeResponse:
    format = "%Y-%m-%d"
    days_to_stats = {}
    start_date_d = datetime.date.strptime(start_date, format)
    end_date_d = datetime.date.strptime(end_date, format)
    num_days = (end_date_d - start_date_d).days + 1
    if num_days < 0:
        raise ValueError("end_date: %s < start_date: %s" % (end_date, start_date))
    for cur_day_num in range(num_days):
        current_date: datetime.date = start_date_d + datetime.timedelta(days=cur_day_num)
        current_dt = datetime.datetime.combine(current_date, datetime.datetime.min.time())
        current_date_str = str(current_date)
        days_to_stats[current_date_str] = server.lib.sun_data.calculate_sun_stats_for_datetime(current_dt)
    return SunStatsForRangeResponse(days_to_stats=days_to_stats)


@app.get("/sun/date/{date_str}")
async def sun_data_for_date(date_str: str) -> server.lib.sun_data.SunStats:
    sun_stats = server.lib.sun_data.calculate_sun_stats_for_date_str(date_str)
    return sun_stats

@app.get("/example_daily_data")
async def example_daily_data() -> list[server.lib.tesla_monthly_data_parser.DailyData]:
    csv_file_path = "/Volumes/github/tofu702_tesla_solar/example_data/2024_10.csv"
    daily_data = server.lib.tesla_monthly_data_parser.parse_csv_file(csv_file_path)
    return daily_data

@app.get("/day_data/range")
async def day_data_for_range(start_date: str, end_date: str) -> DayDataForRangeResponse:
    format = "%Y-%m-%d"
    start_date_d = datetime.date.strptime(start_date, format)
    end_date_d = datetime.date.strptime(end_date, format)
    num_days = (end_date_d - start_date_d).days
    if num_days < 0:
        raise ValueError("end_date: %s < start_date: %s" % (end_date, start_date))
    parser = server.lib.tesla_monthly_data_parser.TeslaDataParser(TESLA_DATA_DIR_PATH)
    all_day_data = parser.data_for_date_range(start_date_d, end_date_d)
    days_to_data = dict([(x.date.strftime(format), x) for x in all_day_data])
    return DayDataForRangeResponse(days_to_data=days_to_data)
