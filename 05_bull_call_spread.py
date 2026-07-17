"""
=====================================================================
05_bull_call_spread.py
Options strategy: Bull Call Spread
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Bull Call Spread'

LEGS = [
    {"option_type": "CE", "action": "BUY", "offset_key": "buy_leg",
     "label": 'Lower CE (buy) strike gap % from spot', "default_pct": 0, "qty_mult": 1},
    {"option_type": "CE", "action": "SELL", "offset_key": "sell_leg",
     "label": 'Higher CE (sell) strike gap % from spot', "default_pct": 3, "qty_mult": 1},
]
