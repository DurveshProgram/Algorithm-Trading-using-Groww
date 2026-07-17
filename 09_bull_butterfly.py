"""
=====================================================================
09_bull_butterfly.py
Options strategy: Bull Butterfly
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Bull Butterfly'

LEGS = [
    {"option_type": "CE", "action": "BUY", "offset_key": "k1",
     "label": 'CE lower wing (buy) gap % from spot', "default_pct": 1, "qty_mult": 1},
    {"option_type": "CE", "action": "SELL", "offset_key": "k2",
     "label": 'CE body (sell x2) gap % from spot', "default_pct": 3, "qty_mult": 2},
    {"option_type": "CE", "action": "BUY", "offset_key": "k3",
     "label": 'CE upper wing (buy) gap % from spot', "default_pct": 5, "qty_mult": 1},
]
