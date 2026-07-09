# =====================
# This is a Sample script that places a Buy order, waits 10 seconds, and then places a Sell order.
# =====================

import time
from growwapi import GrowwAPI

# =====================
# STEP 1: Setup
# =====================

# === Setup Groww API ===
# Please use the "Generate API key" option on the API keys page to obtain the API key and Secret.

user_api_key = "eyJraWQiOiJaTUtjVXciLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjI1NzE2NTE0NDksImlhdCI6MTc4MzI1MTQ0OSwibmJmIjoxNzgzMjUxNDQ5LCJzdWIiOiJ7XCJ0b2tlblJlZklkXCI6XCI1ZDU3ODg4YS00OWQwLTQ5MTQtODRhMC1jYjc2ODlkMjA1MDJcIixcInZlbmRvckludGVncmF0aW9uS2V5XCI6XCJlMzFmZjIzYjA4NmI0MDZjODg3NGIyZjZkODQ5NTMxM1wiLFwidXNlckFjY291bnRJZFwiOlwiZjk5YmJiZWItZTZjOS00NzQ5LTkwNDQtNzNiNjMxYzQ4NDgxXCIsXCJkZXZpY2VJZFwiOlwiNTM3NzMyZmMtOGUzMy01Nzg4LTk5ZGYtMThiOWI0ZDNkYTkxXCIsXCJzZXNzaW9uSWRcIjpcImQ0MGMwMTc2LWEwMWMtNDlhMC05ODBlLTYyYzA2YTY4MzQ4MFwiLFwiYWRkaXRpb25hbERhdGFcIjpcIno1NC9NZzltdjE2WXdmb0gvS0EwYkVpOEh6VUlJdFgyTmFKVFJUZ1ZscU5STkczdTlLa2pWZDNoWjU1ZStNZERhWXBOVi9UOUxIRmtQejFFQisybTdRPT1cIixcInJvbGVcIjpcImF1dGgtdG90cFwiLFwic291cmNlSXBBZGRyZXNzXCI6XCIyNDA5OjQwYzA6NzY6NTAzNTo3Y2VjOjIwM2Y6NDY3YToxMGJkLDE3Mi42OS4xNzkuNjIsMzUuMjQxLjIzLjEyM1wiLFwidHdvRmFFeHBpcnlUc1wiOjI1NzE2NTE0NDk2MDQsXCJ2ZW5kb3JOYW1lXCI6XCJncm93d0FwaVwifSIsImlzcyI6ImFwZXgtYXV0aC1wcm9kLWFwcCJ9.wzO7iAVwUN3wrQYmPpTsel7xnZE7G-knzFdTAwXGIen0ksYita24ws-5xzUsqxZn5U_nljPFXwpnHmljEJArrA"

user_secret = "eqX5$hGS(*drppxbCGTYun%)Za2vT$$#"


access_token = GrowwAPI.get_access_token(api_key = user_api_key, secret = user_secret) 
# Use access_token to initiate GrowwAPi
groww = GrowwAPI(access_token)
print("✅ Ready to Groww")

# =====================
# STEP 2: Place BUY Order
# =====================

trading_symbol = "IDEA"  #Vodafone Idea Ltd
quantity = 1    #Set the quantity you want to buy 
 

#Ensure you have sufficient funds in your Groww account for this order

try:
    # Place a MARKET BUY order
    print(f"Placing MARKET BUY order for {trading_symbol}")
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
    # This will print the order ID of the placed order

except Exception as e: 
    print(f"❌ Failed to place BUY order: {e}")
    exit(1)

# =====================
# STEP 3: Wait 10 seconds
# =====================
print("⏳ Waiting for 10 secs before placing SELL order...")
time.sleep(10)

# =====================
# STEP 4: Place SELL Order
# =====================

#Place a MARKET SELL order
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
    # This will print the order ID of the placed order

except Exception as e:
    print(f"❌ Failed to place SELL order: {e}")