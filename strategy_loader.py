"""
=====================================================================
strategy_loader.py
Scans the strategies/ folder and imports every .py file in it. The
number at the start of each filename (e.g. "03_buy_call.py") becomes
its menu number — files are loaded in filename order, so the menu is
always numbered 1, 2, 3... automatically based on whatever files exist.

To add a new strategy: drop a new file into strategies/ following the
naming pattern "NN_something.py" (NN = next free number) and the
template of an existing file. Nothing else needs to change — no
editing main.py, no editing any other strategy file.

Each strategy file must define:
  CATEGORY      = "equity" or "options"
  DISPLAY_NAME  = "Some Strategy Name"

  If CATEGORY == "equity":
      def run_strategy(groww, gc, symbols): ...

  If CATEGORY == "options":
      LEGS = [ {...}, {...} ]   # leg templates, see any existing
                                 # strategies/NN_*.py options file
=====================================================================
"""

import importlib.util
import pathlib

STRATEGIES_DIR = pathlib.Path(__file__).parent / "strategies"


def discover_strategies():
    """Returns a list of dicts, one per discovered strategy file, in
    filename order: {"label": ..., "category": ..., "module": ...}"""
    if not STRATEGIES_DIR.exists():
        raise SystemExit(f"❌ Couldn't find the 'strategies' folder at {STRATEGIES_DIR}")

    entries = []
    for path in sorted(STRATEGIES_DIR.glob("*.py")):
        if path.name.startswith("_"):
            continue  # skip __init__.py / helper files

        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"⚠️ Skipping {path.name} — failed to load: {e}")
            continue

        category = getattr(module, "CATEGORY", None)
        display_name = getattr(module, "DISPLAY_NAME", path.stem)

        if category not in ("equity", "options"):
            print(f"⚠️ Skipping {path.name} — missing/invalid CATEGORY (must be 'equity' or 'options').")
            continue

        entries.append({
            "label": display_name,
            "category": category,
            "module": module,
            "filename": path.name,
        })

    return entries
