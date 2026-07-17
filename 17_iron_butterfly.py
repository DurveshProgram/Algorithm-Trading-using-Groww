"""
=====================================================================
17_iron_butterfly.py
Options strategy: Iron Butterfly
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Iron Butterfly'

LEGS = [
    {"option_type": "CE", "action": "SELL", "offset_key": "atm",
     "label": 'ATM strike gap % from spot (sold straddle center)', "default_pct": 0, "qty_mult": 1},
    {"option_type": "PE", "action": "SELL", "offset_key": "atm",
     "label": 'ATM strike gap % from spot (sold straddle center)', "default_pct": 0, "qty_mult": 1},
    {"option_type": "CE", "action": "BUY", "offset_key": "wing_up",
     "label": 'Upper CE wing (buy, protection) gap % from spot', "default_pct": 3, "qty_mult": 1},
    {"option_type": "PE", "action": "BUY", "offset_key": "wing_down",
     "label": 'Lower PE wing (buy, protection) gap % from spot', "default_pct": -3, "qty_mult": 1},
]
