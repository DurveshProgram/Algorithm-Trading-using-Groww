# Groww Auto Trade — VS Code Setup

## 1. Requirements
- Python 3.9 or higher (needed for IST timezone handling)
- VS Code with the Python extension installed
- An active Groww Trading API subscription
- Your Groww API Key & Secret (from https://groww.in/trade-api — "Generate API key")

## 2. Setup
Open a terminal inside this folder in VS Code and run:

```bash
pip install -r requirements.txt
```

## 3. Run

```bash
python groww_auto_trade.py
```

The script will ask you, in order:
1. Which login method to use:
   - **Option 1 — API Key + Secret**: simpler, but Groww requires you to
     re-approve this key/secret pair every day on the
     [Groww Cloud API Keys page](https://groww.in/trade-api/api-keys). If you
     see a `400 Bad Request` on login, this is almost always why — go
     re-approve today's key and try again.
   - **Option 2 — TOTP (recommended)**: generated from a TOTP token + secret
     (also from the API Keys page, under "Generate TOTP token"). This method
     has no daily expiry, so it's more reliable for scheduled/unattended runs.
2. Your credentials for whichever method you picked. **Note: secrets are
   typed visibly on screen**, not masked — Windows' `getpass` hidden-input
   turned out to hang/refuse keystrokes on this machine's console setup, so
   the script uses plain visible input instead for reliability. Make sure
   no one's looking over your shoulder, and consider clearing the terminal
   (`cls`) after logging in. The script reports how many characters it
   captured so you can immediately tell if a paste didn't register.
3. A search term to find your stock (e.g. "IDEA"), then a number to pick it from the list.
4. The time you want the trade to run, in 24-hour IST format (e.g. `09:20`).

It will then wait until that time, place a MARKET BUY order for quantity 1,
wait 10 seconds, and place a MARKET SELL order for the same stock.

## Notes
- This places **real orders with real money** if your Groww account is live — double-check
  the symbol, quantity, and time before confirming.
- The script must stay running (terminal open) until the scheduled time and trade complete —
  closing VS Code or your terminal will stop it.
- Your API key/secret are typed at runtime and never saved to disk.
- Uses `PRODUCT_MIS` (intraday) and `ORDER_TYPE_MARKET` — same as your original script.
