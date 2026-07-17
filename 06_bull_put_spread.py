"""
=====================================================================
06_bull_put_spread.py
Options strategy: Bull Put Spread
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Bull Put Spread'

LEGS = [
    {"option_type": "PE", "action": "SELL", "offset_key": "sell_leg",
     "label": 'Higher PE (sell) strike gap % from spot', "default_pct": -1, "qty_mult": 1},
    {"option_type": "PE", "action": "BUY", "offset_key": "buy_leg",
     "label": 'Lower PE (buy, protection) strike gap % from spot', "default_pct": -4, "qty_mult": 1},
]
