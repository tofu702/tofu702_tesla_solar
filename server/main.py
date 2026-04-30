import datetime
import pydantic

import fastapi.staticfiles
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

import server.lib.battery_simulator
import server.lib.sun_data
import server.lib.tesla_monthly_data_parser


TESLA_DATA_DIR_PATH = "/Users/steven/github/tofu702_tesla_solar/example_data/"

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

class DailyBatterySimulatorResponse(pydantic.BaseModel):
    days_to_simulated_result: dict[str, server.lib.battery_simulator.DailyBatterySimResult]

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

@app.get("/battery_simulator/day_range")
async def simulate_battery_for_range(start_date: datetime.date,
                                     end_date: datetime.date,
                                     simulated_battery_capacity_kwh: float,
                                     solar_multiplier: float = 1.0,
                                     ) -> DailyBatterySimulatorResponse:
    format = "%Y-%m-%d"
    num_days = (end_date - start_date).days
    if num_days < 0:
        raise ValueError("end_date: %s < start_date: %s" % (end_date, start_date))
    parser = server.lib.tesla_monthly_data_parser.TeslaDataParser(TESLA_DATA_DIR_PATH)
    battery_simulator = server.lib.battery_simulator.BatterySimulator()
    all_day_solar_data = parser.data_for_date_range(start_date, end_date)
    battery_sim_data = battery_simulator.simulate_day_range(solar_data_for_days=all_day_solar_data,
                                                            simulated_battery_capacity_kwh=simulated_battery_capacity_kwh,
                                                            solar_multiplier=solar_multiplier)
    days_to_sim_results = dict([(x.date.strftime(format), x) for x in battery_sim_data])
    return DailyBatterySimulatorResponse(days_to_simulated_result=days_to_sim_results)

@app.get("/battery_simulator/day_range_csv")
async def simulate_battery_for_range_csv(start_date: datetime.date,
                                     end_date: datetime.date,
                                     simulated_battery_capacity_kwh: float,
                                     solar_multiplier: float = 1.0,
                                     ):
    num_days = (end_date - start_date).days
    if num_days < 0:
        raise ValueError("end_date: %s < start_date: %s" % (end_date, start_date))
    parser = server.lib.tesla_monthly_data_parser.TeslaDataParser(TESLA_DATA_DIR_PATH)
    battery_simulator = server.lib.battery_simulator.BatterySimulator()
    all_day_solar_data = parser.data_for_date_range(start_date, end_date)
    battery_sim_data = battery_simulator.simulate_day_range(solar_data_for_days=all_day_solar_data,
                                                            simulated_battery_capacity_kwh=simulated_battery_capacity_kwh,
                                                            solar_multiplier=solar_multiplier)
    csv_data = battery_simulator.simulated_days_to_csv(battery_sim_data)
    headers = {'Content-Disposition': 'attachment; filename="battery_simulation.csv"'}
    return StreamingResponse(content=csv_data, headers=headers, media_type="test/csv")

@app.get("/monthly_data")
async def monthly_data() -> list[server.lib.tesla_monthly_data_parser.MonthlyData]:
    """Return monthly totals for all months that have data"""
    parser = server.lib.tesla_monthly_data_parser.TeslaDataParser(TESLA_DATA_DIR_PATH)
    return parser.monthly_data()
