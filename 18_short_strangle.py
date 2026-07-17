"""
=====================================================================
18_short_strangle.py
Options strategy: Short Strangle
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Short Strangle'

LEGS = [
    {"option_type": "CE", "action": "SELL", "offset_key": "k_up",
     "label": 'Upper CE (sell) strike gap % from spot', "default_pct": 3, "qty_mult": 1},
    {"option_type": "PE", "action": "SELL", "offset_key": "k_down",
     "label": 'Lower PE (sell) strike gap % from spot', "default_pct": -3, "qty_mult": 1},
]
