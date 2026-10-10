"""
Mustard greens (leafy Brassica juncea) crop parameters for AquaCrop-OSPy.

FIRST-GUESS VALUES - NOT CALIBRATED. There is no published AquaCrop calibration
for mustard greens. Values are taken from AquaCrop's leafy-vegetable conventions,
typical C3 Brassica values, and FAO-56 crop coefficients for leafy greens.
Calibrate against your own greenhouse measurements (see README.md) before
trusting the yields.

Mode: calendar days (CalendarType = 1). GeoAquaCrop also forces calendar-day
mode, so the same values can later be used there.
"""
from aquacrop import Crop

MUSTARD_GREENS = {
    "Name": "MustardGreens",
    "CropType": 1,          # 1 = leafy vegetable (harvest index builds quickly, no flowering)
    "PlantMethod": 1,       # 1 = direct sown (0 = transplanted)
    "CalendarType": 1,      # calendar days
    "SwitchGDD": 0,
    "Determinant": 0,       # canopy keeps growing until senescence

    # --- Phenology (days after sowing), single-cut harvest at ~45 DAS ---
    "EmergenceCD": 5,
    "MaxRootingCD": 35,
    "SenescenceCD": 45,     # = maturity: no canopy decline before harvest
    "MaturityCD": 45,       # harvest day; 35-50 DAS is typical for greens
    "HIstartCD": 8,         # leaf yield starts building soon after emergence
    "YldFormCD": 37,        # HIstart + YldForm = maturity
    "FloweringCD": -999,    # not used for leafy crops
    # GDD equivalents unused in calendar mode (-9 = not set, as in AquaCrop's own files)
    "Emergence": -9, "MaxRooting": -9, "Senescence": -9, "Maturity": -9,
    "HIstart": -9, "YldForm": -9, "Flowering": -999,

    # --- Temperature ---
    "GDDmethod": 3,
    "Tbase": 5.0,           # Brassica base temperature (deg C)
    "Tupp": 30.0,
    "TrColdStress": 1,
    "GDD_up": 8.0,          # GDD/day needed for full transpiration
    "GDD_lo": 0,
    "PolHeatStress": 0,     # pollination not relevant for a leaf harvest
    "PolColdStress": 0,
    "Tmax_up": 40.0, "Tmax_lo": 45.0, "Tmin_up": 10.0, "Tmin_lo": 5.0,

    # --- Canopy ---
    "PlantPop": 300_000,    # plants/ha (e.g. 30 cm rows x ~11 cm in-row)
    "SeedSize": 1.5,        # cm2 of soil covered per seedling at 90% emergence
                            # -> CC0 = 300000 * 1.5e-8 = 0.45 %
    "CCx": 0.90,            # maximum canopy cover
    "CGC_CD": 0.25,         # canopy growth per day -> ~90% cover around 30 DAS
    "CDC_CD": 0.10,         # canopy decline (barely used, harvest before senescence)
    "CGC": -9, "CDC": -9,

    # --- Transpiration & biomass ---
    "Kcb": 1.00,            # basal crop coefficient at full cover (FAO-56 leafy greens ~0.95-1.0)
    "fage": 0.15,
    "WP": 17.0,             # g/m2, normalised water productivity (C3 range 15-20)
    "WPy": 100.0,
    "fsink": 0.5,           # response to CO2 (relevant for CO2-enriched greenhouses)

    # --- Harvest index (marketable leaf+petiole share of above-ground dry biomass) ---
    "HI0": 0.80,
    "dHI_pre": 0.0, "a_HI": 0.0, "b_HI": 0.0, "dHI0": 0.0, "exc": 100.0,
    # AquaCrop-OSPy computes Fresh = Dry / (YldWC / 100), so YldWC is the DRY-MATTER %
    # of the harvested product (despite the name). Mustard greens are ~8-10 % dry matter.
    "YldWC": 8,

    # --- Roots (shallow-rooted, raised beds) ---
    "Zmin": 0.20,
    "Zmax": 0.45,
    "fshape_r": 1.5,
    "SxTopQ": 0.048,
    "SxBotQ": 0.012,

    # --- Water stress (leafy greens are sensitive) ---
    "p_up1": 0.15, "p_lo1": 0.50, "fshape_w1": 3.0,   # canopy expansion
    "p_up2": 0.40, "fshape_w2": 3.0,                  # stomatal closure
    "p_up3": 0.60, "fshape_w3": 3.0,                  # early senescence
    "p_up4": 1.0, "fshape_w4": 1,                     # pollination (unused)
    "p_lo2": 1, "p_lo3": 1, "p_lo4": 1,
    "ETadj": 1.0,
    "Aer": 5.0,             # sensitive to waterlogging
}


def make_mustard_greens(planting_date: str, **overrides) -> Crop:
    """Build the crop. planting_date is 'MM/DD'; overrides replace any parameter above."""
    params = {**MUSTARD_GREENS, **overrides}
    return Crop("custom", planting_date=planting_date, **params)
