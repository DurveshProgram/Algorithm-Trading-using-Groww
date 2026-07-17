"""
=====================================================================
16_short_straddle.py
Options strategy: Short Straddle
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Short Straddle'

LEGS = [
    {"option_type": "CE", "action": "SELL", "offset_key": "atm",
     "label": 'ATM strike gap % from spot (0 = ATM, same strike for CE & PE)', "default_pct": 0, "qty_mult": 1},
    {"option_type": "PE", "action": "SELL", "offset_key": "atm",
     "label": 'ATM strike gap % from spot (0 = ATM, same strike for CE & PE)', "default_pct": 0, "qty_mult": 1},
]
