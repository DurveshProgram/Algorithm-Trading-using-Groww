"""
=====================================================================
10_buy_put.py
Options strategy: Buy Put
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Buy Put'

LEGS = [
    {"option_type": "PE", "action": "BUY", "offset_key": "leg1",
     "label": 'PE strike gap % from spot (0 = ATM)', "default_pct": 0, "qty_mult": 1},
]
