"""
Build an AquaCrop weather table for the inside of a greenhouse / polyhouse.

AquaCrop needs daily MinTemp, MaxTemp, Precipitation and ReferenceET.
Inside a greenhouse:
  * Precipitation = 0 (all water comes from irrigation)
  * ReferenceET is lower than outside: less radiation gets through the cover
    and there is little wind. We estimate it with Hargreaves-Samani from the
    inside temperatures, then multiply by `et0_factor` (default 0.7).
    If you log inside radiation/humidity, compute Penman-Monteith ET0 instead
    and pass it in the 'et0' column.
"""
import numpy as np
import pandas as pd


def extraterrestrial_radiation(lat_deg: float, doy: np.ndarray) -> np.ndarray:
    """Ra in MJ/m2/day (FAO-56 eq. 21)."""
    phi = np.radians(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    delta = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(delta), -1, 1))
    return (24 * 60 / np.pi) * 0.0820 * dr * (
        ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws)
    )


def hargreaves_et0(tmin, tmax, lat_deg, dates) -> np.ndarray:
    """Hargreaves-Samani ET0 (mm/day)."""
    doy = pd.DatetimeIndex(dates).dayofyear.values
    ra_mm = extraterrestrial_radiation(lat_deg, doy) * 0.408  # MJ -> mm water equivalent
    tmean = (tmin + tmax) / 2
    return 0.0023 * ra_mm * (tmean + 17.8) * np.sqrt(np.clip(tmax - tmin, 0, None))


def from_logger_csv(path: str, lat_deg: float, et0_factor: float = 0.7) -> pd.DataFrame:
    """
    Read your greenhouse logger data. CSV columns: date, tmin, tmax [, et0].
    If 'et0' is present it is used as-is; otherwise it is estimated.
    """
    df = pd.read_csv(path, parse_dates=["date"])
    return _to_aquacrop(df, lat_deg, et0_factor)


def synthetic_polyhouse(start: str, end: str, lat_deg: float,
                        tmax_start=30.0, tmax_end=27.0,
                        tmin_start=16.0, tmin_end=12.0,
                        et0_factor: float = 0.7) -> pd.DataFrame:
    """
    PLACEHOLDER climate: temperatures change linearly from start to end values.
    Defaults roughly match a naturally ventilated polyhouse in central India
    from November into December. Replace with your logger data as soon as you can.
    """
    dates = pd.date_range(start, end, freq="D")
    n = len(dates)
    df = pd.DataFrame({
        "date": dates,
        "tmin": np.linspace(tmin_start, tmin_end, n),
        "tmax": np.linspace(tmax_start, tmax_end, n),
    })
    return _to_aquacrop(df, lat_deg, et0_factor)


def _to_aquacrop(df: pd.DataFrame, lat_deg: float, et0_factor: float) -> pd.DataFrame:
    if "et0" in df.columns and df["et0"].notna().all():
        et0 = df["et0"].values
    else:
        et0 = hargreaves_et0(df["tmin"].values, df["tmax"].values, lat_deg, df["date"]) * et0_factor
    return pd.DataFrame({
        "MinTemp": df["tmin"].values,
        "MaxTemp": df["tmax"].values,
        "Precipitation": 0.0,
        "ReferenceET": np.clip(et0, 0.1, None),  # AquaCrop needs ET0 > 0
        "Date": pd.DatetimeIndex(df["date"]),
    })
