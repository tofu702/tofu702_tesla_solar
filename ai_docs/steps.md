# Step 1: Write a more advanced grapher
Read the file in `server/static/day_data.html` and the API docs in `openapi.json`. Create a new `day_data_unified.html` in `server/static` that:
* Unifies both existing graphs in `day_data.html` in to a single graph
* Graphs the solar data (in kwh) using a separate y-axis from the day length (in hours)
* Has check boxes for enabling or disabling the lines.

# Step 2: Add Additional Metrics
Consult `openapi.json` we should make several more lines available
* Home Usage (kWh): From home_kwh
* Grid Usage (kWh): From from_grid_kwh
* Grid Exports (kWh): From to_grid_kwh
* Powerwall Usage (kWh): From from_powerwall_kwh

# Step 3: Year over year comparison
Allow the user to optionally select a secondary year to compare the current data to. The lines for the secondary year should be dashed, but the line colors should be the same for each metric. Place the UI for selecting the secondary year beneath the current year selector and have a control to turn the secondary year on or off.

# Step 4: Aggregation Lines Moving Averages and Moving Maxes
We will add an additional optional aggregation line--currently either a "Moving Average" and "Moving Max" modes. These modes add additional lines to the graphs for the currently selected metrics for the primary year and if selected the secondary year.

There should be 5 options:
* None
* 7 Day Moving Average
* 15 Day Moving Average
* 7 Day Moving Max

Notes:
* Do not apply these to Day Length (no aggregation lines for day length should be drawn)
* We will need to fetch additional data beyond the current month to compute these aggregations.
  * If all data isn't available to fully compute an aggregation for a particular day, do not draw a data point for that day (for example: if only 6 days can be averaged on a day, there should be no data point for the 7 day moving average)

# Step 5: Monthly Summary Data API
Modify `main.py` and `tesla_monthly_data_parser.py` to return monthly totals for all months for which we have data (IE: files exists in the data_file_dirpath).

Notes:
* Leverage the existing `_parse_csv_file` function; do write a second csv parser.
* The pydantic object for the API should return structures similar to Daily Data but:
   * Instead of `date` specify `first_day_of_month`
   * Note that all the fields should be cummulative for the entire month. For example: `home_kwh` should be the total kwh for the home that month.

# Step 6: Front End For Monthly Data
Create a new `static/monthly_comparison.html` that shows monthly data for each month as a bar graph. 

Notes
* Read `openapi.json` for the `/monthly_data` API spec.
* Metric selection should be based on the `day_data_unified.html`, but radio buttons should be used so that only one metric may be selected at a time.
  * Day Length should not be displayed so there is no need to call the sun_data APIs. 
* The Bar Chart should work as follows
  * The x axis labels should be the "Month of Year"
  * The y axis is (obviously) in kwh
  * For a particular month there should be separate bars for each year. For instance, there might be adjacent bars for January 2024, January 2025 and January 2026.
  * All bars for the same year should be the same color.