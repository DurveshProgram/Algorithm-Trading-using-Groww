"""
=====================================================================
15_bear_butterfly.py
Options strategy: Bear Butterfly
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Bear Butterfly'

LEGS = [
    {"option_type": "PE", "action": "BUY", "offset_key": "k1",
     "label": 'PE upper wing (buy) gap % from spot', "default_pct": -1, "qty_mult": 1},
    {"option_type": "PE", "action": "SELL", "offset_key": "k2",
     "label": 'PE body (sell x2) gap % from spot', "default_pct": -3, "qty_mult": 2},
    {"option_type": "PE", "action": "BUY", "offset_key": "k3",
     "label": 'PE lower wing (buy) gap % from spot', "default_pct": -5, "qty_mult": 1},
]
