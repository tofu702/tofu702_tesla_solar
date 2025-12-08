import fastapi.staticfiles
from fastapi import FastAPI
import server.lib.sun_data

import datetime
import pydantic
import typing
from server.lib.sun_data import calculate_sun_stats_for_date_str

# Create FastAPI instance
app = FastAPI(
    title="Tesla Solar Stats Tool",
    description="A Tool For Getting Tesla Solar Related Long Term Stats",
    version="0.1.0"
)

class SunStatsForRangeResponse(pydantic.BaseModel):
    days_to_stats: dict[str, server.lib.sun_data.SunStats]

# Root endpoint
@app.get("/")
#async def root():
#    return {"message": "Welcome to the Barebones FastAPI Server"}
async def read_root():
    """Says Hello World"""
    return {"Hello": "World"}

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
    num_days = (end_date_d - start_date_d).days
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

# Example API endpoint
# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}