"""
=====================================================================
22_long_butterfly.py
Options strategy: Long Butterfly
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Long Butterfly'

LEGS = [
    {"option_type": "CE", "action": "BUY", "offset_key": "k1",
     "label": 'Lower CE (buy) gap % from spot', "default_pct": -2, "qty_mult": 1},
    {"option_type": "CE", "action": "SELL", "offset_key": "k2",
     "label": 'ATM CE body (sell x2) gap % from spot', "default_pct": 0, "qty_mult": 2},
    {"option_type": "CE", "action": "BUY", "offset_key": "k3",
     "label": 'Upper CE (buy) gap % from spot', "default_pct": 2, "qty_mult": 1},
]
