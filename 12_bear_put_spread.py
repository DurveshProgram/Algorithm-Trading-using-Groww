"""
=====================================================================
12_bear_put_spread.py
Options strategy: Bear Put Spread
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Bear Put Spread'

LEGS = [
    {"option_type": "PE", "action": "BUY", "offset_key": "buy_leg",
     "label": 'Higher PE (buy) strike gap % from spot', "default_pct": 0, "qty_mult": 1},
    {"option_type": "PE", "action": "SELL", "offset_key": "sell_leg",
     "label": 'Lower PE (sell) strike gap % from spot', "default_pct": -3, "qty_mult": 1},
]
