# MOSAIC historical model v2

This version replaces the synthetic generator with real historical public climate data.

## Sources

- NASA POWER Daily API: precipitation, 2 m temperature, 2 m relative humidity, 2 m wind speed, root-zone soil wetness.
- NOAA PSL/CPC: monthly Nino 3.4 anomaly.
- NOAA PSL: monthly Dipole Mode Index (IOD/DMI).
- Australian Bureau of Meteorology: daily RMM1/RMM2, MJO phase and amplitude.

## Important scientific boundary

NASA POWER meteorology is analysis/reanalysis-scale gridded data. It is useful for a reproducible real-data baseline, but it is not Panchayat-resolution observed rainfall. Operational MOSAIC should later replace/augment precipitation and forecast predictors with IMD/NCMRWF gridded observations and forecast/hindcast data when available.

The `onset` target is an agricultural wet-establishment proxy created from observed rainfall. It is deliberately **not** called the official IMD monsoon onset definition.

The heavy-rain label uses 64.5 mm/day as the lower threshold for IMD's heavy-rain category.

## No future-data leakage

Features are computed only from information available on or before the forecast issue date. Future rainfall is used only to create target labels for lead weeks 1-4.

The default temporal evaluation is:

- Train: through 2018
- Validation/calibration: 2019-2022
- Test: 2023-2025

Evaluation is reported overall and separately for lead weeks 1, 2, 3 and 4. Brier skill is also compared with a historical climatology baseline.
