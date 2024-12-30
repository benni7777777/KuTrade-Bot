import requests
import numpy as np
import json
import math
from time import sleep
import datetime
import hmac
import hashlib
import time
import uuid
import os
import base64
from dotenv import load_dotenv  # Import this

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('KUCOIN_KEY')
API_SECRET = os.getenv('KUCOIN_SECRET')
API_PASSPHRASE = os.getenv('KUCOIN_PASSPHRASE')

# Access environment variables securely
API_KEY = os.getenv('KUCOIN_KEY')
API_SECRET = os.getenv('KUCOIN_SECRET')
API_PASSPHRASE = os.getenv('KUCOIN_PASSPHRASE')

if not all([API_KEY, API_SECRET, API_PASSPHRASE]):
    raise ValueError("API keys and passphrase must be set")

def get_kucoin_headers(endpoint, query_string='', method='GET'):
    now = int(time.time() * 1000)  # Corrected call to time()
    str_to_sign = f"{now}{method}{endpoint}{query_string}"
    signature = hmac.new(API_SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()
    passphrase = hmac.new(API_SECRET.encode('utf-8'), API_PASSPHRASE.encode('utf-8'), hashlib.sha256).digest()
    
    headers = {
        "KC-API-SIGN": base64.b64encode(signature).decode('utf-8'),
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": API_KEY,
        "KC-API-PASSPHRASE": base64.b64encode(passphrase).decode('utf-8'),
        "KC-API-KEY-VERSION": "2"
    }
    return headers

def fetch_all_symbols():
    url = "https://api-futures.kucoin.com/api/v1/contracts/active"
    headers = get_kucoin_headers('/api/v1/contracts/active')
    data = fetch_data(url, headers)
    if data is None:
        print("Error fetching symbols. Skipping order placement.")
        return {}
    symbols_info = {}
    for item in data:
        print(item)
        symbols_info[item['symbol']] = item
    return symbols_info

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def adjust_price(price, tick_size):
    """Adjust price to be a multiple of the tick size and return as string for the API."""
    if tick_size == 0:  # Handle zero tick size
        tick_size = 0.1  # Default to 0.1 if tick size is 0
    adjusted_price = round(price / tick_size) * tick_size
    return "{:.8f}".format(adjusted_price).rstrip('0').rstrip('.')

def adjust_quantity(capital, price, leverage, lot_size, max_size):
    """Adjust the quantity to ensure it does not exceed capital limitations and it must be an integer."""
    max_possible_quantity = capital / (price / leverage)
    adjusted_quantity = np.floor(max_possible_quantity / lot_size) * lot_size
    return int(max(lot_size, min(adjusted_quantity, max_size)))  # Ensure the quantity is an integer


def load_trading_signals(filename='signals.json'):
    try:
        with open(filename, 'r') as file:
            signals = json.load(file)
            print(f"\nLoaded signals from {filename}:")
            for signal in signals:
                print(f"Symbol: {signal['Symbol']}")
                print(f"Entry: {signal['Entry Price']}")
                print(f"Risk: {signal['Position Risk']}")
                print(f"Leverage: {signal['Leverage']}x\n")
            return signals
    except FileNotFoundError:
        print(f"No signals file found ({filename})")
        return []
    except json.JSONDecodeError:
        print(f"Error reading signals file ({filename})")
        return []
    except Exception as e:
        print(f"Unexpected error loading signals: {str(e)}")
        return []


def fetch_data(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f"Error fetching data: {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None

def get_futures_balance(currency='USDT'):
    endpoint = "/api/v1/account-overview"
    query_string = f"?currency={currency}"
    headers = get_kucoin_headers(endpoint, query_string, 'GET')
    url = "https://api-futures.kucoin.com" + endpoint + query_string
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return float(response.json()['data']['availableBalance'])
    print(f"Error fetching futures balance: {response.status_code}, {response.text}")
    return 0

import time  # Ensure this is not overshadowed or misused in the code

def calculate_quantity(price, capital, leverage):
  """Calculate the maximum quantity that can be bought with the given capital at the specified leverage."""
  max_quantity = (capital * leverage) / price
  return max_quantity  # Return the float quantity for further adjustments

def place_stop_loss_and_take_profit(symbol, entry_price, stop_loss, take_profit, trailing_stop, quantity, side, symbols_info, futures_balance):
    tick_size = symbols_info[symbol]['tickSize']
    orders = {}
    
    # Opposite side for closing orders
    stop_side = 'sell' if side == 'buy' else 'buy'
    
    # Place Stop Loss as a market stop order
    stop_loss_params = {
        'symbol': symbol,
        'quantity': quantity,
        'leverage': 1,
        'futures_balance': futures_balance,
        'order_type': 'stop',  # Changed to just 'stop'
        'side': stop_side,
        'price': adjust_price(stop_loss, tick_size)
    }
    
    orders['stop_loss'] = place_order(**stop_loss_params)
    
    # Place Take Profit as a limit order
    take_profit_params = {
        'symbol': symbol,
        'quantity': quantity,
        'leverage': 1,
        'futures_balance': futures_balance,
        'order_type': 'limit',
        'side': stop_side,
        'price': adjust_price(take_profit, tick_size)
    }
    
    orders['take_profit'] = place_order(**take_profit_params)
    
    # Place backup stop as a market stop order
    backup_stop_price = adjust_price(
        stop_loss * 0.99 if side == 'buy' else stop_loss * 1.01,
        tick_size
    )
    
    backup_stop_params = {
        'symbol': symbol,
        'quantity': quantity,
        'leverage': 1,
        'futures_balance': futures_balance,
        'order_type': 'stop',  # Changed to just 'stop'
        'side': stop_side,
        'price': backup_stop_price
    }
    
    orders['market_stop'] = place_order(**backup_stop_params)
    
    return orders

def place_trailing_stop(symbol, quantity, activation_price, callback_rate, side):
    endpoint = "/api/v1/orders"
    params = {
        'clientOid': str(uuid.uuid4()),
        'symbol': symbol,
        'side': side,
        'type': 'trailing_stop',
        'size': str(quantity),
        'activationPrice': str(activation_price),
        'callbackRate': str(callback_rate)
    }
    
    headers = get_kucoin_headers(endpoint, json.dumps(params), 'POST')
    url = "https://api-futures.kucoin.com" + endpoint
    
    try:
        response = requests.post(url, headers=headers, json=params)
        if response.status_code == 200:
            return response.json()
        print(f"Error placing trailing stop: {response.status_code}, {response.text}")
        return None
    except Exception as e:
        print(f"Failed to place trailing stop: {str(e)}")
        return None

def calculate_order_side(entry_price, take_profit):
    return "sell" if take_profit < entry_price else "buy"

def place_order(symbol, quantity, leverage, futures_balance, order_type, side="buy", price=None):
    client_oid = str(uuid.uuid4())
    
    # Base parameters
    params = {
        'clientOid': client_oid,
        'symbol': symbol,
        'side': side,
        'leverage': str(leverage),
        'size': str(quantity)
    }
    
    # Add specific parameters based on order type
    if order_type in ['limit', 'take_profit']:
        params['type'] = 'limit'
        params['price'] = str(price)
    elif order_type in ['stop_market', 'stop']:
        params['type'] = 'market'
        params['stop'] = 'down' if side == 'sell' else 'up'
        params['stopPrice'] = str(price)
        params['stopPriceType'] = 'MP'  # Mark Price
        params['reduceOnly'] = True
    elif order_type == 'market':
        params['type'] = 'market'

    endpoint = "/api/v1/orders"
    headers = get_kucoin_headers(endpoint, json.dumps(params), 'POST')
    url = "https://api-futures.kucoin.com" + endpoint

    try:
        response = requests.post(url, headers=headers, json=params)
        result = response.json()
        if response.status_code != 200:
            print(f"Error placing {order_type} order: {result}")
            print(f"Parameters used: {params}")
        return result
    except Exception as e:
        print(f"HTTP Request failed: {e}")
        return None

def determine_order_side(entry_price, take_profit):
    """Determine the side of the order based on entry and take profit prices."""
    return "buy" if take_profit > entry_price else "sell"

def main():
    symbols_info = fetch_all_symbols()
    futures_balance = get_futures_balance()
    
    if futures_balance <= 0:
        print("No available capital in futures wallet.")
        return

    trading_signals = load_trading_signals()
    if not trading_signals:
        print("No trading signals to process.")
        return

    # More conservative capital allocation
    max_positions = 3
    risk_per_trade = 0.02  # 2% risk per trade
    effective_capital_per_signal = min(
        futures_balance * risk_per_trade,
        futures_balance / max_positions
    )

    active_positions = 0
    for signal in trading_signals:
        if active_positions >= max_positions:
            break
            
        symbol = signal["Symbol"]
        if symbol not in symbols_info:
            print(f"Symbol {symbol} not found in available futures. Skipping...")
            continue

        # Use the exact values from the signal
        leverage = min(signal["Leverage"], 5)  # Cap at 5x for safety
        entry_price = signal["Entry Price"]  # We'll still use this for calculations
        take_profit = signal["Take Profit"]
        stop_loss = signal["Stop Loss"]
        trailing_stop = signal["Trailing Stop"]
        position_risk = float(signal["Position Risk"].rstrip('%')) / 100
        
        # Verify the trade still meets our risk criteria
        if position_risk > risk_per_trade:
            print(f"Skipping {symbol}: Position risk {position_risk*100}% exceeds maximum {risk_per_trade*100}%")
            continue
        
        # Calculate position size based on signal's risk
        risk_amount = effective_capital_per_signal * position_risk
        position_size = risk_amount / (abs(entry_price - stop_loss) / entry_price)
        
        side = calculate_order_side(entry_price, take_profit)
        
        # Adjust quantity based on lot size and max size
        lot_size = symbols_info[symbol]['lotSize']
        max_size = symbols_info[symbol]['maxOrderQty']
        quantity = adjust_quantity(position_size, entry_price, leverage, lot_size, max_size)

        print(f"\nPlacing orders for {symbol}:")
        print(f"Risk: {position_risk*100:.2f}%")
        print(f"Size: {quantity}")
        print(f"Leverage: {leverage}x")
        print(f"Side: {side}")

        # Place market order for immediate entry
        entry_order = place_order(
            symbol=symbol,
            quantity=quantity,
            leverage=leverage,
            futures_balance=futures_balance,
            order_type="market",  # Changed to market order
            side=side
        )

        if entry_order and entry_order.get('code') == '200000':
            print("\nMarket order placed! Setting up protection orders...")
            
            # Wait briefly for the order to be processed
            time.sleep(1)
            
            # Place protective orders
            protection_orders = place_stop_loss_and_take_profit(
                symbol, entry_price, stop_loss, take_profit, trailing_stop,
                quantity, side, symbols_info, futures_balance
            )
            
            print(f"\nOrders for {symbol}:")
            print(f"Entry (Market): {entry_order}")
            print(f"Stop Loss: {protection_orders.get('stop_loss')}")
            print(f"Take Profit: {protection_orders.get('take_profit')}")
            print(f"Backup Stop: {protection_orders.get('market_stop')}")
            
            active_positions += 1
            print(f"Active positions: {active_positions}/{max_positions}")
        else:
            print(f"Failed to place market order for {symbol}")

if __name__ == "__main__":
    main()
