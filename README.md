# Mustard greens in AquaCrop – greenhouse, Indian conditions

A first mustard-greens (leafy *Brassica juncea*) crop for **AquaCrop-OSPy**, the model GeoAquaCrop runs,
set up for a single greenhouse / polyhouse.

| File | What it does |
|---|---|
| `mustard_greens_crop.py` | Crop parameters + `make_mustard_greens()` |
| `greenhouse_weather.py` | Builds inside-greenhouse weather (no rain, reduced ET0) from your logger CSV, or a placeholder climate |
| `run_greenhouse.py` | Runs one crop with drip irrigation; writes `results/season_summary.csv`, daily CSVs and `growth.png` |

## Run

Needs Python 3.9+ (GeoAquaCrop itself uses 3.11).

```bash
conda create -n gac python=3.11 -y
conda activate gac
pip install aquacrop pandas matplotlib
python run_greenhouse.py
python run_greenhouse.py --weather my_greenhouse.csv
```

Logger CSV format: `date,tmin,tmax` (optional `et0` column in mm/day).

## Key starting values (NOT calibrated)

| Parameter | Value | Basis |
|---|---|---|
| Crop type | Leafy vegetable | Harvest is leaves; no flowering/grain logic |
| Emergence / harvest | 5 / 45 days after sowing | Typical single-cut greens 35–50 DAS |
| Max canopy cover (CCx) | 0.90 | Dense stand |
| Canopy growth (CGC) | 0.25 /day | ~90 % cover by ~30 DAS |
| Kcb | 1.00 | FAO-56 leafy greens |
| Water productivity (WP) | 17 g/m² | C3 crop range 15–20 |
| Harvest index (HI0) | 0.80 | Marketable share of above-ground dry biomass |
| Dry matter of product (`YldWC`) | 8 % | AquaCrop-OSPy: fresh = dry ÷ (YldWC/100) |
| Root depth | 0.20 → 0.45 m | Shallow, raised beds |
| Base / upper temp | 5 / 30 °C | Brassica |
| Plants/ha | 300 000 | 30 cm rows × ~11 cm |

Greenhouse setup: no rain, ET0 = Hargreaves × 0.7, drip refills at 70 % of available water,
CO2 fixed at 420 ppm (change if you enrich).

## Calibration – what to measure

From one or two greenhouse crops (ideally a well-watered and a deficit treatment):

1. **Canopy cover** every 5–7 days (phone photo + Canopeo app works) → tune `CGC_CD`, `CCx`, `EmergenceCD`.
2. **Above-ground dry biomass** at 3–4 dates (oven-dry 0.25 m² samples) → tune `WP`.
3. **Fresh marketable yield** and **dry-matter %** at harvest → tune `HI0`, `YldWC`.
4. **Irrigation applied** and soil moisture (tensiometer or sensor) → check `Kcb`, `ET0_FACTOR`.
5. **Inside Tmin/Tmax** daily (and ideally RH + radiation for proper Penman-Monteith ET0).

Order: phenology → canopy → biomass → yield. Judge fit with RMSE, NRMSE (<20 % is acceptable) and Willmott's d.

## Later: moving to GeoAquaCrop (open field, gridded)

GeoAquaCrop has no mustard. To add it you would need to:
- register the crop in AquaCrop-OSPy (`crop_params`) or pass these values through GeoAquaCrop's `crop_param_override`;
- add `'MustardGreens'` to `CROPS` in `geoaquacrop_simulate/config.py`;
- provide your own crop-calendar layer (GGCMI has no mustard) – sowing date + season length per grid cell;
- optionally a crop-area layer (SPAM has no mustard greens); without it, production in tonnes is left blank.
