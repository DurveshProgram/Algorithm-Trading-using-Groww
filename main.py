"""
=====================================================================
main.py
Run this file to log in once, then pick which strategy to run — the
menu is built automatically by scanning the strategies/ folder. You
never need to edit this file to add a new strategy: just drop a new
file into strategies/ (see strategy_loader.py for the template) and
it will appear in the menu, numbered automatically, next time you run.

After a strategy finishes (or fails), you can run another without
logging in again.
=====================================================================
"""

import groww_common as gc
import strategy_options
import strategy_loader


def choose_strategy(entries):
    print("\n" + "=" * 60)
    print("📈 Choose a strategy to run")
    print("=" * 60)
    for i, e in enumerate(entries, start=1):
        tag = "Equity" if e["category"] == "equity" else "Options"
        print(f"  {i}. [{tag}] {e['label']}")

    while True:
        choice = input(f"Enter a number (1-{len(entries)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(entries):
                return entries[idx]
        except ValueError:
            pass
        print("❌ Invalid selection, try again.")


def main():
    groww = gc.login()
    symbols = gc.load_nse_equity_symbols()

    entries = strategy_loader.discover_strategies()
    if not entries:
        raise SystemExit("❌ No strategies found in the strategies/ folder.")

    while True:
        entry = choose_strategy(entries)
        print(f"\n▶️ Running: {entry['label']}\n")

        try:
            if entry["category"] == "equity":
                entry["module"].run_strategy(groww, gc, symbols)
            else:  # "options"
                strategy_options.run_for_module(groww, entry["module"])
        except Exception as e:
            print(f"❌ Strategy stopped unexpectedly: {e}")

        print("\n" + "=" * 60)
        again = input("Run another strategy without logging in again? (y/n): ").strip().lower()
        if again != "y":
            print("👋 Exiting. No more orders will be placed.")
            break


if __name__ == "__main__":
    main()
