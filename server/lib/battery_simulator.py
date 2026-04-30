from time import strptime

import csv
import dataclasses
import datetime
import io

import pydantic

import server.lib.tesla_monthly_data_parser


class DailyBatterySimResult(pydantic.BaseModel):
  date: datetime.date = None

  # Pass through stats
  home_kwh: float = None
  solar_energy_kwh: float = None

  # Key results
  eod_battery_kwh: float = None
  battery_usage_kwh: float = None
  from_grid_kwh: float = None

  # Debug Data
  precharge_home_kwh: float = None
  during_charge_home_kwh: float = None  # Aka solar direct
  postcharge_home_kwh: float = None
  precharge_battery_usage_kwh: float = None
  postcharge_battery_usage_kwh: float = None
  precharge_battery_kwh: float = None
  postcharge_battery_kwh: float = None


# @dataclasses.dataclass
# class BatterySimulatorDayData:
#   date: datetime.date
#   solar_

class BatterySimulator:
  """ Basic Battery Simulator Model
  3 Uses of Daily Solar
   1. "Direct Solar": Solar -> Home directly (no battery)
   2. "Charging Solar" (to_powerwall): Solar -> Powerwall (until full)
   3. "Export Solar" (to_grid): Solar -> Grid

   direct_solar = solar_energy - old_to_powerwall - old_to_grid
   charging_solar = min(solar_energy - direct_solar, remaining_powerwall_capacity)
   export_solar = solar_energy - direct_solar - charging_solar


   3 Sources of Home Energy
   1. "Direct Solar": See Above
   2. "From Powerwall"
   3. "From Grid"

   # TODO: Think about remaining powerwall capacity. I think it's something like this
     * home_non_direct_solar  = home_kwh - direct_solar
     * Then pay for home_non_direct_solar w/ prior day's powerwall as much as possible
     * If there's anything left over, that's remaining_powerwall_capacity, otherwise it's 0
     * For the EOD number, subtract out the remaining to_powerwall_kwh
     * If that doesn't cover it, fill the rest from the grid

   Assume that prior day's EOD powerwall capacity is used first


   Example:
     12:01AM                  6AM                 9 AM                                       6 PM                11:59PM
     USAGE:
    | from_powerwall (-5 kWh) | from_grid (-2 kWh) | solar [10 kWh direct, 13 kWh to battery, 4 kWh to grid] | from_powerwall (-6kWh) |
    BATTERY:
    5 kWH<<<<<<<<<<<<<<<<<0 kWh----------------0kWh>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>13kWh<<<<<<<<<<<<<<<<<<<<<7kWh
    Overall Stats:
    * start of day battery = 5 kWh (Not in original Stats)
    * to_powerwall = 13 kWh
    * from_grid = 2 kWh
    * to_grid = 4 kWh
    * solar = 23 kWh
    * from_powerwall = 11 kWh
    * end of day battery = 7 kWh (not in original stats)

    Problem: of the 11 kWh from_powerwall, how many were before the charging period and how many were after?
    * IE: of the 4 kWh that went "to_grid" how many could go to a larger battery?

    There seem to be 2 possible strategies here:
    1. "Cascaded Batteries": Assume the existing powerwall is "used first". IE: Fills first and empties first. It's
       "grid" is really a second battery that tries to supply power in the morning (to decrease from_grid) and fills
       during the day (to absorb to_grid).
         PROBLEM: This strategy doesn't work if simulating a smaller battery
    2. "Half and Half": Assume that from_powerwall is split evenly between the morning and the evening. The means that
       we can charge max(0, start_of_day_battery - from_powerwall/2)

  """

  def __init__(self):
    pass

  def simulate_day_range(self,
                         solar_data_for_days: list[server.lib.tesla_monthly_data_parser.DailyData],
                         simulated_battery_capacity_kwh: float,
                         solar_multiplier: float = 1.0) -> list[DailyBatterySimResult]:
    results = []  # Have to do this to get access to prior result
    for daily_solar_data in solar_data_for_days:
      prior_day_sim_result = results[-1] if results else None
      cur_day_sim_result = self._simulate_day(day_solar_data=daily_solar_data,
                                              prior_day_battery_state=prior_day_sim_result,
                                              simulated_battery_capacity_kwh=simulated_battery_capacity_kwh,
                                              solar_multiplier=solar_multiplier)
      results.append(cur_day_sim_result)
    return results

  def _compute_to_powerwall(self, day_solar_data: server.lib.tesla_monthly_data_parser.DailyData):
    # basically, inflows must equal outflows
    # inflows = outflows
    # inflows = solar + from_battery + from_grid
    # outflows = to_grid + home + to_powerwall
    # solar + from_battery = to_grid + home + to_powerwall
    # to_powerwall = (solar + from_battery) - (to_grid + home)
    inflow_kwh = day_solar_data.solar_energy_kwh + day_solar_data.from_powerwall_kwh + day_solar_data.from_grid_kwh
    return inflow_kwh - (day_solar_data.to_grid_kwh + day_solar_data.home_kwh)

  def _simulate_day(self, day_solar_data: server.lib.tesla_monthly_data_parser.DailyData,
                    prior_day_battery_state: DailyBatterySimResult | None,
                    simulated_battery_capacity_kwh: float,
                    solar_multiplier: float = 1.0,
                    morning_fraction_of_home_usage: float = 0.5) -> DailyBatterySimResult:
    prior_to_powerwall = self._compute_to_powerwall(day_solar_data)

    solar_energy_kwh = day_solar_data.solar_energy_kwh * solar_multiplier

    # Solar energy that was used directly by the home bypassing the battery entirely
    # This number if the same regardless of the amount of battery
    direct_solar_kwh = solar_energy_kwh - day_solar_data.to_grid_kwh - prior_to_powerwall

    # Solar that wasn't direct
    non_direct_solar_kwh = solar_energy_kwh - direct_solar_kwh

    # Home usage that wasn't fulfilled by direct_solar
    home_kwh_after_direct_solar = day_solar_data.home_kwh - direct_solar_kwh

    # Simplifying assumption: We'll use yesterday battery storage to fulfill 1/2 of the remaining home usage
    # (after subtracting out direct solar)
    morning_precharge_home_kwh = morning_fraction_of_home_usage * home_kwh_after_direct_solar
    evening_postcharge_home_kwh = home_kwh_after_direct_solar - morning_precharge_home_kwh

    prior_eod_battery_kwh = prior_day_battery_state.eod_battery_kwh if prior_day_battery_state else 0
    precharge_battery_usage_kwh = min(prior_eod_battery_kwh, morning_precharge_home_kwh)
    kwh_in_battery_when_charging_starts = prior_eod_battery_kwh - precharge_battery_usage_kwh
    unused_kwh_in_battery_at_charge_start = simulated_battery_capacity_kwh - kwh_in_battery_when_charging_starts

    # IE: Charge the battery as much as possible
    charge_kwh = min(unused_kwh_in_battery_at_charge_start, non_direct_solar_kwh)
    postcharge_battery_kwh = kwh_in_battery_when_charging_starts + charge_kwh

    # Post Solar Battery usage
    postcharge_battery_usage_kwh = min(evening_postcharge_home_kwh, postcharge_battery_kwh)

    # Key end of day stats
    eod_battery_kwh = postcharge_battery_kwh - postcharge_battery_usage_kwh
    total_battery_usage_kwh = precharge_battery_usage_kwh + postcharge_battery_usage_kwh

    # from_grid = deficit of home_kwh that battery + direct solar couldn't account for
    from_grid_kwh = day_solar_data.home_kwh - (precharge_battery_usage_kwh + direct_solar_kwh + postcharge_battery_usage_kwh)

    return DailyBatterySimResult(
      date=day_solar_data.date,
      home_kwh=day_solar_data.home_kwh,
      solar_energy_kwh=solar_energy_kwh,

      eod_battery_kwh=eod_battery_kwh,
      battery_usage_kwh=total_battery_usage_kwh,
      from_grid_kwh=from_grid_kwh,

      precharge_home_kwh=morning_precharge_home_kwh,
      during_charge_home_kwh=direct_solar_kwh,
      postcharge_home_kwh=evening_postcharge_home_kwh,
      precharge_battery_usage_kwh=precharge_battery_usage_kwh,
      postcharge_battery_usage_kwh=postcharge_battery_usage_kwh,
      precharge_battery_kwh=kwh_in_battery_when_charging_starts,
      postcharge_battery_kwh=postcharge_battery_kwh
    )

  def simulated_days_to_csv(self, simulated_days: list[DailyBatterySimResult]):
    out_stringio = io.StringIO()
    writer = csv.writer(out_stringio)
    col_names = ["date", "home_kwh", "solar_energy_kwh", "eod_battery_kwh", "battery_usage_kwh", "from_grid_kwh",
                 "precharge_home_kwh", "during_charge_home_kwh", "postcharge_home_kwh",
                 "precharge_battery_usage_kwh", "postcharge_battery_usage_kwh", "precharge_battery_kwh",
                 "postcharge_battery_kwh"]
    writer.writerow(col_names)
    for simulated_day in simulated_days:
      full_row = [getattr(simulated_day, x) for x in col_names]
      writer.writerow(full_row)
    return out_stringio.getvalue()
