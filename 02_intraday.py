"""
=====================================================================
02_intraday.py
Equity strategy: choose BUY-first or SELL-first, custom quantity, and
exit either after N seconds or at a fixed square-off time.
Auto-discovered by strategy_loader.py.
=====================================================================
"""

import time

CATEGORY = "equity"
DISPLAY_NAME = "Intraday — Buy/Sell first, custom exit (time-based or fixed square-off)"


def _choose_direction():
    print("\nChoose direction:")
    print("  1. BUY first, then SELL later (long)")
    print("  2. SELL first, then BUY later (short/intraday shorting)")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "BUY", "SELL"
        if choice == "2":
            return "SELL", "BUY"
        print("❌ Please enter 1 or 2.")


def _choose_exit_plan(gc):
    print("\nHow should the exit order be triggered?")
    print("  1. Wait a fixed number of seconds after entry, then exit")
    print("  2. Exit at a specific square-off time (IST)")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            secs_str = input("Enter number of seconds to wait before exit (e.g. 10, 60, 300): ").strip()
            try:
                secs = int(secs_str)
                if secs <= 0:
                    raise ValueError
                return ("wait_seconds", secs)
            except ValueError:
                print("❌ Please enter a positive whole number of seconds.")
        elif choice == "2":
            square_off_at = gc.get_time_ist(label="square-off (exit)")
            return ("fixed_time", square_off_at)
        else:
            print("❌ Please enter 1 or 2.")


def _place_order(groww, trading_symbol, quantity, transaction_type_str):
    transaction_type = groww.TRANSACTION_TYPE_BUY if transaction_type_str == "BUY" else groww.TRANSACTION_TYPE_SELL
    return groww.place_order(
        trading_symbol=trading_symbol,
        quantity=quantity,
        validity=groww.VALIDITY_DAY,
        exchange=groww.EXCHANGE_NSE,
        segment=groww.SEGMENT_CASH,
        product=groww.PRODUCT_MIS,
        order_type=groww.ORDER_TYPE_MARKET,
        transaction_type=transaction_type
    )


def run_strategy(groww, gc, symbols):
    trading_symbol = gc.choose_symbol(symbols)

    quantity_str = input("Enter quantity to trade (default 1): ").strip()
    quantity = int(quantity_str) if quantity_str else 1

    entry_side, exit_side = _choose_direction()

    entry_at = gc.get_time_ist(label=f"{entry_side} entry order")
    exit_plan_type, exit_plan_value = _choose_exit_plan(gc)

    gc.wait_until(entry_at, label=f"{entry_side} entry")

    try:
        print(f"\nPlacing MARKET {entry_side} order for {trading_symbol} (qty {quantity})")
        entry_order = _place_order(groww, trading_symbol, quantity, entry_side)
        print(f"✅ {entry_side} order placed. Order ID: {entry_order['groww_order_id']}")
    except Exception as e:
        print(f"❌ Failed to place {entry_side} entry order: {e}")
        return

    if exit_plan_type == "wait_seconds":
        print(f"⏳ Waiting {exit_plan_value} seconds before placing {exit_side} exit order...")
        time.sleep(exit_plan_value)
    else:
        gc.wait_until(exit_plan_value, label=f"{exit_side} exit")

    try:
        print(f"Placing MARKET {exit_side} order for {trading_symbol} (qty {quantity})")
        exit_order = _place_order(groww, trading_symbol, quantity, exit_side)
        print(f"✅ {exit_side} order placed. Order ID: {exit_order['groww_order_id']}")
    except Exception as e:
        print(f"❌ Failed to place {exit_side} exit order: {e}")
        print("   ⚠️ Your entry position may still be open — check your Groww holdings/positions"
              " and consider squaring it off manually if needed.")
