"""
=====================================================================
08_bull_condor.py
Options strategy: Bull Condor
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Bull Condor'

LEGS = [
    {"option_type": "CE", "action": "BUY", "offset_key": "k1",
     "label": 'CE leg 1 (buy, lowest strike) gap % from spot', "default_pct": 0, "qty_mult": 1},
    {"option_type": "CE", "action": "SELL", "offset_key": "k2",
     "label": 'CE leg 2 (sell) gap % from spot', "default_pct": 2, "qty_mult": 1},
    {"option_type": "CE", "action": "SELL", "offset_key": "k3",
     "label": 'CE leg 3 (sell) gap % from spot', "default_pct": 5, "qty_mult": 1},
    {"option_type": "CE", "action": "BUY", "offset_key": "k4",
     "label": 'CE leg 4 (buy, highest strike) gap % from spot', "default_pct": 7, "qty_mult": 1},
]
