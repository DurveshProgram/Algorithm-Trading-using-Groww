# Groww Auto Trade — Auto-Discovered Multi-Strategy Setup (VS Code)

## Folder layout

```
main.py                  <- Run this one. Never needs editing to add strategies.
groww_common.py           <- Shared login, stock search, IST time, F&O instrument helpers.
strategy_options.py       <- Generic engine that runs any options strategy.
strategy_loader.py        <- Auto-discovers everything in strategies/.
strategies/
    01_quick_flip.py       <- Equity strategy
    02_intraday.py         <- Equity strategy
    03_buy_call.py         <- Options strategy
    04_sell_put.py         <- Options strategy
    ... (one file per strategy, 03-22)
requirements.txt
```

**The number at the start of each filename in `strategies/` IS its menu number.** `main.py` scans that folder every time it runs and builds the menu automatically, in filename order — it never needs to be edited.

## 1. Setup

```bash
pip install -r requirements.txt
```

## 2. Run

```bash
python main.py
```

You'll be asked to log in once (API Key+Secret or TOTP), then shown a menu built from whatever's in `strategies/`. After a strategy finishes (or fails), you can run another without logging in again.

## 3. Adding a new strategy — no editing required elsewhere

**To add a new options strategy:** create a new file `strategies/23_my_strategy.py` (next free number) with this shape:

```python
CATEGORY = "options"
DISPLAY_NAME = "My New Strategy"

LEGS = [
    {"option_type": "CE", "action": "BUY", "offset_key": "leg1",
     "label": "CE strike gap % from spot (0 = ATM)", "default_pct": 0, "qty_mult": 1},
    # add more legs as needed
]
```
Use any existing `strategies/0X_*.py` options file as a template — copy one and edit `DISPLAY_NAME` + `LEGS`.

**To add a new equity strategy:** create `strategies/23_my_equity_strategy.py` with:

```python
CATEGORY = "equity"
DISPLAY_NAME = "My New Equity Strategy"

def run_strategy(groww, gc, symbols):
    trading_symbol = gc.choose_symbol(symbols)
    # ... your logic, using groww.place_order(...) as needed
```

Use `strategies/01_quick_flip.py` or `strategies/02_intraday.py` as a template.

**That's it** — next time you run `python main.py`, the new file just appears in the menu with the number you gave it. No other file needs to change.

### If you want to replace/update just one strategy
Only that one file needs to change — e.g. if I send you an updated `17_iron_butterfly.py`, just overwrite that single file in your `strategies/` folder. Nothing else in the project is affected.

## 4. How the options strategies work

**No Groww `get_option_chain` API is used** — that endpoint needs a subscription/role your key may not have. Instead:
1. **Underlying** — you type it (e.g. `NIFTY`, `RELIANCE`).
2. **Expiry** — picked from a numbered menu of **real expiries** pulled from the public `instruments.csv` (same file the equity dropdown uses — no subscription needed).
3. **Spot price** — you type this in yourself (check the Groww app/NSE).
4. **Strike gap %** per leg — snapped to the **nearest strike that actually exists** for that expiry, never invented.
5. **Lots, product type, stoploss ₹, target ₹, failsafe square-off time.**
6. A full leg-by-leg summary — you must type `YES` to place anything.

After placing entry orders, it tries once to fetch live prices (`get_ltp`) for auto stoploss/target monitoring. If your key doesn't have live-data access either, it tells you clearly and falls back to holding until your square-off time (or `Ctrl+C` to exit early) while you track P&L yourself in the Groww app.

### ⚠️ Important
- **These are common textbook constructions**, not verified against a single authoritative source — particularly **"Batman"**, which isn't a universally standardized name. Check the printed leg summary matches what you intend.
- **Multi-leg execution risk**: each leg is a separate order — check your Groww positions after running any multi-leg strategy, especially the first few times.
- These place **real orders with real money**.
- The static-IP requirement (SEBI rule) still applies to order placement.
- Keep the terminal open until your strategy finishes.
- Credentials are typed visibly (not masked) and never written to disk.
