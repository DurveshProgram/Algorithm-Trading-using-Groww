"""
=====================================================================
01_quick_flip.py
Equity strategy: place a MARKET BUY order, wait 10 seconds, then place
a MARKET SELL order for the same stock and quantity.
Auto-discovered by strategy_loader.py.
=====================================================================
"""

import time

CATEGORY = "equity"
DISPLAY_NAME = "Quick Flip — Buy, wait, then Sell"


def run_strategy(groww, gc, symbols):
    trading_symbol = gc.choose_symbol(symbols)
    quantity_str = input("Enter quantity to trade (default 1): ").strip()
    quantity = int(quantity_str) if quantity_str else 1

    run_at = gc.get_time_ist(label="BUY order")
    gc.wait_until(run_at, label="BUY order")

    try:
        print(f"\nPlacing MARKET BUY order for {trading_symbol}")
        buy_order_id = groww.place_order(
            trading_symbol=trading_symbol,
            quantity=quantity,
            validity=groww.VALIDITY_DAY,
            exchange=groww.EXCHANGE_NSE,
            segment=groww.SEGMENT_CASH,
            product=groww.PRODUCT_MIS,
            order_type=groww.ORDER_TYPE_MARKET,
            transaction_type=groww.TRANSACTION_TYPE_BUY
        )
        print(f"✅ BUY order placed for {trading_symbol}. Order ID: {buy_order_id['groww_order_id']}")
    except Exception as e:
        print(f"❌ Failed to place BUY order: {e}")
        return

    print("⏳ Waiting for 10 secs before placing SELL order...")
    time.sleep(10)

    try:
        print(f"Placing MARKET SELL order for {trading_symbol}")
        sell_order_id = groww.place_order(
            trading_symbol=trading_symbol,
            quantity=quantity,
            validity=groww.VALIDITY_DAY,
            exchange=groww.EXCHANGE_NSE,
            segment=groww.SEGMENT_CASH,
            product=groww.PRODUCT_MIS,
            order_type=groww.ORDER_TYPE_MARKET,
            transaction_type=groww.TRANSACTION_TYPE_SELL
        )
        print(f"✅ SELL order placed for {trading_symbol}. Order ID: {sell_order_id['groww_order_id']}")
    except Exception as e:
        print(f"❌ Failed to place SELL order: {e}")
