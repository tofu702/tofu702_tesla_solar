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

# Step 7: Add [Only] Shortcut Buttons for the Daily Data
In `static/day_data_unified.html` add buttons labeled "[Only]" for each of the metrics in the "Chart Visibility Controls". These buttons should uncheck all of the other boxes except for that metric which it should explicitly check.

# Step 8: Change Monthly Data UI to Year Checkboxs
In `static/monthly_comparison.html` change the UI for year selection (in the `<div class="controls">`) to be check boxes for the relevant years (2024, 2025, 2026) and remove the other UI--`<select>` element and comparison mode should go away. Obviously we should now allow an arbitrary number of years to be compared.

# Step 9: Create a new All Time Data Web Page
Create new page for all time data in `static/all_time.html`.

## Total and Daily Average Table
Shows the following in table format. Totals should be in the first column and daily averages should be in the second column.:
* Total Days: Total Days of Data
* Total Solar Energy and Daily Average Solar Energy
* Total Home Usage and Daily Average Home Usage
* Total Grid Usage and Daily Average Grid Usage
* Total Grid Exports and Daily Average Grid Exports
* Total Powerwall Usage and Daily Average Powerwall Usage
* "Total Production - Exports": Should be "Total Solar Energy" - "Grid Exports" and the corresponding daily average

## Other All Time Stats
Show these in a separate table
* "% Production": Compute as percentage "Total Solar Energy" / "Total Home Usage"
* "% Production - Exports": Compute as Percentage "Total Production - Exports" / "Total Home Usage"
* "# Days w/ > 2 kWh in Exports": These should be days without at least 2 kWh in exports 
* "Total Powerwall Cycles": "Total Powerwall Usage" / 13.5. Round to the nearest integer

## Notes:
* Call `/monthly_data` and aggregate to produce this
* Design this is such a way that it could be added to the existing `main.html` in the future, but keep it separate for now.

# Step 10: Create a yearly day range view
Create new `static/year_over_year_by_day.html`. This file should be based on `static/day_data_unified.html` but has several key distinctions
* It takes arbitrary start (month, day) and end (month, day) tuples
* It has check boxes for the years to show

## More Details
* Default to a full calendar year range (Jan 1 through Dec 31 inclusive)
* All years that are checked should be shown the graph.
* Use similar aggregation controls to `day_data_unified.html` including the "Only Show Aggregates" checkbox

# Step 11: Battery Simulator By Day
Create a new "Battery Simulator" page that simulates the behavior of the system with a user selected number of Powerwall batteries.

## Notes
* For the server API, see `ai_docs/openapi.json` and look for `/battery_simulator/day_range`
* The overall structure of this page should be like `server/static/year_over_year_by_day.html`
* The user should be able to click checkboxes to compare several powerwall options. Options for 0, 1, 2, 3 or 4 powerwalls should be displayed. Each Powerwall has a simulated_battery_capacity of 13.5 kWh, so 2 Powerwalls for example would have a 27 kWh total capacity.
* Each checked powerwall box will require a different call to the battery simulator API.
* Users should only be able to select a single metric to compare (radio buttons, not check boxes)
* Same aggregation controls as `server/static/year_over_year_by_day.html`

# Metric for the user to select
* "Home Usage": `home_kwh`
* "Solar Data": `solar_energy_kwh`
* "End of Day Battery": `eod_battery_kwh`
* "Battery Usage": `battery_usage_kwh`
* "Grid Usage": `from_grid_kwh` (checked)

# Step 12: Top Navigation
* Add a unified tab bar to navigate between the main pages. Every page in the group should have the same nav:
  * `all_time.html`
  * `battery_simulator.html`
  * `day_data_unified.html`
  * `monthly_comparison.html`
  * `year_over_year_by_day.html.`
* Get the page names from `main.html`, but don't add the top nav to `main.html`
* Try to factor this code out so that we don't have to modify the pages individually
* Make this approach modular enough to support additional pages

# Step 13: Add Solar Simulation to Battery Simulator
Replace the "Powerwalls" section of the simulator with "Scenarios" that support both a powerwall count and a solar multiplier (how much solar power increases or decreases relative to the data). Support up to 4 scenarios, including the "Original". 
* Scenarios should be expressed as a table with three items in each row:
  * Enabled (Checkbox)
  * Number of Powerwalls (Integer text field), defaults to 1
  * Solar multiplier (float text field), defaults to 1.0
* The first scenario is the "Original". It consists of 1 powerwall (editable) and a solar multiplier of 1.0 that is fixed.
* The remaining scenarios should default be 
  * Powerwalls=2, solar_multiplier=1.0
  * Powerwalls=3, solar_multiplier=1.0
  * Powerwalls=4, solar_multiplier=1.0
* Redraw when fields change or the Enabled check boxes are checked/uncheckd

## Notes
* Re-read `openapi.json`.


# Step 14: Simulator Monthly View
Goal: Build a page that shows simulation results for each month. It uses Scenarios UI from `battery_and_solar_simulator.html` and monthly view similar to the one in `monthly_comparison.html`.  

## Interface
* Put the scenarios UI above the bar charts for now
* Have a year picker like `monthly_comparison.html` that lets the user check boxes for which years to compare
* For now, we will just look at `from_grid_kwh` (presented in the UI as "Grid Usage"). We may add more metrics later.
* Unlike `monthly_comparison.html` the x-axis should be year-month (ex: 25-Jan for January 2025). IE: We don't want to loop by month the way we do in `monthly_comparison.html`; the x-axis should just be straight chronological order.

## Notes
* Re-read `openapi.json` and use the `battery_and_solar_simulator/monthly_data` end point

# Step 15: Add "Summary View" To Monthly Simulator
* Make the graph clearly below the controls so that it can use the full width (don't let the scenarios be to the left of the graph)
* Add tab selector that switches between the graph and a summary table for total.
* Each column in the summary table corresponds to one of the Enabled Scenarios
* Have the following metrics in the summary table with one metric per row
  * "Total Home kWh":  sum of `home_kwh` for all months under consideration (should be same for all columns)
  * "Total Solar kWh": sum of `solar_energy_kwh` for all months under consideration
  * "Total Grid Usage kWh": sum of `from_grid_kwh` for all months under consideration
  * "Grid Usage % of Home Total": sum of `from_grid_kwh` / sum(`home_kwh`)
  * "Grid Usage Relative to Original kWh": sum of `from_grid_kwh` for Scenario 1 relative to sum for this scenario
  * "Total Battery Usage kWh": sum of `battery_usage_kwh`
  * "Total Battery Relative to Original kWh": sum(`battery_usage_kwh`) for Scenario 1 relative to sum(`battery_usage_kwh`) for this scenario
* 