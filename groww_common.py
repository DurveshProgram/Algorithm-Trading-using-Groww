"""
=====================================================================
groww_common.py
Shared building blocks used by every strategy file:
  - Login (API Key+Secret flow OR TOTP flow)
  - NSE equity instrument list + terminal search/select ("dropdown")
  - IST time helpers (ask for a time, wait until it arrives)

Nothing in this file places trades. Import what you need from it in
your strategy scripts, or run main.py to pick a strategy interactively.
=====================================================================
"""

import csv
import io
import time
import urllib.request
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    raise SystemExit(
        "This project needs Python 3.9 or higher (for zoneinfo). "
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
# LOGIN
# =====================================================================

def _get_input_visible(prompt):
    """Plain visible input(). getpass() can hang/refuse keystrokes on
    some Windows console setups, so secrets are typed visibly here.
    Reports captured length (not the value) so paste failures are obvious."""
    print("⚠️  This will be typed visibly on screen (not hidden).")
    value = input(prompt).strip()
    if len(value) == 0:
        print("⚠️ Nothing was captured (0 characters). The paste/type likely didn't register.")
    else:
        print(f"   (captured {len(value)} characters)")
    return value


def login():
    """Prompts for credentials, authenticates, and returns a ready-to-use
    GrowwAPI client. Call this once per run (e.g. from main.py) and pass
    the returned client into whichever strategy you run."""
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

    try:
        if choice == "1":
            api_key = input("Enter your Groww API Key: ").strip()
            api_secret = _get_input_visible("Enter your Groww API Secret: ")
            print("\n🔑 Authenticating with Groww (API Key + Secret flow)...")
            access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
        else:
            if not PYOTP_AVAILABLE:
                raise SystemExit(
                    "The 'pyotp' package is required for the TOTP flow. Install it with:\n"
                    "    pip install pyotp"
                )
            totp_token = input("Enter your Groww TOTP Token (API Key for TOTP flow): ").strip()
            totp_secret = _get_input_visible("Enter your Groww TOTP Secret: ").replace(" ", "")
            totp_code = pyotp.TOTP(totp_secret).now()
            print("\n🔑 Authenticating with Groww (TOTP flow)...")
            access_token = GrowwAPI.get_access_token(api_key=totp_token, totp=totp_code)
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("   If this is a 400 Bad Request on the API Key + Secret flow, the key/secret pair")
        print("   likely needs to be re-approved today on the Groww Cloud API Keys page.")
        raise SystemExit(1)

    groww = GrowwAPI(access_token)
    print("✅ Ready to Groww\n")
    return groww


# =====================================================================
# INSTRUMENT SEARCH / SELECT ("dropdown")
# =====================================================================

def load_nse_equity_symbols():
    print("📥 Downloading instrument list from Groww...")
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
# IST TIME HELPERS
# =====================================================================

def get_time_ist(label="run"):
    """Asks for a HH:MM (24-hour, IST) time and returns a timezone-aware
    datetime for the next occurrence of that time (today, or tomorrow if
    that time already passed today)."""
    print(f"\n🕒 When should the {label} happen? (Indian Standard Time)")
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
            run_at += timedelta(days=1)
            print(f"ℹ️ That time has already passed today, scheduling for tomorrow: {run_at.strftime('%Y-%m-%d %H:%M')} IST")
        else:
            print(f"✅ Scheduled for: {run_at.strftime('%Y-%m-%d %H:%M')} IST")

        confirm = input("Confirm this time? (y/n): ").strip().lower()
        if confirm == "y":
            return run_at


def wait_until(run_at, label="scheduled time"):
    print(f"\n⏳ Waiting until {run_at.strftime('%Y-%m-%d %H:%M')} IST ({label})...")
    while True:
        now = datetime.now(IST)
        remaining = (run_at - now).total_seconds()
        if remaining <= 0:
            break
        sleep_chunk = min(remaining, 300)
        time.sleep(sleep_chunk)
        now = datetime.now(IST)
        print(f"   Still waiting... {int((run_at - now).total_seconds())} seconds left")


# =====================================================================
# OPTIONS / F&O HELPERS
# =====================================================================

# =====================================================================
# OPTIONS / F&O HELPERS
# (Built entirely from the public instruments.csv — no live-data API
# calls, since those require a Groww subscription/role your key may not
# have. This means expiries and strikes shown are always REAL contracts
# that actually exist, never guessed or randomly generated.)
# =====================================================================

_fno_cache = {}  # underlying_symbol -> list of contract dicts (avoids re-downloading per call)


def load_fno_contracts(underlying_symbol):
    """Downloads the instruments CSV (once, cached) and returns every
    CE/PE option contract for the given F&O underlying (e.g. 'NIFTY',
    'RELIANCE'). Each contract: {trading_symbol, option_type, expiry_date,
    strike_price (float), lot_size (int)}."""
    underlying_symbol = underlying_symbol.upper()
    if underlying_symbol in _fno_cache:
        return _fno_cache[underlying_symbol]

    print(f"📥 Downloading instrument list to find {underlying_symbol} option contracts...")
    with urllib.request.urlopen(INSTRUMENTS_URL) as response:
        raw = response.read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(raw))
    contracts = []
    for row in reader:
        if row.get("segment") != "FNO":
            continue
        if row.get("underlying_symbol") != underlying_symbol:
            continue
        if row.get("instrument_type") not in ("CE", "PE"):
            continue
        try:
            contracts.append({
                "trading_symbol": row["trading_symbol"],
                "option_type": row["instrument_type"],
                "expiry_date": row["expiry_date"],
                "strike_price": float(row["strike_price"]),
                "lot_size": int(float(row["lot_size"])),
            })
        except (ValueError, KeyError):
            continue

    _fno_cache[underlying_symbol] = contracts
    print(f"✅ Found {len(contracts)} option contracts for {underlying_symbol}.\n")
    return contracts


def get_available_expiries(contracts):
    """Returns sorted unique expiry dates (as 'YYYY-MM-DD' strings) that
    actually exist for this underlying."""
    expiries = sorted(set(c["expiry_date"] for c in contracts))
    return expiries


def choose_expiry(contracts):
    """Shows a numbered menu of REAL available expiry dates and returns
    the one the user picks."""
    expiries = get_available_expiries(contracts)
    if not expiries:
        raise SystemExit("❌ No F&O contracts found for this underlying — check the symbol spelling.")

    print("\nAvailable expiry dates:")
    for i, exp in enumerate(expiries, start=1):
        print(f"  {i}. {exp}")

    while True:
        choice = input(f"Enter a number (1-{len(expiries)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(expiries):
                return expiries[idx]
        except ValueError:
            pass
        print("❌ Invalid selection, try again.")


def get_available_strikes(contracts, expiry_date, option_type):
    """Returns sorted unique real strike prices (floats) available for
    this expiry + option type (CE or PE)."""
    strikes = sorted(set(
        c["strike_price"] for c in contracts
        if c["expiry_date"] == expiry_date and c["option_type"] == option_type
    ))
    return strikes


def nearest_available_strike(strikes, target_price):
    """Given a list of real available strikes, returns the one closest
    to target_price. Never invents a strike that doesn't exist."""
    if not strikes:
        return None
    return min(strikes, key=lambda s: abs(s - target_price))


def find_contract(contracts, expiry_date, strike_price, option_type):
    """Finds the exact contract dict (with trading_symbol) matching an
    expiry + strike + option type."""
    for c in contracts:
        if c["expiry_date"] == expiry_date and c["strike_price"] == strike_price and c["option_type"] == option_type:
            return c
    return None


def get_fno_lot_size(underlying_symbol):
    """Returns the lot size for the given F&O underlying, or None if not found."""
    contracts = load_fno_contracts(underlying_symbol)
    if contracts:
        return contracts[0]["lot_size"]
    return None
