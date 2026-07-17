"""
=====================================================================
21_long_iron_condor.py
Options strategy: Long Iron Condor
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Long Iron Condor'

LEGS = [
    {"option_type": "PE", "action": "SELL", "offset_key": "k1",
     "label": 'Lowest PE (sell, wing) gap % from spot', "default_pct": -5, "qty_mult": 1},
    {"option_type": "PE", "action": "BUY", "offset_key": "k2",
     "label": 'Lower-mid PE (buy) gap % from spot', "default_pct": -2, "qty_mult": 1},
    {"option_type": "CE", "action": "BUY", "offset_key": "k3",
     "label": 'Upper-mid CE (buy) gap % from spot', "default_pct": 2, "qty_mult": 1},
    {"option_type": "CE", "action": "SELL", "offset_key": "k4",
     "label": 'Highest CE (sell, wing) gap % from spot', "default_pct": 5, "qty_mult": 1},
]
