"""
Shared helpers for the calgary_adaptation scripts, so the same code is not
copy-pasted across the figure/map/weather modules:

  * the plotting palette + style (used by energy_profile.py)
  * the Calgary forward-sortation-area (FSA = the first 3 characters of a postal
    code, e.g. "T2E") definition
  * reading the Statistics Canada FSA boundary map (a shapefile) and turning it
    into drawable polygons + centroids, in the StatCan Lambert projection (metres)
  * projecting a latitude/longitude onto that same projection (used to place
    weather grid points into neighbourhoods)

Nothing here runs on its own; it is imported by the other modules.
"""

from __future__ import annotations

import io
import math
import zipfile
from pathlib import Path

import numpy as np
import shapefile  # pyshp
from matplotlib.path import Path as MplPath

REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_ZIP = (REPO_ROOT / "data" / "input" / "alberta" / "census" / "_raw"
                / "lfsa000a21a_e.zip")
SHP_BASE = "lfsa000a21a_e/lfsa000a21a_e"
# StatCan 2021 FSA digital boundary file (shapefile, NAD83 / StatCan Lambert).
BOUNDARY_URL = (
    "https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/"
    "boundary-limites/files-fichiers/lfsa000a21a_e.zip"
)

# "Calgary" = FSA prefixes T2/T3 plus T1Y (36 areas, ~96.5% of dwellings) - the
# same definition every profile script uses.
CALGARY_FSA_PREFIXES = ("T2", "T3")
CALGARY_FSA_EXACT = frozenset({"T1Y"})


def is_calgary_fsa(fsa: str) -> bool:
    return fsa.startswith(CALGARY_FSA_PREFIXES) or fsa in CALGARY_FSA_EXACT


# --------------------------------------------------------------------------- #
# Plot style (one place, so the figures look identical everywhere)
# --------------------------------------------------------------------------- #

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"     # single-series default
AQUA = "#1baf7a"     # comparison series
YELLOW = "#eda100"   # third series
VIOLET = "#4a3aa7"   # fifth series


def apply_style() -> None:
    """Apply the shared matplotlib look (call once before drawing figures)."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": ["Segoe UI", "DejaVu Sans", "sans-serif"],
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "text.color": INK,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_2,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.titlecolor": INK,
        "font.size": 10,
        "axes.titlesize": 12,
        "figure.dpi": 150,
    })


# --------------------------------------------------------------------------- #
# Geography: read the FSA boundary shapefile -> polygons + centroids
# (StatCan Lambert projection, metres - so an equal aspect ratio looks right)
# --------------------------------------------------------------------------- #

def _shape_to_path(shape) -> MplPath:
    """A pyshp polygon (possibly with several detached parts) -> one matplotlib
    Path, so multipart FSAs render / test correctly."""
    pts = shape.points
    starts = list(shape.parts) + [len(pts)]
    verts: list = []
    codes: list = []
    for a, b in zip(starts[:-1], starts[1:]):
        ring = pts[a:b]
        verts.extend(ring)
        codes.append(MplPath.MOVETO)
        codes.extend([MplPath.LINETO] * (len(ring) - 2))
        codes.append(MplPath.CLOSEPOLY)
    return MplPath(np.asarray(verts), codes)


def _largest_part_centroid(shape) -> tuple[float, float]:
    """Centroid of the shape's biggest ring (so a label / nearest-point sits on
    the main body, not floating between detached pieces)."""
    pts = shape.points
    starts = list(shape.parts) + [len(pts)]
    best_area, best_c = -1.0, (0.0, 0.0)
    for a, b in zip(starts[:-1], starts[1:]):
        ring = pts[a:b]
        x = np.asarray([p[0] for p in ring])
        y = np.asarray([p[1] for p in ring])
        cross = x[:-1] * y[1:] - x[1:] * y[:-1]
        signed = cross.sum() / 2.0
        area = abs(signed)
        if area > best_area:
            if signed:
                cx = ((x[:-1] + x[1:]) * cross).sum() / (6 * signed)
                cy = ((y[:-1] + y[1:]) * cross).sum() / (6 * signed)
            else:
                cx, cy = x.mean(), y.mean()
            best_area, best_c = area, (cx, cy)
    return best_c


def ensure_boundary_zip() -> None:
    """Download + cache the StatCan FSA boundary zip (~22 MB) if it is missing."""
    if BOUNDARY_ZIP.exists() and BOUNDARY_ZIP.stat().st_size > 1_000_000:
        return
    import time
    import requests
    BOUNDARY_ZIP.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading FSA boundaries -> {BOUNDARY_ZIP.relative_to(REPO_ROOT)}")
    sess = requests.Session()
    sess.headers.update({"User-Agent": "LTE-Sampler-Residential calgary_adaptation"})
    for attempt in range(5):
        try:
            with sess.get(BOUNDARY_URL, timeout=180, stream=True) as r:
                r.raise_for_status()
                n = 0
                with open(BOUNDARY_ZIP, "wb") as fh:
                    for chunk in r.iter_content(1 << 20):
                        fh.write(chunk)
                        n += len(chunk)
            if n < 1_000_000:
                raise RuntimeError(f"download too small ({n} bytes)")
            print(f"  downloaded {n / 1e6:.0f} MB")
            return
        except (requests.RequestException, RuntimeError) as err:
            print(f"  retry {attempt + 1}/5 ({err})")
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"could not download {BOUNDARY_URL}")


def load_calgary_fsa_shapes() -> dict[str, tuple[MplPath, tuple[float, float]]]:
    """{FSA: (polygon, centroid)} for every Calgary FSA, from the StatCan 2021
    boundary file (downloaded + cached on first use). Centroids are in the
    shapefile's Lambert metres."""
    ensure_boundary_zip()
    with zipfile.ZipFile(BOUNDARY_ZIP) as z:
        reader = shapefile.Reader(
            shp=io.BytesIO(z.read(SHP_BASE + ".shp")),
            dbf=io.BytesIO(z.read(SHP_BASE + ".dbf")),
            shx=io.BytesIO(z.read(SHP_BASE + ".shx")),
            encoding="latin-1",
        )
        fld = [f[0] for f in reader.fields[1:]]
        idx = fld.index("CFSAUID")
        out: dict[str, tuple[MplPath, tuple[float, float]]] = {}
        for sr in reader.iterShapeRecords():
            fsa = sr.record[idx]
            if is_calgary_fsa(fsa):
                out[fsa] = (_shape_to_path(sr.shape), _largest_part_centroid(sr.shape))
    return out


# --------------------------------------------------------------------------- #
# Lambert Conformal Conic forward (EPSG:3347, NAD83 / StatCan Lambert):
# latitude/longitude (degrees) -> x,y metres in the boundary file's projection.
# --------------------------------------------------------------------------- #

class LambertNAD83:
    A = 6_378_137.0
    E2 = 2 / 298.257222101 - (1 / 298.257222101) ** 2
    PHI1, PHI2 = math.radians(49.0), math.radians(77.0)
    PHI0 = math.radians(63.390675)
    LAM0 = math.radians(-91.866667)
    FE, FN = 6_200_000.0, 3_000_000.0

    def __init__(self) -> None:
        self.e = math.sqrt(self.E2)
        n = (math.log(self._m(self.PHI1)) - math.log(self._m(self.PHI2))) / \
            (math.log(self._t(self.PHI1)) - math.log(self._t(self.PHI2)))
        self.n = n
        self.F = self._m(self.PHI1) / (n * self._t(self.PHI1) ** n)
        self.rho0 = self.A * self.F * self._t(self.PHI0) ** n

    def _m(self, phi: float) -> float:
        return math.cos(phi) / math.sqrt(1 - self.E2 * math.sin(phi) ** 2)

    def _t(self, phi: float) -> float:
        es = self.e * math.sin(phi)
        return math.tan(math.pi / 4 - phi / 2) / ((1 - es) / (1 + es)) ** (self.e / 2)

    def forward(self, lat: float, lon: float) -> tuple[float, float]:
        phi, lam = math.radians(lat), math.radians(lon)
        rho = self.A * self.F * self._t(phi) ** self.n
        theta = self.n * (lam - self.LAM0)
        return (self.FE + rho * math.sin(theta),
                self.FN + self.rho0 - rho * math.cos(theta))
