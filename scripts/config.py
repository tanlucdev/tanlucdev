from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
USERNAME = "tanlucdev"

ASCII_RAMP = " .`:-=+*cs#%@"
ASCII_COLS = 100
ASCII_ROWS = 53
PORTRAIT_WIDTH = 370
INFO_CARD_WIDTH = 490
HEATMAP_WIDTH = 860

ASCII_SVG = ROOT / f"{USERNAME}-ascii.svg"
INFO_CARD_SVG = ROOT / "info-card.svg"
HEATMAP_SVG = ROOT / "contrib-heatmap.svg"
CONTRIB_JSON = DATA_DIR / "contributions.json"

BG = "#0d1117"
FG = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#3fb950"
HEATMAP_PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#56d364"]

HEATMAP_WEEKS = 53
HEATMAP_DAYS = 7
CELL = 12
GAP = 4
RADIUS = 3
