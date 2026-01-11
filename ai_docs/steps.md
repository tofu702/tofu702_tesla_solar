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