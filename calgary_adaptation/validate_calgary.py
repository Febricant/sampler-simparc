"""
validate_calgary.py  --  Task 2 (assert the Calgary plumbing worked)

Checks the generated CSVs and FAILS LOUDLY (AssertionError) unless 100% of rows:
  * map to the Calgary EPW,
  * have site_time_zone_utc_offset == -7.0,
  * keep daylight saving enabled,
  * and contain zero 'Bi-energie' draws.

EPW + UTC + DST live in building-mapping.csv (HPXML args); the raw
Source_Energie_Chauf draw lives in building-input.csv. We check both.

Run:
    python calgary_adaptation/validate_calgary.py
"""

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PROJECT_DIR, "data", "output")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

CALGARY_EPW = "CAN_AB_Calgary.Intl.AP.718770_CWEC2020.epw"


def main():
    m = pd.read_csv(os.path.join(OUT, "building-mapping.csv"))
    i = pd.read_csv(os.path.join(OUT, "building-input.csv"))
    n = len(m)

    # 1) every dwelling uses the Calgary weather file
    bad_epw = m.loc[m["weather_station_epw_filepath"] != CALGARY_EPW, "weather_station_epw_filepath"]
    assert bad_epw.empty, f"{len(bad_epw)}/{n} rows have a non-Calgary EPW: {bad_epw.unique()[:5]}"

    # 2) every dwelling is UTC -7.0
    utc = pd.to_numeric(m["site_time_zone_utc_offset"], errors="coerce")
    assert np.allclose(utc, -7.0), f"UTC offsets present: {utc.value_counts(dropna=False).to_dict()}"

    # 3) daylight saving stays enabled
    dst = m["simulation_control_daylight_saving_enabled"].astype(str).str.lower()
    assert dst.isin(["true", "1"]).all(), f"DST not all True: {dst.value_counts().to_dict()}"

    # 4) zero Bi-energie -- in the raw draw...
    n_bie = int((i["Source_Energie_Chauf"] == "Bi-energie").sum())
    assert n_bie == 0, f"{n_bie}/{n} rows still drew Bi-energie in Source_Energie_Chauf"

    # ...and as a belt-and-braces check, nowhere in the HPXML output either
    hit = m.apply(lambda c: c.astype(str).str.contains("Bi-energie", case=False, na=False)).any().any()
    assert not hit, "Found the literal 'Bi-energie' somewhere in building-mapping.csv"

    print(f"PASS  ({n} dwellings): 100% Calgary EPW, UTC -7.0, DST on, zero Bi-energie.")


if __name__ == "__main__":
    main()
