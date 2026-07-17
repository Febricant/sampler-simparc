# -*- coding: utf-8 -*-
"""Decide whether a sampler CSV can actually be simulated, and repair it if not.

``preprocess_data_to_dict`` prints a "not valid" warning for every one of the
~330 measure arguments a CSV does not carry, so a real problem arrives as one
extra line in roughly 7,900. This module reports only what can break a run:

  * cast failures -- a non-numeric Double or a blank Integer. These are the only
    two conditions that raise in ``preprocess_data_types``.
  * invalid Choice values -- the key is dropped from ``hpxml_args`` and the
    OpenStudio step fails much later, recorded in ``results/errors.parquet``.
    This is the failure in
    ``building-test-from-sampler-with-error-for-building17.csv``.
  * blank cells the CSV does carry whose feature is switched on and for which
    the measure documents no fallback -- the rest are listed separately, since
    OS-HPXML defaults or autosizes them.
  * field combinations OS-HPXML refuses even though each value is legal on its
    own, e.g. an apartment unit with a conditioned basement. These fail inside
    the measure, after the run has started.
  * columns that look like measure arguments but are not, so they are silently
    carried as metadata and never reach OpenStudio.

``main.py`` calls :func:`check` before simulating anything, so a CSV OS-HPXML
would reject never reaches OpenStudio. ``validate_sampler_csv.py`` is the
standalone CLI over the same code.
"""

import contextlib
import io
import xml.etree.ElementTree as ET

import pandas as pd

import config
from preprocessing import preprocess_data_types, preprocess_data_to_dict

# Measure arguments the sampler emits under an older name. Both targets are the
# names used by measures/BuildResidentialHPXML/measure.xml.
RENAMES = {
    "slab_perimeter_depth": "slab_perimeter_insulation_depth",
    "slab_under_width": "slab_under_insulation_width",
}


def omittable_arguments():
    """Arguments that are safe to leave blank, per the measure's own documentation.

    OS-HPXML spells out the fallback in the description ("If not provided, the
    OS-HPXML default is used", "If not provided, assumes not ducted"). An
    argument with neither that clause nor a default value has nothing to fall
    back on, so omitting it on a dwelling that needs it fails the OpenStudio
    step -- the defect in the -with-error-for-building17 sample.
    """
    safe = set()
    for argument in ET.parse(config.HPXML_SCHEMA_FILE).getroot().iter("argument"):
        name = argument.findtext("name")
        if argument.findtext("default_value") is not None:
            safe.add(name)
        elif "if not provided" in (argument.findtext("description") or "").lower():
            safe.add(name)
    return safe


def _is_off(value):
    """True when a gate column reads as absent or disabled."""
    if pd.isna(value):
        return True
    return str(value).strip().lower() in {"false", "none", "no", "0", "0.0", "", "aucun"}


# A blank cell is expected when the feature it belongs to is switched off.
# Each rule is (column predicate, gate column, condition on the row).
EXPECTED_BLANK = [
    (lambda c: c.startswith("water_heater_"), "ChaufEau_Presence",
     lambda row: str(row.get("ChaufEau_Presence", "")).strip() == "Aucun"),
    (lambda c: c == "water_heater_tank_volume", "water_heater_type",
     lambda row: str(row.get("water_heater_type", "")).strip() == "instantaneous water heater"),
    (lambda c: c.startswith("heat_pump_"), "heat_pump_type",
     lambda row: _is_off(row.get("heat_pump_type"))),
    (lambda c: c.startswith("cooling_system_"), "cooling_system_type",
     lambda row: _is_off(row.get("cooling_system_type"))),
    (lambda c: c.startswith("pool_"), "pool_present",
     lambda row: _is_off(row.get("pool_present"))),
    (lambda c: c.startswith("permanent_spa_"), "permanent_spa_present",
     lambda row: _is_off(row.get("permanent_spa_present"))),
    (lambda c: c.startswith("misc_plug_loads_vehicle"), "misc_plug_loads_vehicle_present",
     lambda row: _is_off(row.get("misc_plug_loads_vehicle_present"))),
    (lambda c: c == "schedules_vacancy_period", "Vacancy Status",
     lambda row: str(row.get("Vacancy Status", "")).strip() != "Vacant"),
    (lambda c: c.startswith("overhangs_"), "Overhangs",
     lambda row: _is_off(row.get("Overhangs"))),
    (lambda c: c.startswith("geothermal_loop_")
     or c == "simulation_control_ground_to_air_heat_pump_model_type", "heat_pump_type",
     lambda row: "ground-to-air" not in str(row.get("heat_pump_type", ""))),
    (lambda c: c.startswith("pv_system"), "pv_system_present",
     lambda row: _is_off(row.get("pv_system_present"))),
    (lambda c: c.startswith("mech_vent"), "mech_vent_fan_type",
     lambda row: _is_off(row.get("mech_vent_fan_type"))),
    (lambda c: c.startswith("dehumidifier_"), "dehumidifier_type",
     lambda row: _is_off(row.get("dehumidifier_type"))),
]


def blank_is_expected(column, row):
    for matches, gate, condition in EXPECTED_BLANK:
        if matches(column) and gate in row and condition(row):
            return True
    return False


def check_casts(data, constraints):
    """Reproduce the casts in preprocess_data_types and collect the failures."""
    casts = {"Boolean": bool, "Integer": int, "Choice": str, "Double": float, "String": str}
    failures = []
    for column in data.columns:
        if column not in constraints:
            continue
        arg_type = constraints[column]["Type"]
        try:
            data[column].astype(casts[arg_type])
        except Exception as exc:
            failures.append((column, arg_type, "%s: %s" % (type(exc).__name__, exc)))
    return failures


def check_choices(data, constraints):
    """Values present in the CSV that the measure will refuse."""
    findings = []
    for column in data.columns:
        if column not in constraints or constraints[column]["Type"] != "Choice":
            continue
        allowed = set(map(str, constraints[column]["Choices"]))
        seen = {}
        for index, value in data[column].items():
            if pd.isna(value):
                continue
            if str(value) not in allowed:
                seen.setdefault(str(value), []).append(index + 1)  # building_id is 1-based
        for value, rows in seen.items():
            findings.append((column, value, rows, sorted(allowed)))
    return findings


def check_blanks(data, constraints, omittable):
    """Blanks in columns the CSV carries whose feature is switched on.

    Returns (blocking, informational). A blank only stops a simulation when the
    measure has nothing to fall back on: a Choice argument with no default has
    to be mapped to an EnergyPlus object, so leaving it out fails the step. That
    is the defect in the ``-with-error-for-building17`` sample. Everything the
    measure documents a fallback for is fine -- ``test.csv`` simulated 100/100
    with blank ``pool_heater_type`` (defaults to "none") and blank
    ``water_heater_tank_volume`` (OS-HPXML autosizes it).
    """
    blocking, informational = [], []
    records = data.to_dict(orient="records")
    for column in data.columns:
        if column not in constraints:
            continue
        constraint = constraints[column]
        rows = [
            index + 1
            for index, row in enumerate(records)
            if pd.isna(row[column]) and not blank_is_expected(column, row)
        ]
        if not rows:
            continue
        risky = constraint["Type"] == "Choice" and column not in omittable
        bucket = blocking if risky else informational
        bucket.append((column, constraint["Type"], rows))
    return blocking, informational


# Combinations OS-HPXML rejects outright. Per-field validation cannot see these:
# every value is individually legal, only the pairing fails, and it fails inside
# the BuildResidentialHPXML measure -- after the run has started.
# (description, predicate over a row)
UNSUPPORTED_COMBINATIONS = [
    ("apartment unit with a conditioned basement/crawlspace",
     lambda row: (row.get("geometry_unit_type") == "apartment unit"
                  and row.get("geometry_foundation_type") in
                  ("ConditionedBasement", "ConditionedCrawlspace"))),
]


def check_combinations(data):
    """Field pairings the measure refuses, even though each value is legal."""
    findings = []
    for description, is_unsupported in UNSUPPORTED_COMBINATIONS:
        rows = [i + 1 for i, row in enumerate(data.to_dict(orient="records"))
                if is_unsupported(row)]
        if rows:
            findings.append((description, rows))
    return findings


def check_unrecognized(data, constraints):
    """snake_case columns that look like measure arguments but are not."""
    return [
        c for c in data.columns
        if c not in constraints and c.islower() and " " not in c and "_" in c
    ]


def repair(data):
    """Apply the fixes a stale sampler export needs; return (data, changes)."""
    changes = []
    for old, new in RENAMES.items():
        if old not in data.columns:
            continue
        if new not in data.columns:
            data = data.rename(columns={old: new})
            changes.append("renamed %s -> %s" % (old, new))
            continue
        # A stale export carries both names: the sampler's pinned column
        # contract supplies the correct one (empty) and appends the misnamed one
        # (populated) at the end. Renaming would leave two columns of the same
        # name, and read_csv then mangles the populated one to "<name>.1" -- so
        # the repair would silently do nothing. Merge into the correct column.
        filled = data[new].isna() & data[old].notna()
        data.loc[filled, new] = data.loc[filled, old]
        data = data.drop(columns=[old])
        changes.append("merged %s into %s (%d value(s))" % (old, new, int(filled.sum())))

    # OS-HPXML forbids ConditionedBasement/ConditionedCrawlspace on apartment
    # units. Mapping.py never reached its AboveApartment branch (arg was ""), so
    # exports made before that fix carry the unsupported pairing.
    if {"geometry_unit_type", "geometry_foundation_type"} <= set(data.columns):
        apartment = data["geometry_unit_type"].eq("apartment unit")
        conditioned = data["geometry_foundation_type"].isin(
            ["ConditionedBasement", "ConditionedCrawlspace"])
        target = apartment & conditioned
        if target.any():
            level = data["Geometry Building Level"] if "Geometry Building Level" in data.columns \
                else pd.Series("", index=data.index)
            # A unit with a dwelling below it sits above an apartment; a
            # bottom-floor unit does not, so its basement stays in the model but
            # outside the unit's conditioned volume.
            above = target & level.isin(["Middle", "Top"])
            below = target & ~level.isin(["Middle", "Top"])
            data.loc[above, "geometry_foundation_type"] = "AboveApartment"
            data.loc[below & data["geometry_foundation_type"].eq("ConditionedBasement"),
                     "geometry_foundation_type"] = "UnconditionedBasement"
            data.loc[below & data["geometry_foundation_type"].eq("ConditionedCrawlspace"),
                     "geometry_foundation_type"] = "UnventedCrawlspace"
            if "geometry_attic_type" in data.columns:
                data.loc[target & level.eq("Middle"), "geometry_attic_type"] = "BelowApartment"
            changes.append(
                "apartment foundations: %d -> AboveApartment, %d -> Unconditioned"
                % (int(above.sum()), int(below.sum())))

    if "ChaufEau_Presence" in data.columns:
        absent = data["ChaufEau_Presence"].astype(str).str.strip() == "Aucun"
        group = [c for c in data.columns if c.startswith("water_heater_")]
        if absent.any() and group:
            partial = int(data.loc[absent, group].notna().any(axis=1).sum())
            if partial:
                data.loc[absent, group] = None
                changes.append(
                    "cleared water_heater_* on %d row(s) with no water heater" % partial
                )
    return data, changes


class Findings:
    """What is wrong with a CSV, and whether any of it stops a simulation."""

    def __init__(self, casts, choices, combinations, blocking_blanks,
                 other_blanks, unrecognized):
        self.casts = casts
        self.choices = choices
        self.combinations = combinations
        self.blocking_blanks = blocking_blanks
        self.other_blanks = other_blanks
        self.unrecognized = unrecognized

    @property
    def blocking(self):
        """True when simulating this CSV would fail rather than merely warn."""
        return bool(self.casts or self.choices or self.combinations
                    or self.blocking_blanks)

    @property
    def empty(self):
        return not (self.blocking or self.other_blanks or self.unrecognized)


def check(data, constraints=None):
    """Run every check over ``data`` and return a :class:`Findings`."""
    constraints = config.ARGS_CONSTRAINTS if constraints is None else constraints
    blocking_blanks, other_blanks = check_blanks(data, constraints, omittable_arguments())
    return Findings(
        casts=check_casts(data.copy(), constraints),
        choices=check_choices(data, constraints),
        combinations=check_combinations(data),
        blocking_blanks=blocking_blanks,
        other_blanks=other_blanks,
        unrecognized=check_unrecognized(data, constraints),
    )


def report(path, data, constraints=None, findings=None):
    """Print the findings; return True when the file is safe to simulate."""
    constraints = config.ARGS_CONSTRAINTS if constraints is None else constraints
    findings = check(data, constraints) if findings is None else findings

    print("== %s" % path)
    print("   %d buildings, %d columns (%d measure arguments)"
          % (len(data), len(data.columns), sum(c in constraints for c in data.columns)))

    if findings.casts:
        print("   BLOCKING - preprocess_data_types will raise:")
        for column, arg_type, message in findings.casts:
            print("      %s (%s): %s" % (column, arg_type, message))

    if findings.choices:
        print("   BLOCKING - invalid Choice values (argument dropped, OpenStudio fails later):")
        for column, value, rows, allowed in findings.choices:
            print("      %s = %r on row(s) %s" % (column, value, rows[:10]))
            print("         allowed: %s" % allowed)

    if findings.combinations:
        print("   BLOCKING - OS-HPXML does not support these combinations:")
        for description, rows in findings.combinations:
            print("      %s: %d building(s) %s"
                  % (description, len(rows), rows[:15]))

    if findings.blocking_blanks:
        print("   BLOCKING - required by an active feature, no default to fall back on:")
        for column, arg_type, rows in findings.blocking_blanks:
            print("      %s (%s) blank on building(s) %s"
                  % (column, arg_type, rows[:10]))

    if findings.other_blanks:
        print("   Blanks the measure will default or autosize:")
        for column, arg_type, rows in findings.other_blanks:
            print("      %s (%s) on %d building(s): %s"
                  % (column, arg_type, len(rows), rows[:10]))

    if findings.unrecognized:
        print("   Not measure arguments - carried as metadata, never simulated:")
        for column in findings.unrecognized:
            hint = "  <-- did you mean %s?" % RENAMES[column] if column in RENAMES else ""
            print("      %s%s" % (column, hint))

    if findings.empty:
        print("   no findings")
    return not findings.blocking


def preprocessing_succeeds(data, constraints=None):
    """Exercise the simulator's own path, so anything the checks above do not
    model still surfaces here rather than at simulation time.

    Returns (ok, message). ``message`` names the argument count on success and
    the exception on failure.
    """
    constraints = config.ARGS_CONSTRAINTS if constraints is None else constraints
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            frame, hpxml_columns = preprocess_data_types(data.copy(), constraints)
            buildings = preprocess_data_to_dict(frame, constraints, hpxml_columns)
    except Exception as exc:
        return False, "SimParc preprocessing raised %s: %s" % (type(exc).__name__, exc)
    return True, ("preprocessing OK - %d measure arguments reach OpenStudio per building"
                  % len(buildings[0]["hpxml_args"]))
