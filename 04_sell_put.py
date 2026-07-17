"""
=====================================================================
04_sell_put.py
Options strategy: Sell Put
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Sell Put'

LEGS = [
    {"option_type": "PE", "action": "SELL", "offset_key": "leg1",
     "label": 'PE strike gap % from spot (0 = ATM)', "default_pct": 0, "qty_mult": 1},
]
