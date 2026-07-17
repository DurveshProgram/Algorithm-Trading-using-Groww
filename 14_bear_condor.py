"""
=====================================================================
14_bear_condor.py
Options strategy: Bear Condor
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Bear Condor'

LEGS = [
    {"option_type": "PE", "action": "BUY", "offset_key": "k1",
     "label": 'PE leg 1 (buy, highest strike) gap % from spot', "default_pct": 0, "qty_mult": 1},
    {"option_type": "PE", "action": "SELL", "offset_key": "k2",
     "label": 'PE leg 2 (sell) gap % from spot', "default_pct": -2, "qty_mult": 1},
    {"option_type": "PE", "action": "SELL", "offset_key": "k3",
     "label": 'PE leg 3 (sell) gap % from spot', "default_pct": -5, "qty_mult": 1},
    {"option_type": "PE", "action": "BUY", "offset_key": "k4",
     "label": 'PE leg 4 (buy, lowest strike) gap % from spot', "default_pct": -7, "qty_mult": 1},
]
