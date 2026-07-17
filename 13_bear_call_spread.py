"""
=====================================================================
13_bear_call_spread.py
Options strategy: Bear Call Spread
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Bear Call Spread'

LEGS = [
    {"option_type": "CE", "action": "SELL", "offset_key": "sell_leg",
     "label": 'Lower CE (sell) strike gap % from spot', "default_pct": 1, "qty_mult": 1},
    {"option_type": "CE", "action": "BUY", "offset_key": "buy_leg",
     "label": 'Higher CE (buy, protection) strike gap % from spot', "default_pct": 4, "qty_mult": 1},
]
