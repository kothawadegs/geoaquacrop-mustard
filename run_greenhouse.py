"""
Simulate one greenhouse crop of mustard greens with AquaCrop-OSPy.

    python run_greenhouse.py                      # placeholder climate
    python run_greenhouse.py --weather logger.csv # your logged inside climate

Edit the SETTINGS block for your greenhouse.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from aquacrop import AquaCropModel, CO2, FieldMngt, InitialWaterContent, IrrigationManagement, Soil

from greenhouse_weather import from_logger_csv, synthetic_polyhouse
from mustard_greens_crop import make_mustard_greens

# ---------------- SETTINGS ----------------
LATITUDE = 20.0                # deg N - change to your site
SOWING = "2025/11/01"          # YYYY/MM/DD
SIM_END = "2025/12/31"         # must be after sowing + 45 days
SOIL = "SandyLoam"             # bed soil; AquaCrop built-ins: Loam, SandyLoam, ClayLoam, ...
CO2_PPM = 420                  # raise if you enrich CO2
ET0_FACTOR = 0.7               # inside ET0 / estimated outside ET0
# Drip irrigation: refill whenever root-zone water drops below 70 % of available water
IRRIGATION = IrrigationManagement(irrigation_method=1, SMT=[70, 70, 70, 70],
                                  WetSurf=30, AppEff=90, MaxIrr=10)
MULCH = FieldMngt(mulches=False)   # e.g. FieldMngt(mulches=True, mulch_pct=80, f_mulch=0.5) for plastic mulch
# ------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weather", help="CSV with columns date,tmin,tmax[,et0] logged inside the greenhouse")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    if args.weather:
        weather = from_logger_csv(args.weather, LATITUDE, ET0_FACTOR)
    else:
        print("NOTE: using PLACEHOLDER greenhouse climate - pass --weather for real data.")
        weather = synthetic_polyhouse(SOWING, SIM_END, LATITUDE, et0_factor=ET0_FACTOR)

    crop = make_mustard_greens(planting_date=SOWING[5:])
    model = AquaCropModel(
        sim_start_time=SOWING,
        sim_end_time=SIM_END,
        weather_df=weather,
        soil=Soil(SOIL),
        crop=crop,
        initial_water_content=InitialWaterContent(value=["FC"]),
        irrigation_management=IRRIGATION,
        field_management=MULCH,
        co2_concentration=CO2(constant_conc=True, current_concentration=CO2_PPM),
    )
    model.run_model(till_termination=True)

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    stats = model.get_simulation_results()
    growth = model.get_crop_growth()
    flux = model.get_water_flux()
    stats.to_csv(out / "season_summary.csv", index=False)
    growth.to_csv(out / "daily_growth.csv", index=False)
    flux.to_csv(out / "daily_water.csv", index=False)

    print(stats.to_string(index=False))
    season = growth[growth["dap"] > 0]
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.5))
    ax[0].plot(season["dap"], season["canopy_cover"] * 100); ax[0].set_title("Canopy cover (%)")
    ax[1].plot(season["dap"], season["biomass"] / 100); ax[1].set_title("Biomass (t/ha dry)")
    ax[2].plot(season["dap"], season["FreshYield"]); ax[2].set_title("Fresh leaf yield (t/ha)")
    for a in ax:
        a.set_xlabel("Days after sowing")
    fig.tight_layout()
    fig.savefig(out / "growth.png", dpi=120)
    print(f"Saved results to {out.resolve()}")


if __name__ == "__main__":
    main()
