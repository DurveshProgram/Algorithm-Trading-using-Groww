"""
=====================================================================
Groww Auto Trade — Buy, wait 10s, Sell
Runs locally in VS Code (terminal only, no UI).

What this script does:
  1. Asks for your Groww credentials in the terminal (not hardcoded) —
     supports EITHER the daily API Key+Secret flow OR the no-expiry
     TOTP flow (recommended, avoids daily re-approval on Groww's site).
  2. Downloads the live Groww instruments list and lets you search/select
     a stock from the terminal (acts as a "dropdown").
  3. Asks what time (IST, 24-hour HH:MM) you want the trade to run.
  4. Waits until that time, places a MARKET BUY order, waits 10 seconds,
     then places a MARKET SELL order.

Run with:  python groww_auto_trade.py
Requires: pip install growwapi pyotp
=====================================================================
"""

import csv
import io
import time
import getpass
import urllib.request
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    raise SystemExit(
        "This script needs Python 3.9 or higher (for zoneinfo). "
        "Please upgrade Python or install the 'backports.zoneinfo' package."
    )

from growwapi import GrowwAPI

try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False

IST = ZoneInfo("Asia/Kolkata")
INSTRUMENTS_URL = "https://growwapi-assets.groww.in/instruments/instrument.csv"


# =====================================================================
# STEP 1: Ask for API credentials (typed at runtime, never stored)
# =====================================================================

def get_secret_hidden(prompt):
    """Uses plain visible input() instead of getpass.
    getpass() can silently hang or refuse keystrokes on some Windows
    console setups (seen with the WindowsApps Python alias), so this
    trades hidden-typing for reliability. The typed value is never
    echoed anywhere else and only lives in memory for this run."""
    print("⚠️  This will be typed visibly on screen (not hidden).")
    value = input(prompt).strip()

    if len(value) == 0:
        print("⚠️ Nothing was captured (0 characters). The paste/type likely didn't register.")
    else:
        print(f"   (captured {len(value)} characters)")
    return value


def get_credentials():
    print("=" * 60)
    print("🔐 Groww API Login")
    print("=" * 60)
    print("Choose authentication method:")
    print("  1. API Key + Secret  (requires daily re-approval on Groww's API Keys page)")
    print("  2. TOTP               (recommended — no daily expiry)")

    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice in ("1", "2"):
            break
        print("❌ Please enter 1 or 2.")

    if choice == "1":
        api_key = input("Enter your Groww API Key: ").strip()
        api_secret = get_secret_hidden("Enter your Groww API Secret (hidden): ")
        print("\n🔑 Authenticating with Groww (API Key + Secret flow)...")
        access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
        return access_token

    # TOTP flow
    if not PYOTP_AVAILABLE:
        raise SystemExit(
            "The 'pyotp' package is required for the TOTP flow. Install it with:\n"
            "    pip install pyotp"
        )

    totp_token = input("Enter your Groww TOTP Token (API Key for TOTP flow): ").strip()
    totp_secret = get_secret_hidden("Enter your Groww TOTP Secret (hidden): ").replace(" ", "")

    totp_code = pyotp.TOTP(totp_secret).now()
    print(f"   Generated current TOTP code (auto, not shown for safety).")

    print("\n🔑 Authenticating with Groww (TOTP flow)...")
    access_token = GrowwAPI.get_access_token(api_key=totp_token, totp=totp_code)
    return access_token


# =====================================================================
# STEP 2: Load instruments and let user search/select (dropdown-style)
# =====================================================================

def load_nse_equity_symbols():
    print("\n📥 Downloading instrument list from Groww...")
    with urllib.request.urlopen(INSTRUMENTS_URL) as response:
        raw = response.read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(raw))
    symbols = []
    for row in reader:
        if row.get("exchange") == "NSE" and row.get("segment") == "CASH" \
           and row.get("instrument_type") in ("EQ", None, ""):
            symbols.append({
                "trading_symbol": row["trading_symbol"],
                "name": row.get("name", "").strip()
            })

    seen = set()
    unique_symbols = []
    for s in symbols:
        if s["trading_symbol"] not in seen:
            seen.add(s["trading_symbol"])
            unique_symbols.append(s)
    unique_symbols.sort(key=lambda x: x["trading_symbol"])
    print(f"✅ Loaded {len(unique_symbols)} NSE equity symbols.\n")
    return unique_symbols


def choose_symbol(symbols):
    query = input("🔎 Type part of the company name or symbol (e.g. IDEA): ").strip().upper()
    matches = [s for s in symbols if query in s["trading_symbol"].upper() or query in s["name"].upper()]

    if not matches:
        print("❌ No matches found. Try again.\n")
        return choose_symbol(symbols)

    display_matches = matches[:30]
    if len(matches) > 30:
        print(f"⚠️ {len(matches)} matches found, showing first 30. Refine your search if needed.")

    print("\nSelect a stock:")
    for i, m in enumerate(display_matches, start=1):
        print(f"  {i}. {m['trading_symbol']} - {m['name']}")

    choice = input("Enter number: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(display_matches):
            return display_matches[idx]["trading_symbol"]
    except ValueError:
        pass

    print("❌ Invalid selection, try again.\n")
    return choose_symbol(symbols)


# =====================================================================
# STEP 3: Ask for the run time (IST)
# =====================================================================

def get_run_time_ist():
    print("\n🕒 When should the trade run? (Indian Standard Time)")
    while True:
        time_str = input("Enter time as HH:MM in 24-hour format (e.g. 09:20): ").strip()
        try:
            hour, minute = map(int, time_str.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            print("❌ Invalid format. Please enter like 09:20 or 14:45.")
            continue

        now = datetime.now(IST)
        run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run_at <= now:
            # If the time already passed today, schedule for the same time tomorrow
            run_at += timedelta(days=1)
            print(f"ℹ️ That time has already passed today, scheduling for tomorrow: {run_at.strftime('%Y-%m-%d %H:%M')} IST")
        else:
            print(f"✅ Scheduled for: {run_at.strftime('%Y-%m-%d %H:%M')} IST")

        confirm = input("Confirm this time? (y/n): ").strip().lower()
        if confirm == "y":
            return run_at


def wait_until(run_at):
    print(f"\n⏳ Waiting until {run_at.strftime('%Y-%m-%d %H:%M')} IST to place the BUY order...")
    while True:
        now = datetime.now(IST)
        remaining = (run_at - now).total_seconds()
        if remaining <= 0:
            break
        # Print a heartbeat every ~5 minutes so you know it's alive, sleep in small chunks
        sleep_chunk = min(remaining, 300)
        time.sleep(sleep_chunk)
        now = datetime.now(IST)
        print(f"   Still waiting... {int((run_at - now).total_seconds())} seconds left")


# =====================================================================
# MAIN
# =====================================================================

def main():
    try:
        access_token = get_credentials()
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("   If this is a 400 Bad Request on the API Key + Secret flow, the most common cause")
        print("   is that the key/secret pair needs to be re-approved today on the Groww Cloud API")
        print("   Keys page. Consider switching to the TOTP flow (option 2) to avoid this.")
        return

    groww = GrowwAPI(access_token)
    print("✅ Ready to Groww")

    all_symbols = load_nse_equity_symbols()
    trading_symbol = choose_symbol(all_symbols)
    quantity = 1  # Change this if you want to trade a different quantity

    run_at = get_run_time_ist()
    wait_until(run_at)

    # =========== BUY ===========
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

    # =========== WAIT 10s ===========
    print("⏳ Waiting for 10 secs before placing SELL order...")
    time.sleep(10)

    # =========== SELL ===========
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


if __name__ == "__main__":
    main()
