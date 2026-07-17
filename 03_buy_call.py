"""
=====================================================================
03_buy_call.py
Options strategy: Buy Call
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Buy Call'

LEGS = [
    {"option_type": "CE", "action": "BUY", "offset_key": "leg1",
     "label": 'CE strike gap % from spot (0 = ATM)', "default_pct": 0, "qty_mult": 1},
]
