"""
=====================================================================
strategy_options.py
Generic engine that runs ANY options strategy — strategies themselves
live as individual files in strategies/ (auto-discovered by
strategy_loader.py). This file just implements the shared mechanics:
underlying/expiry/spot input, strike resolution, order placement,
and P&L monitoring.

IMPORTANT: This does NOT use Groww's get_option_chain API, because
that endpoint requires a subscription/role your key may not have
("Access Forbidden" errors seen previously). Instead:
  - Expiries and strikes come from the public instruments.csv (same
    file the equity dropdown already uses — no auth/subscription needed).
  - You type in the current spot/index value yourself (check the
    Groww app or NSE site) instead of it being fetched live.
  - Every expiry and strike you're offered is a REAL contract that
    exists — never a guessed or randomly generated one.

Flow:
  1. Ask for underlying (NIFTY, BANKNIFTY, or an F&O stock).
  2. Show a numbered menu of REAL available expiry dates for it.
  3. Ask you to type in the current spot/index value.
  4. For the chosen strategy, ask for each leg's strike gap % from spot
     (with sensible defaults) — snapped to the nearest REAL strike that
     exists for that expiry.
  5. Ask for lots, product type (MIS/NRML), and a combined stoploss +
     target in rupees, plus a failsafe square-off time.
  6. Show a confirmation summary before placing anything.
  7. Place all legs, then try to monitor live P&L (via get_ltp) — if
     that's also blocked, falls back to a manual mode where you just
     hold until your square-off time (or Ctrl+C to exit early) and
     track P&L yourself in the Groww app.

⚠️ Multi-leg execution risk: each leg is placed as a separate order.
If one leg fills and another doesn't, you can be left with an
unhedged/naked position. Always check your Groww positions after
running this, especially the first few times.
=====================================================================
"""

import time
from datetime import datetime

import groww_common as gc


def _ask_underlying():
    print("\nCommon underlyings: NIFTY, BANKNIFTY, FINNIFTY, or any F&O stock (e.g. RELIANCE)")
    return input("Enter underlying symbol: ").strip().upper()


def _get_spot_price(groww, underlying):
    """Tries to auto-fetch the live spot/index price via get_ltp. Falls
    back to asking the user to type it in only if that call is blocked
    (e.g. subscription/role restriction) or fails for any reason."""
    try:
        ltp_map = groww.get_ltp(segment=groww.SEGMENT_CASH, exchange_trading_symbols=f"NSE_{underlying}")
        spot = ltp_map.get(f"NSE_{underlying}")
        if spot is not None:
            print(f"✅ Auto-fetched live spot price for {underlying}: {spot}")
            return float(spot)
        raise ValueError("Empty response")
    except Exception as e:
        print(f"⚠️ Couldn't auto-fetch live spot price ({e}).")
        print("   This usually means your API key doesn't have live-data access yet.")
        while True:
            raw = input(f"Enter the CURRENT spot/index price of {underlying} manually "
                        f"(check Groww app or NSE site): ").strip()
            try:
                return float(raw)
            except ValueError:
                print("❌ Please enter a number, e.g. 25000 or 25000.50")


def _ask_offsets(strategy_def):
    """Asks the user once per unique offset_key used by this strategy's legs."""
    seen = {}
    for leg in strategy_def["legs"]:
        key = leg["offset_key"]
        if key in seen:
            continue
        prompt = f"{leg['label']} [default {leg['default_pct']}]: "
        raw = input(prompt).strip()
        try:
            pct = float(raw) if raw else float(leg["default_pct"])
        except ValueError:
            print(f"   ⚠️ Invalid number, using default {leg['default_pct']}")
            pct = float(leg["default_pct"])
        seen[key] = pct
    return seen


def _resolve_legs(strategy_def, offsets, contracts, expiry_date, spot):
    """Turns leg templates + user offsets into concrete legs using REAL
    strikes that exist in the instruments CSV for this expiry."""
    resolved = []
    for leg in strategy_def["legs"]:
        pct = offsets[leg["offset_key"]]
        target_price = spot * (1 + pct / 100.0)

        available_strikes = gc.get_available_strikes(contracts, expiry_date, leg["option_type"])
        if not available_strikes:
            raise SystemExit(f"❌ No {leg['option_type']} strikes found for expiry {expiry_date}.")

        strike = gc.nearest_available_strike(available_strikes, target_price)
        contract = gc.find_contract(contracts, expiry_date, strike, leg["option_type"])

        resolved.append({
            "option_type": leg["option_type"],
            "action": leg["action"],
            "strike": strike,
            "trading_symbol": contract["trading_symbol"],
            "lot_size": contract["lot_size"],
            "qty_mult": leg["qty_mult"],
            "entry_ltp": None,  # filled in later if live data is available
        })
    return resolved


def _try_fetch_ltps(groww, resolved_legs):
    """Attempts to fetch live LTPs for all legs in one call. Returns True
    if it worked (and fills entry_ltp on each leg), False if the live
    data feed is blocked (e.g. subscription/role issue)."""
    try:
        exchange_symbols = tuple(f"NSE_{leg['trading_symbol']}" for leg in resolved_legs)
        ltp_map = groww.get_ltp(segment=groww.SEGMENT_FNO, exchange_trading_symbols=exchange_symbols)
        for leg in resolved_legs:
            leg["entry_ltp"] = ltp_map.get(f"NSE_{leg['trading_symbol']}")
        return all(leg["entry_ltp"] is not None for leg in resolved_legs)
    except Exception as e:
        print(f"⚠️ Live price fetch not available ({e}). Will run in manual-monitoring mode.")
        return False


def _print_summary(underlying, expiry, spot, resolved_legs, lots, lot_size, product, sl_amount, target_amount, square_off_at, live_data_available):
    print("\n" + "=" * 60)
    print("📋 Trade Summary — review carefully before confirming")
    print("=" * 60)
    print(f"Underlying: {underlying}   Spot (as entered): {spot}   Expiry: {expiry}")
    print(f"Lots: {lots}   Lot size: {lot_size}   Total qty per leg unit: {lots * lot_size}")
    print(f"Product: {product}")
    print("\nLegs (all strikes below are REAL contracts that exist for this expiry):")
    for leg in resolved_legs:
        qty = lots * lot_size * leg["qty_mult"]
        ltp_str = f"LTP {leg['entry_ltp']}" if leg["entry_ltp"] is not None else "LTP unavailable"
        print(f"  {leg['action']:<4} {leg['trading_symbol']:<25} strike {leg['strike']:<10} qty {qty:<6} ({ltp_str})")

    if live_data_available:
        print(f"\nStoploss: exit all legs if combined loss reaches ₹{sl_amount}")
        print(f"Target:   exit all legs if combined profit reaches ₹{target_amount}")
    else:
        print("\n⚠️ Live price monitoring is NOT available with your current API access.")
        print("   Stoploss/target will NOT be auto-monitored — you'll need to track P&L yourself")
        print("   in the Groww app and exit manually (or wait for the square-off time below).")

    print(f"Failsafe square-off time: {square_off_at.strftime('%Y-%m-%d %H:%M')} IST (forces exit regardless of P&L)")
    print("=" * 60)


def _place_leg_order(groww, trading_symbol, qty, action, product):
    transaction_type = groww.TRANSACTION_TYPE_BUY if action == "BUY" else groww.TRANSACTION_TYPE_SELL
    product_const = groww.PRODUCT_MIS if product == "MIS" else groww.PRODUCT_NRML
    return groww.place_order(
        trading_symbol=trading_symbol,
        quantity=qty,
        validity=groww.VALIDITY_DAY,
        exchange=groww.EXCHANGE_NSE,
        segment=groww.SEGMENT_FNO,
        product=product_const,
        order_type=groww.ORDER_TYPE_MARKET,
        transaction_type=transaction_type,
    )


def _opposite(action):
    return "SELL" if action == "BUY" else "BUY"


def _compute_pnl(groww, resolved_legs, lots, lot_size):
    exchange_symbols = tuple(f"NSE_{leg['trading_symbol']}" for leg in resolved_legs)
    ltp_map = groww.get_ltp(segment=groww.SEGMENT_FNO, exchange_trading_symbols=exchange_symbols)

    total_pnl = 0.0
    details = []
    for leg in resolved_legs:
        current_ltp = ltp_map.get(f"NSE_{leg['trading_symbol']}")
        if current_ltp is None:
            continue
        qty = lots * lot_size * leg["qty_mult"]
        sign = 1 if leg["action"] == "BUY" else -1
        leg_pnl = sign * (current_ltp - leg["entry_ltp"]) * qty
        total_pnl += leg_pnl
        details.append((leg["trading_symbol"], current_ltp, leg_pnl))
    return total_pnl, details


def _execute_and_monitor(groww, resolved_legs, lots, lot_size, product, sl_amount, target_amount, square_off_at, live_data_available):
    # =========== PLACE ENTRY ORDERS FOR ALL LEGS ===========
    print("\n🚀 Placing entry orders...")
    for leg in resolved_legs:
        qty = lots * lot_size * leg["qty_mult"]
        try:
            resp = _place_leg_order(groww, leg["trading_symbol"], qty, leg["action"], product)
            print(f"✅ {leg['action']} {leg['trading_symbol']} qty {qty} — Order ID: {resp.get('groww_order_id')}")
        except Exception as e:
            print(f"❌ Failed to place {leg['action']} {leg['trading_symbol']}: {e}")
            print("   ⚠️ Some legs may already be filled — check your Groww positions immediately"
                  " and manually square off any unintended open legs.")

    # =========== MONITOR ===========
    if live_data_available:
        print("\n📈 Monitoring combined P&L. Press Ctrl+C to stop monitoring (won't auto-exit legs).")
        try:
            while True:
                now = datetime.now(gc.IST)
                if now >= square_off_at:
                    print("\n⏰ Square-off time reached — exiting all legs.")
                    break
                try:
                    pnl, details = _compute_pnl(groww, resolved_legs, lots, lot_size)
                except Exception as e:
                    print(f"⚠️ Couldn't fetch live prices this cycle: {e}")
                    time.sleep(10)
                    continue

                print(f"   P&L: ₹{pnl:.2f}   " + "  ".join(f"{sym}={ltp}" for sym, ltp, _ in details))

                if sl_amount > 0 and pnl <= -abs(sl_amount):
                    print(f"\n🛑 Stoploss hit (₹{pnl:.2f}) — exiting all legs.")
                    break
                if target_amount > 0 and pnl >= abs(target_amount):
                    print(f"\n🎯 Target hit (₹{pnl:.2f}) — exiting all legs.")
                    break
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n⚠️ Monitoring stopped manually. Your positions are still OPEN.")
            if input("Exit (square off) all legs now? (y/n): ").strip().lower() != "y":
                print("👋 Leaving positions open — remember to manage them manually in Groww.")
                return
    else:
        print("\n⏳ Manual-monitoring mode: holding until square-off time.")
        print("   Track your P&L in the Groww app. Press Ctrl+C anytime to exit early.")
        try:
            gc.wait_until(square_off_at, label="square-off (manual monitoring mode)")
        except KeyboardInterrupt:
            print("\n⚠️ Stopped manually. Your positions are still OPEN.")
            if input("Exit (square off) all legs now? (y/n): ").strip().lower() != "y":
                print("👋 Leaving positions open — remember to manage them manually in Groww.")
                return

    # =========== EXIT ALL LEGS ===========
    print("\n🚪 Placing exit orders for all legs...")
    for leg in resolved_legs:
        qty = lots * lot_size * leg["qty_mult"]
        exit_action = _opposite(leg["action"])
        try:
            resp = _place_leg_order(groww, leg["trading_symbol"], qty, exit_action, product)
            print(f"✅ {exit_action} {leg['trading_symbol']} qty {qty} — Order ID: {resp.get('groww_order_id')}")
        except Exception as e:
            print(f"❌ Failed to exit {leg['trading_symbol']}: {e}")
            print("   ⚠️ Check your Groww positions and square off manually if needed.")


def run_for_module(groww, module):
    """Runs an options strategy given its auto-discovered module (which
    must define DISPLAY_NAME and LEGS)."""
    strategy_def = {"display": module.DISPLAY_NAME, "legs": module.LEGS}
    return _run(groww, strategy_def)


def _run(groww, strategy_def):
    underlying = _ask_underlying()
    contracts = gc.load_fno_contracts(underlying)
    expiry = gc.choose_expiry(contracts)
    spot = _get_spot_price(groww, underlying)

    print(f"\n▶️ {strategy_def['display']}")
    print("⚠️  Verify this leg construction matches what you intend before trading real money.")

    offsets = _ask_offsets(strategy_def)
    resolved_legs = _resolve_legs(strategy_def, offsets, contracts, expiry, spot)

    lot_size = resolved_legs[0]["lot_size"]

    lots_str = input("Enter number of lots (default 1): ").strip()
    lots = int(lots_str) if lots_str else 1

    print("\nProduct type:")
    print("  1. MIS (intraday, auto square-off by exchange/broker end-of-day rules)")
    print("  2. NRML (carry forward / positional)")
    product = "MIS" if input("Enter 1 or 2 (default 1): ").strip() != "2" else "NRML"

    sl_str = input("\nEnter stoploss amount in ₹ (combined across all legs, e.g. 2000): ").strip()
    sl_amount = float(sl_str) if sl_str else 0.0

    target_str = input("Enter target amount in ₹ (combined across all legs, e.g. 4000): ").strip()
    target_amount = float(target_str) if target_str else 0.0

    square_off_at = gc.get_time_ist(label="failsafe square-off (forces exit no matter what)")

    print("\n📡 Checking if live price monitoring is available...")
    live_data_available = _try_fetch_ltps(groww, resolved_legs)

    _print_summary(underlying, expiry, spot, resolved_legs, lots, lot_size, product, sl_amount, target_amount, square_off_at, live_data_available)
    confirm = input("\nType YES to place these orders: ").strip()
    if confirm != "YES":
        print("❌ Cancelled — no orders placed.")
        return

    _execute_and_monitor(groww, resolved_legs, lots, lot_size, product, sl_amount, target_amount, square_off_at, live_data_available)


def _choose_strategy_module():
    import strategy_loader
    entries = [e for e in strategy_loader.discover_strategies() if e["category"] == "options"]
    print("\n" + "=" * 60)
    print("📊 Choose an options strategy")
    print("=" * 60)
    for i, e in enumerate(entries, start=1):
        print(f"  {i}. {e['label']}")
    while True:
        choice = input(f"Enter a number (1-{len(entries)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(entries):
                return entries[idx]["module"]
        except ValueError:
            pass
        print("❌ Invalid selection, try again.")


def run_strategy(groww, symbols):
    """Standalone entry point (python strategy_options.py) — shows its
    own options menu (discovered from strategies/). `symbols` (equity
    list) is unused."""
    module = _choose_strategy_module()
    run_for_module(groww, module)


if __name__ == "__main__":
    groww = gc.login()
    run_strategy(groww, symbols=None)