import requests
import hmac
import hashlib
import time
import os
import base64
import json
import uuid  # Ensure UUID is imported
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('KUCOIN_KEY')
API_SECRET = os.getenv('KUCOIN_SECRET')
API_PASSPHRASE = os.getenv('KUCOIN_PASSPHRASE')

def get_kucoin_headers(endpoint, query_string='', method='GET'):
    now = int(time.time() * 1000)
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

def close_position(symbol, size, leverage):
    endpoint = "/api/v1/orders"
    side = 'buy' if float(size) < 0 else 'sell'  # Determine the correct side to close the position
    order_type = 'market'
    client_oid = str(uuid.uuid4())  # Generate a unique client order ID
    params = {
        'clientOid': client_oid,
        'symbol': symbol,
        'side': side,
        'type': order_type,
        'size': abs(int(size)),  # Market order requires size as an integer
        'leverage': leverage,  # Add leverage to the order parameters
    }
    query_string = json.dumps(params)
    headers = get_kucoin_headers(endpoint, query_string, 'POST')
    url = f"https://api-futures.kucoin.com{endpoint}"
    
    response = requests.post(url, headers=headers, json=params)
    if response.status_code == 200:
        print(f"Closed position for {symbol}: {response.json()}")
    else:
        print(f"Failed to close position for {symbol}: {response.status_code} {response.text}")

def fetch_open_positions():
    endpoint = "/api/v1/positions"
    headers = get_kucoin_headers(endpoint, '', 'GET')
    url = f"https://api-futures.kucoin.com{endpoint}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        positions = [position for position in data if float(position['currentQty']) != 0]
        # Fetch leverage here if available or use default leverage value
        for position in positions:
            position['leverage'] = position.get('leverage', '1')  # Assuming '1' as default if not provided
        return positions
    else:
        print(f"Failed to fetch open positions: {response.text}")
        return []

def main():
    open_positions = fetch_open_positions()
    for position in open_positions:
        close_position(position['symbol'], position['currentQty'], position['leverage'])

if __name__ == "__main__":
    main()
