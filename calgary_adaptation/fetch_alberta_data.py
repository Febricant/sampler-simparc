"""
Phase 1 - Data acquisition for the Calgary/Alberta re-calibration
(see ALBERTA_RECALIBRATION_PLAN.md, section 4, Phase 1).

Pulls the two primary machine-readable sources:

1. NRCan EnerGuide Rating System Open Data (house-level microdata)
   - CKAN DataStore on open.canada.ca, package 0a7619fd-2ffe-44b5-9027-3dfcec0866fd
   - one resource per year (2004-2006, 2007, ..., 2025), all datastore-active
   - filtered to PROVINCE = "AB", paginated (the API caps a page at 32,000 rows)
   - written as one Parquet file per year under data/input/alberta/energuide/

2. City of Calgary BenchmarkYYC (aggregated benchmarking metrics)
   - Socrata v3 CSV exports, saved verbatim under data/input/alberta/benchmarkyyc/

Also stubs data/input/alberta/SOURCES.md for tracking manual StatCan/CEUD pulls.

Usage (from repo root, with the project venv):
    python calgary_adaptation/fetch_alberta_data.py                # everything
    python calgary_adaptation/fetch_alberta_data.py --only energuide --years 2020-2025
    python calgary_adaptation/fetch_alberta_data.py --only benchmarkyyc
    python calgary_adaptation/fetch_alberta_data.py --force        # re-download

The script is idempotent: a year whose Parquet file already exists is skipped
unless --force is given. A manifest.json in the energuide folder records row
counts, resource ids and retrieval dates for provenance.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parents[1]
ALBERTA_DIR = REPO_ROOT / "data" / "input" / "alberta"
ENERGUIDE_DIR = ALBERTA_DIR / "energuide"
BENCHMARK_DIR = ALBERTA_DIR / "benchmarkyyc"
SOURCES_MD = ALBERTA_DIR / "SOURCES.md"

CKAN_BASE = "https://open.canada.ca/data/en/api/3/action"
ENERGUIDE_PACKAGE_ID = "0a7619fd-2ffe-44b5-9027-3dfcec0866fd"

# The DataStore rejects limits above 32,000. We stay well under it so a page
# of ~100 selected fields keeps a modest payload (a few MB of JSON).
PAGE_SIZE = 16_000
MAX_RETRIES = 5
BACKOFF_BASE_S = 2.0          # 2, 4, 8, 16, 32 s
PAGE_PAUSE_S = 0.4            # courtesy pause between pages
TIMEOUT_S = 180

# Province filter candidates, tried in order until one returns rows
# (field coding has been stable as "AB" in recent years; the fallbacks
# guard against older vintages coding it differently).
PROVINCE_FILTERS = [{"PROVINCE": "AB"}, {"PROVINCE": "Alberta"}]

BENCHMARKYYC_VIEWS = {
    # dataset slug -> (Socrata v3 CSV export, human name)
    "new_buildings_a3uu-975p": (
        "https://data.calgary.ca/api/v3/views/a3uu-975p/query.csv",
        "Calgary New Buildings: Environmental Performance Metrics",
    ),
    "existing_buildings_ixvd-v9b3": (
        "https://data.calgary.ca/api/v3/views/ixvd-v9b3/query.csv",
        "Calgary Existing Buildings: Environmental Performance Metrics",
    ),
}

# Curated field list (~95 of ~400 columns): everything the re-calibration plan
# maps onto sampler parameters (plan section 3), plus identity/weighting and
# energy-validation fields. Requested per-resource after intersecting with the
# fields that year actually has (older vintages lack the newer columns).
ENERGUIDE_FIELDS = [
    # identity / weighting / geography
    "_id", "HOUSEID", "EVALUATIONSID", "EVALTYPE", "ENTRYDATE", "DATASET",
    "PROVINCE", "CLIENTCITY", "CLIENTPCODE", "HOUSEREGION", "WEATHERLOC",
    "PROGRAMNAME",
    # geometry / vintage / occupancy
    "YEARBUILT", "TYPEOFHOUSE", "STOREYS", "NUMBUILDINGSTOREYS",
    "HEATEDFLOORAREA", "FLOORAREA", "FOOTPRINT", "HSEVOL",
    "NUMDWELLINGUNITS", "TOTALOCCUPANTS",
    # foundation
    "FNDTYPE", "BASEMENTFLOORAR", "CRAWLSPFLOORAR", "SLABFLOORAREA",
    "WALKOUTFLOORAR",
    # envelope
    "CEILINS", "MAINWALLINS", "FNDWALLINS", "SLABINSUL", "CEILINGTYPE",
    "AIR50P", "EGHCRITNATACH", "EGHCRITTOTACH", "NLA",
    "WINDOWCODE", "WINDOWCODENUM", "NUMWINDOWS", "NUMWINESTAR",
    "NUMWINU105", "NUMWINU122", "NUMDOORS", "NUMDOORESTAR",
    # space heating
    "FURNACEFUEL", "FURNACETYPE", "FURSSEFF", "HEATAFUE", "EGHFURSEASEFF",
    "SUPPHTGFUEL1", "SUPPHTGFUEL2", "SUPPHTGTYPE1", "SUPPHTGTYPE2",
    "HPEquipType", "HPSOURCE", "HPCAP", "ASHPHSPF", "CCASHP", "TYPE1CAPACITY",
    # cooling
    "AIRCONDTYPE", "ASHPSEER", "AIRCOP",
    # ventilation
    "CENVENTSYSTYPE", "HRVEFF0C", "TOTALVENTSUPPLY", "TOTALVENTEXH",
    # domestic hot water
    "PDHWFUEL", "PDHWTYPE", "PDHWEF", "PDHWUEF", "PRIMARYDHWTANKVOLUME",
    "DHWHPTYPE", "SDHWFUEL", "SDHWTYPE",
    # setpoints / behaviour
    "TMAIN", "TBSMNT", "ThermostatHeatingNighttime", "ThermostatCooling",
    "PROGSMARTTHERMOSTAT", "HotWaterTemperature",
    # PV / storage / EV
    "KWPV", "NUMSOLSYS", "BATTERYSTORAGE", "ELECAUTOCHRGSTATION", "EVCharger",
    # ratings & energy (validation targets)
    "EGHRATING", "ERSRATING", "ERSENERGYINTENSITY", "ERSGHG", "EGHDESHTLOSS",
    "EGHFCONELEC", "EGHFCONNGAS", "EGHFCONOIL", "EGHFCONPROP", "EGHFCONWOOD",
    "EGHFCONTOTAL", "EGHSPACEENERGY", "ERSSPACECOOLENERGY",
    "ERSWATERHEATINGENERGY", "ERSVENTILATIONENERGY",
    "ERSLIGHTAPPLIANCEENERGY", "MEUI", "TEDI",
]


# --------------------------------------------------------------------------- #
# HTTP helpers
# --------------------------------------------------------------------------- #

def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {"User-Agent": "LTE-Sampler-Residential calgary_adaptation/fetch_alberta_data"}
    )
    return s


def _get_json(session: requests.Session, url: str, params: dict) -> dict:
    """GET with exponential backoff on rate limits, server errors and timeouts."""
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = session.get(url, params=params, timeout=TIMEOUT_S)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
            resp.raise_for_status()
            payload = resp.json()
            if not payload.get("success", False):
                raise RuntimeError(f"CKAN error: {payload.get('error')}")
            return payload
        except (requests.RequestException, ValueError, RuntimeError) as err:
            last_err = err
            wait = BACKOFF_BASE_S * (2 ** attempt)
            # honour Retry-After when the server sends one
            resp = getattr(err, "response", None)
            if resp is not None and resp.headers.get("Retry-After"):
                try:
                    wait = max(wait, float(resp.headers["Retry-After"]))
                except ValueError:
                    pass
            print(f"    retry {attempt + 1}/{MAX_RETRIES} in {wait:.0f}s ({err})")
            time.sleep(wait)
    raise RuntimeError(f"giving up on {url}: {last_err}")


# --------------------------------------------------------------------------- #
# 1. EnerGuide (CKAN DataStore)
# --------------------------------------------------------------------------- #

def discover_energuide_resources(session: requests.Session) -> dict[str, str]:
    """Map year label ('2004-2006', '2007', ..., '2025') -> datastore resource id.

    Discovered at runtime from package_show so new yearly resources (or
    replaced resource ids) are picked up without editing this script.
    """
    payload = _get_json(
        session, f"{CKAN_BASE}/package_show", {"id": ENERGUIDE_PACKAGE_ID}
    )
    resources: dict[str, str] = {}
    for res in payload["result"]["resources"]:
        name = (res.get("name") or "").strip()
        # year resources are named "2025", "2024", ... "2007", "2004-2006"
        if res.get("datastore_active") and name.replace("-", "").isdigit():
            resources[name] = res["id"]
    if not resources:
        raise RuntimeError("no datastore-active year resources found in package")
    return dict(sorted(resources.items()))


def _available_fields(session: requests.Session, resource_id: str) -> set[str]:
    """Field ids present in one year's resource (schemas differ across years)."""
    payload = _get_json(
        session,
        f"{CKAN_BASE}/datastore_search",
        {"resource_id": resource_id, "limit": 0},
    )
    return {f["id"] for f in payload["result"]["fields"]}


def fetch_energuide_year(
    session: requests.Session,
    year: str,
    resource_id: str,
    out_dir: Path,
    page_size: int = PAGE_SIZE,
    all_fields: bool = False,
) -> dict:
    """Pull every Alberta record of one year resource into a Parquet file.

    Pagination: sort=_id with limit/offset pages, then verify the row count
    against the API-reported total so silent truncation is impossible.
    """
    available = _available_fields(session, resource_id)
    if all_fields:
        fields_param = None
        kept = sorted(available)
    else:
        kept = [f for f in ENERGUIDE_FIELDS if f in available]
        fields_param = ",".join(kept)
        missing = sorted(set(ENERGUIDE_FIELDS) - available)
        if missing:
            print(f"    note: {len(missing)} curated fields absent in {year} "
                  f"(e.g. {', '.join(missing[:5])}...)")

    records: list[dict] = []
    total: int | None = None
    filters_used: dict | None = None

    for filters in PROVINCE_FILTERS:
        params = {
            "resource_id": resource_id,
            "filters": json.dumps(filters),
            "limit": page_size,
            "offset": 0,
            "sort": "_id",
        }
        if fields_param:
            params["fields"] = fields_param
        payload = _get_json(session, f"{CKAN_BASE}/datastore_search", params)
        total = payload["result"]["total"]
        if total > 0:
            filters_used = filters
            records.extend(payload["result"]["records"])
            break

    if not total:
        print(f"    {year}: 0 Alberta rows under any province filter - skipping")
        return {"year": year, "resource_id": resource_id, "rows": 0}

    while len(records) < total:
        params["offset"] = len(records)
        payload = _get_json(session, f"{CKAN_BASE}/datastore_search", params)
        page = payload["result"]["records"]
        if not page:
            break  # defensive: total can drift if the resource is re-loaded mid-pull
        records.extend(page)
        print(f"    {year}: {len(records):,}/{total:,}")
        time.sleep(PAGE_PAUSE_S)

    if len(records) != total:
        print(f"    WARNING {year}: fetched {len(records):,} rows, API reported "
              f"{total:,} (resource may have been re-loaded during the pull)")

    df = pd.DataFrame.from_records(records, columns=kept)
    out_path = out_dir / f"energuide_ab_{year}.parquet"
    df.to_parquet(out_path, index=False)
    print(f"    {year}: wrote {len(df):,} rows x {len(df.columns)} cols -> {out_path.name}")
    return {
        "year": year,
        "resource_id": resource_id,
        "rows": len(df),
        "columns": len(df.columns),
        "filters": filters_used,
        "file": out_path.name,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def fetch_energuide(years: list[str] | None, force: bool, page_size: int,
                    all_fields: bool) -> None:
    ENERGUIDE_DIR.mkdir(parents=True, exist_ok=True)
    session = _session()
    resources = discover_energuide_resources(session)
    print(f"EnerGuide: {len(resources)} year resources discovered "
          f"({', '.join(resources)})")

    manifest_path = ENERGUIDE_DIR / "manifest.json"
    manifest: dict = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for year, resource_id in resources.items():
        if years and not _year_selected(year, years):
            continue
        out_path = ENERGUIDE_DIR / f"energuide_ab_{year}.parquet"
        if out_path.exists() and not force:
            print(f"  {year}: exists, skipping (--force to re-download)")
            continue
        print(f"  {year}: fetching (resource {resource_id})")
        entry = fetch_energuide_year(
            session, year, resource_id, ENERGUIDE_DIR,
            page_size=page_size, all_fields=all_fields,
        )
        manifest[year] = entry
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
    print(f"EnerGuide done. Manifest: {manifest_path}")


def _year_selected(year_label: str, wanted: list[str]) -> bool:
    """'2004-2006' matches if any single year in the span was requested."""
    if year_label in wanted:
        return True
    if "-" in year_label:
        lo, hi = year_label.split("-")
        return any(lo <= y <= hi for y in wanted if y.isdigit())
    return False


def _parse_years(spec: str) -> list[str]:
    """'2020-2025' or '2007,2010' -> explicit list of year strings."""
    years: list[str] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-")
            years.extend(str(y) for y in range(int(lo), int(hi) + 1))
        elif part:
            years.append(part)
    return years


# --------------------------------------------------------------------------- #
# 2. BenchmarkYYC (Socrata CSV export)
# --------------------------------------------------------------------------- #

def fetch_benchmarkyyc(force: bool) -> None:
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    session = _session()
    for slug, (url, title) in BENCHMARKYYC_VIEWS.items():
        out_path = BENCHMARK_DIR / f"{slug}.csv"
        if out_path.exists() and not force:
            print(f"  {slug}: exists, skipping")
            continue
        print(f"  fetching {title}")
        for attempt in range(MAX_RETRIES):
            try:
                resp = session.get(url, timeout=TIMEOUT_S)
                resp.raise_for_status()
                break
            except requests.RequestException as err:
                wait = BACKOFF_BASE_S * (2 ** attempt)
                print(f"    retry {attempt + 1}/{MAX_RETRIES} in {wait:.0f}s ({err})")
                time.sleep(wait)
        else:
            raise RuntimeError(f"could not fetch {url}")
        text = resp.content.decode("utf-8-sig", errors="replace")
        n_lines = text.count("\n")
        if n_lines < 2:
            raise RuntimeError(f"{slug}: response looks empty ({n_lines} lines)")
        out_path.write_text(text, encoding="utf-8", newline="")
        print(f"    wrote {n_lines:,} lines -> {out_path.relative_to(REPO_ROOT)}")


# --------------------------------------------------------------------------- #
# 3. Manual sources stub
# --------------------------------------------------------------------------- #

SOURCES_TEMPLATE = """\
# Alberta data sources - provenance log

Automated pulls (see `calgary_adaptation/fetch_alberta_data.py` and
`energuide/manifest.json` for exact row counts and retrieval dates):

| Source | Location | Licence |
|---|---|---|
| NRCan EnerGuide Rating System Open Data (PROVINCE=AB, 2004-2025) | `energuide/*.parquet` | Open Government Licence - Canada |
| City of Calgary BenchmarkYYC (new + existing buildings) | `benchmarkyyc/*.csv` | Open Government Licence - City of Calgary |

Manual downloads - fill one row per file you add:

| File | Source dataset (table id) | URL | Retrieved | Used for |
|---|---|---|---|---|
| `res_ab_e.xlsx` | NRCan CEUD, Residential Sector Alberta, Tables 1-41 | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm | (add date) | Tier-B margins: heating system stock, appliance stock, water heaters |
| | StatCan 38-10-0286 (primary heating systems and type of energy) | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3810028601 | | `Source_Energie_Chauf` / `Chauffage_Logement` cross-check |
| | Census 2021 Profile, Calgary CSD (dwelling type x period x tenure x household size) | https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm | | Raking margins (IPF) |
| | StatCan 20-10-0025 (ZEV registrations, AB) | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010002501 | | `Vehicule_Presence` |
| | CMHC Rental Market Survey, Calgary vacancy | https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research | | `Vacancy Status` |
| | HES tables (AC saturation, thermostats) | https://www150.statcan.gc.ca/n1/en/surveys/3881 | | `Climatisation`, `ModeConsigne` |
"""


def write_sources_stub(force: bool) -> None:
    ALBERTA_DIR.mkdir(parents=True, exist_ok=True)
    if SOURCES_MD.exists() and not force:
        print(f"  {SOURCES_MD.relative_to(REPO_ROOT)} exists, leaving untouched")
        return
    SOURCES_MD.write_text(SOURCES_TEMPLATE, encoding="utf-8")
    print(f"  wrote {SOURCES_MD.relative_to(REPO_ROOT)}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--only", choices=["energuide", "benchmarkyyc", "sources"],
                        help="run a single step (default: all three)")
    parser.add_argument("--years", type=str, default=None,
                        help="EnerGuide years, e.g. '2020-2025' or '2007,2010'")
    parser.add_argument("--page-size", type=int, default=PAGE_SIZE,
                        help=f"datastore_search page size (max 32000, default {PAGE_SIZE})")
    parser.add_argument("--all-fields", action="store_true",
                        help="pull all ~400 EnerGuide columns instead of the curated set")
    parser.add_argument("--force", action="store_true",
                        help="re-download files that already exist")
    args = parser.parse_args(argv)

    if args.page_size > 32_000:
        parser.error("--page-size must be <= 32000 (hard CKAN DataStore cap)")
    years = _parse_years(args.years) if args.years else None

    if args.only in (None, "sources"):
        print("== SOURCES.md stub ==")
        write_sources_stub(args.force)
    if args.only in (None, "benchmarkyyc"):
        print("== BenchmarkYYC ==")
        fetch_benchmarkyyc(args.force)
    if args.only in (None, "energuide"):
        print("== EnerGuide (PROVINCE=AB) ==")
        fetch_energuide(years, args.force, args.page_size, args.all_fields)
    return 0


if __name__ == "__main__":
    sys.exit(main())
