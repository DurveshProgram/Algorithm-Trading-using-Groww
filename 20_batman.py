"""
=====================================================================
20_batman.py
Options strategy: Batman (twin butterfly — call butterfly + put butterfly)
Auto-discovered by strategy_loader.py — CATEGORY + LEGS below are all
main.py needs to add this to the menu. No other file needs editing.
=====================================================================
"""

CATEGORY = "options"
DISPLAY_NAME = 'Batman (twin butterfly — call butterfly + put butterfly)'

LEGS = [
    {"option_type": "CE", "action": "BUY", "offset_key": "c1",
     "label": '[Call wing] lower CE (buy) gap % from spot', "default_pct": 1, "qty_mult": 1},
    {"option_type": "CE", "action": "SELL", "offset_key": "c2",
     "label": '[Call wing] CE body (sell x2) gap % from spot', "default_pct": 3, "qty_mult": 2},
    {"option_type": "CE", "action": "BUY", "offset_key": "c3",
     "label": '[Call wing] upper CE (buy) gap % from spot', "default_pct": 5, "qty_mult": 1},
    {"option_type": "PE", "action": "BUY", "offset_key": "p1",
     "label": '[Put wing] upper PE (buy) gap % from spot', "default_pct": -1, "qty_mult": 1},
    {"option_type": "PE", "action": "SELL", "offset_key": "p2",
     "label": '[Put wing] PE body (sell x2) gap % from spot', "default_pct": -3, "qty_mult": 2},
    {"option_type": "PE", "action": "BUY", "offset_key": "p3",
     "label": '[Put wing] lower PE (buy) gap % from spot', "default_pct": -5, "qty_mult": 1},
]
