import requests
import numpy as np
import json
import math
from time import sleep
from tabulate import tabulate
import datetime
import random

def round_up(value):
    if value < 1:
        return round(value, 8)  # Keep up to 8 decimal places for very small numbers
    else:
        return round(value, 2)  # Round up to 2 decimal places for larger numbers

def fetch_data(url, retries=3, backoff_factor=1):
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            print(f"Attempt {attempt+1}: Error occurred: {err}")
            sleep(backoff_factor)
            backoff_factor *= 2  # Exponential backoff
    print("Max retries exceeded.")
    return None

def exponential_backoff(retries, backoff_factor=1):
    sleep(backoff_factor)
    return backoff_factor * 2  # Double the backoff interval

def fetch_all_symbols():
    url = "https://api-futures.kucoin.com/api/v1/contracts/active"
    data = fetch_data(url)
    if data and 'data' in data:
        # Ensuring that the data field which contains contracts info is parsed correctly
        return [item['symbol'] for item in data['data']]
    return []


def fetch_crypto_indicators(symbol, exchanges=['BYBIT', 'BINANCE']):
    indicators = [
        "open", "close", "volume", "VWAP|60", "RSI|60", "ADX|60", "ATR|60",
        "MACD.macd", "MACD.signal", "Stoch.K", "Stoch.D", 
        "EMA5", "EMA10", "EMA20", "EMA30", "EMA50", "EMA100", "EMA200",
        "Pivot.M.Classic.Middle", "Pivot.M.Classic.R1", "Pivot.M.Classic.S1"
    ]

    # Clean up symbol name
    clean_symbol = symbol.replace("USDTM", "USDT").replace("USDM", "USDT")
    
    symbol_formats = []
    if 'BYBIT' in exchanges:
        symbol_formats.append(f"BYBIT:{clean_symbol}")  # Remove .P suffix
    if 'BINANCE' in exchanges:
        symbol_formats.append(f"BINANCE:{clean_symbol}")

    for ticker in symbol_formats:
        try:
            url = "https://scanner.tradingview.com/crypto/scan"
            request_body = {
                "symbols": {"tickers": [ticker]},
                "columns": indicators
            }
            response = requests.post(url, json=request_body)
            
            if response.ok:
                data = response.json().get('data', [])
                if data and isinstance(data, list) and data[0].get('d'):
                    indicators_data = data[0]['d']
                    # Don't modify the data with random values
                    indicators_data = [0.0 if x is None else x for x in indicators_data]
                    result = dict(zip(indicators, indicators_data))
                    if result.get('close') is not None:  # Only return if we have valid price data
                        return result
            else:
                continue
        except Exception as e:
            continue

    return {}

def analyze_order_book(symbol):
    url = f"https://api.kucoin.com/api/v1/level2/depth500?symbol={symbol}"
    order_book = fetch_data(url)
    if order_book and 'data' in order_book:
        bids = [(float(bid[0]), float(bid[1])) for bid in order_book['data']['bids']]
        asks = [(float(ask[0]), float(ask[1])) for ask in order_book['data']['asks']]
        return bids, asks
    return [], []

def predict_price_movement_advanced(bids, asks, indicators, klines):
    if not klines or not isinstance(klines, list):
        print("Error: Invalid or missing klines data.")
        return None, None, None

    try:
        closing_prices = [float(kline[4]) for kline in klines if len(kline) > 4 and kline[4]]
        if not closing_prices:
            print("Error: No closing prices available in klines.")
            return None, None, None

        average_closing_price = sum(closing_prices) / len(closing_prices)
        predicted_change = (average_closing_price - closing_prices[-1]) / closing_prices[-1] * 100
        predicted_price = closing_prices[-1] * (1 + predicted_change / 100)
        standard_deviation = np.std(closing_prices)
        confidence = max(0, 100 - standard_deviation)

        return predicted_price, predicted_change, confidence
    except Exception as e:
        print(f"Error processing klines data: {str(e)}")
        return None, None, None



def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def advanced_trading_strategy(indicators, last_price):
    # Extract key indicators or set defaults safely
    atr = safe_float(indicators.get('ATR|60'), 0.01 * last_price)
    rsi = safe_float(indicators.get('RSI|60'), 50)
    macd = safe_float(indicators.get('MACD.macd'), 0)
    macd_signal = safe_float(indicators.get('MACD.signal'), 0)
    stoch_k = safe_float(indicators.get('Stoch.K'), 50)
    stoch_d = safe_float(indicators.get('Stoch.D'), 50)
    vwap = safe_float(indicators.get('VWAP|60'), last_price)
    ema5 = safe_float(indicators.get('EMA5'), last_price)
    ema10 = safe_float(indicators.get('EMA10'), last_price)
    ema20 = safe_float(indicators.get('EMA20'), last_price)
    ema50 = safe_float(indicators.get('EMA50'), last_price)
    ema200 = safe_float(indicators.get('EMA200'), last_price)
    pivot_middle = safe_float(indicators.get('Pivot.M.Classic.Middle'), last_price)
    pivot_r1 = safe_float(indicators.get('Pivot.M.Classic.R1'), last_price)
    pivot_s1 = safe_float(indicators.get('Pivot.M.Classic.S1'), last_price)

    # Enhanced trend analysis
    short_trend = ema5 > ema10 and ema10 > ema20
    medium_trend = ema20 > ema50
    long_trend = ema50 > ema200
    
    # Volume-based trend confirmation
    volume = safe_float(indicators.get('volume'), 0)
    volume_trend = volume > safe_float(indicators.get('volume_ma', 0), 0)
    
    # Advanced MACD analysis
    macd_trend = macd > macd_signal
    macd_strength = abs(macd - macd_signal) / last_price
    
    # Enhanced momentum analysis
    stoch_trend = stoch_k > stoch_d
    stoch_oversold = stoch_k < 20 and stoch_d < 20
    stoch_overbought = stoch_k > 80 and stoch_d > 80
    
    # Price relative to VWAP
    vwap_trend = last_price > vwap
    
    # Pivot point analysis
    pivot_resistance = last_price < pivot_r1
    pivot_support = last_price > pivot_s1
    
    # Comprehensive trend score (0-100)
    trend_score = 0
    trend_score += 20 if short_trend else 0
    trend_score += 15 if medium_trend else 0
    trend_score += 10 if long_trend else 0
    trend_score += 15 if volume_trend else 0
    trend_score += 15 if macd_trend else 0
    trend_score += 15 if vwap_trend else 0
    trend_score += 10 if pivot_support and not pivot_resistance else (-10 if pivot_resistance and not pivot_support else 0)

    # Dynamic position sizing based on trend strength
    position_size_factor = trend_score / 100

    # Enhanced entry conditions
    strong_buy = (
        trend_score > 75 and
        not stoch_overbought and
        macd_trend and
        vwap_trend and
        pivot_support
    )
    
    strong_sell = (
        trend_score < 25 and
        not stoch_oversold and
        not macd_trend and
        not vwap_trend and
        pivot_resistance
    )

    # Dynamic ATR multiplier based on trend strength
    atr_multiplier = 2 + (trend_score / 100)

    if strong_buy:
        entry_price = round_up(last_price * (1 + 0.001 * position_size_factor))
        take_profit = round_up(entry_price + atr * atr_multiplier)
        stop_loss = round_up(entry_price - (atr * (atr_multiplier * 0.5)))
    elif strong_sell:
        entry_price = round_up(last_price * (1 - 0.001 * position_size_factor))
        take_profit = round_up(entry_price - atr * atr_multiplier)
        stop_loss = round_up(entry_price + (atr * (atr_multiplier * 0.5)))
    else:
        entry_price = round_up(last_price)
        take_profit = round_up(entry_price + atr)
        stop_loss = round_up(entry_price - atr)

    # Enhanced success chance calculation
    success_chance = calculate_enhanced_success_chance(
        trend_score, macd_strength, position_size_factor,
        stoch_k, stoch_d, vwap_trend, volume_trend
    )
    
    # Optimized leverage based on multiple factors
    leverage = calculate_optimized_leverage(success_chance, atr / last_price, trend_score)

    return entry_price, take_profit, stop_loss, leverage

def calculate_enhanced_success_chance(trend_score, macd_strength, position_size_factor,
                                   stoch_k, stoch_d, vwap_trend, volume_trend):
    base_chance = trend_score * 0.6  # Increased from 0.5 for better base chance
    
    # Add additional probability based on other factors
    base_chance += 12 if macd_strength > 0.0008 else 0  # Slightly more lenient MACD threshold
    base_chance += 12 if abs(stoch_k - stoch_d) < 15 else 0  # More lenient stochastic convergence
    base_chance += 12 if vwap_trend else 0  # Increased VWAP importance
    base_chance += 12 if volume_trend else 0  # Increased volume importance
    base_chance += 12 * position_size_factor  # Increased position confidence impact
    
    # Less aggressive diminishing returns
    final_chance = 50 + (base_chance - 50) * 0.9  # Changed from 0.8 to 0.9
    
    return max(0, min(100, final_chance))

def calculate_optimized_leverage(success_chance, volatility, trend_score):
    # Base leverage on success chance with stricter limits
    base_leverage = success_chance / 20  # Reduced from 15 to 20 for more conservative leverage
    
    # Adjust for volatility
    volatility_factor = 1 - (volatility * 10)
    leverage = base_leverage * volatility_factor
    
    # Adjust for trend strength
    trend_factor = trend_score / 100
    leverage = leverage * (0.8 + (0.4 * trend_factor))
    
    # More conservative leverage caps
    if success_chance > 85:
        max_leverage = 5  # Reduced from 7
    elif success_chance > 75:
        max_leverage = 4  # Reduced from 5
    elif success_chance > 65:
        max_leverage = 3  # Reduced from 4
    else:
        max_leverage = 2  # Reduced from 3
        
    return min(math.ceil(leverage), max_leverage)

import json

def calculate_trend_score(data):
    last_price = safe_float(data.get('close'))
    trend_score = 0
    
    # EMA trends (35 points total)
    trend_score += 15 if safe_float(data.get('EMA5', 0)) > safe_float(data.get('EMA10', 0)) else 0
    trend_score += 10 if safe_float(data.get('EMA20', 0)) > safe_float(data.get('EMA50', 0)) else 0
    trend_score += 10 if safe_float(data.get('EMA50', 0)) > safe_float(data.get('EMA200', 0)) else 0
    
    # MACD trend (20 points)
    trend_score += 20 if safe_float(data.get('MACD.macd', 0)) > safe_float(data.get('MACD.signal', 0)) else 0
    
    # Price vs VWAP (25 points)
    trend_score += 25 if last_price > safe_float(data.get('VWAP|60'), last_price) else 0
    
    # RSI momentum (20 points)
    rsi = safe_float(data.get('RSI|60', 50))
    if 40 <= rsi <= 60:  # Neutral zone
        trend_score += 10
    elif 60 < rsi <= 70:  # Bullish but not overbought
        trend_score += 20
    elif 30 <= rsi < 40:  # Oversold but recovering
        trend_score += 15
    
    return trend_score

def check_market_correlation(symbol, results, max_correlation=0.7):
    """Check if the symbol is highly correlated with existing positions."""
    try:
        if not results or len(results) < 2:
            return True
        
        symbol_prices = [float(results[symbol].get('close', 0)) for _ in range(10)]
        if all(price == 0 for price in symbol_prices):
            return True
            
        for other_symbol in results:
            if other_symbol != symbol:
                other_prices = [float(results[other_symbol].get('close', 0)) for _ in range(10)]
                if all(price == 0 for price in other_prices):
                    continue
                try:
                    correlation = np.corrcoef(symbol_prices, other_prices)[0, 1]
                    if not np.isnan(correlation) and abs(correlation) > max_correlation:
                        return False
                except:
                    continue
        return True
    except Exception as e:
        print(f"Correlation check error for {symbol}: {str(e)}")
        return True

def provide_trading_recommendation(results, min_success_chance):
    if not results:
        print("No valid results to analyze.")
        return []
        
    table = []
    daily_trades = 0
    max_daily_trades = 3
    max_portfolio_risk = 0.02
    
    for symbol, data in results.items():
        try:
            if daily_trades >= max_daily_trades:
                break
                
            last_price = data.get('close')
            if last_price is None:
                continue
                
            last_price = float(last_price)
            if last_price <= 0:
                continue
                
            if not check_market_correlation(symbol, results):
                continue
                
            entry_price, take_profit, stop_loss, leverage = advanced_trading_strategy(data, last_price)
            
            position_risk = abs(entry_price - stop_loss) / entry_price
            if position_risk > max_portfolio_risk:
                continue
                
            trend_score = calculate_trend_score(data)
            success_chance = calculate_enhanced_success_chance(
                trend_score=trend_score,
                macd_strength=abs(safe_float(data.get('MACD.macd', 0)) - safe_float(data.get('MACD.signal', 0))) / last_price,
                position_size_factor=1.0,
                stoch_k=safe_float(data.get('Stoch.K', 50)),
                stoch_d=safe_float(data.get('Stoch.D', 50)),
                vwap_trend=last_price > safe_float(data.get('VWAP|60'), last_price),
                volume_trend=True
            )
            
            if success_chance >= min_success_chance:
                trailing_stop = round_up(entry_price * 0.02)
                
                table.append({
                    "Symbol": symbol,
                    "Entry Price": entry_price,
                    "Take Profit": take_profit,
                    "Stop Loss": stop_loss,
                    "Trailing Stop": trailing_stop,
                    "Chances of Success": success_chance,
                    "Leverage": leverage,
                    "Position Risk": f"{position_risk*100:.2f}%"
                })
                daily_trades += 1
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            continue

    table.sort(key=lambda x: (x['Chances of Success'], -float(x['Position Risk'].rstrip('%'))), reverse=True)

    if len(table) > 0:
        with open('signals.json', 'w') as file:
            json.dump(table[:3], file, indent=4)
        print(f"\nSaved top {min(3, len(table))} trading signals to 'signals.json'")
        print("\nTop opportunities:")
        for t in table[:3]:
            print(f"{t['Symbol']}: {t['Chances of Success']}% success, {t['Position Risk']} risk, {t['Leverage']}x leverage")
    else:
        print("No trading opportunities meet the criteria.")
    
    return table

import random

def shuffle_and_prioritize_symbols(symbols, previous_symbols, max_symbols=500):
    random.shuffle(symbols)  # Shuffle the list of symbols to randomize order
    # Prioritize symbols not in the last traded set
    new_symbols = [symbol for symbol in symbols if symbol not in previous_symbols]
    remaining_symbols = [symbol for symbol in symbols if symbol in previous_symbols]
    prioritized_list = new_symbols + remaining_symbols
    return prioritized_list[:max_symbols]  # Return a limited number of symbols to analyze

def main():
    print("Using a minimum success chance of 70%.")
    print("\nFetching market data...")
    
    # Get all available symbols
    symbols = fetch_all_symbols()
    if not symbols:
        print("No symbols found.")
        return

    for symbol in symbols:
        print(f"Found data for {symbol}")

    print(f"\nAnalyzing {len(symbols)} symbols...")
    
    trading_signals = []
    for symbol in symbols:
        indicators = fetch_crypto_indicators(symbol)
        if not indicators or 'close' not in indicators:
            continue
            
        last_price = indicators['close']
        entry_price, take_profit, stop_loss, leverage = advanced_trading_strategy(indicators, last_price)
        
        # Calculate success chance
        trend_score = calculate_trend_score(indicators)
        macd_strength = abs(indicators.get('MACD.macd', 0) - indicators.get('MACD.signal', 0)) / last_price
        position_size_factor = trend_score / 100
        stoch_k = indicators.get('Stoch.K', 50)
        stoch_d = indicators.get('Stoch.D', 50)
        vwap_trend = last_price > indicators.get('VWAP|60', last_price)
        volume_trend = indicators.get('volume', 0) > 0
        
        success_chance = calculate_enhanced_success_chance(
            trend_score, macd_strength, position_size_factor,
            stoch_k, stoch_d, vwap_trend, volume_trend
        )
        
        # Calculate position risk
        atr = indicators.get('ATR|60', last_price * 0.01)
        risk_percentage = (abs(entry_price - stop_loss) / entry_price) * 100
        
        # Filter for good opportunities (now accepting more signals)
        if success_chance > 70 and risk_percentage < 2:  # Relaxed criteria
            signal = {
                "Symbol": symbol,
                "Entry Price": entry_price,
                "Take Profit": take_profit,
                "Stop Loss": stop_loss,
                "Position Risk": f"{risk_percentage:.2f}%",
                "Leverage": min(round(leverage), 5),  # Cap at 5x
                "Trailing Stop": 2  # Default trailing stop
            }
            trading_signals.append(signal)
    
    # Sort by success chance but keep multiple signals
    trading_signals.sort(key=lambda x: float(x["Position Risk"].rstrip('%')))
    
    # Save all qualifying signals (up to 5)
    max_signals = min(5, len(trading_signals))
    if max_signals > 0:
        with open('signals.json', 'w') as f:
            json.dump(trading_signals[:max_signals], f, indent=4)
        print(f"\nSaved top {max_signals} trading signals to 'signals.json'")
        
        print("\nTop opportunities:")
        for signal in trading_signals[:max_signals]:
            print(f"{signal['Symbol']}: {success_chance}% success, {signal['Position Risk']} risk, {signal['Leverage']}x leverage")
        
        print("\nFound trading opportunities!")
        print("----------------------------")
        for signal in trading_signals[:max_signals]:
            print(f"\nSymbol: {signal['Symbol']}")
            print(f"Success Chance: {success_chance}%")
            print(f"Entry: {signal['Entry Price']}")
            print(f"Take Profit: {signal['Take Profit']}")
            print(f"Stop Loss: {signal['Stop Loss']}")
            print(f"Risk: {signal['Position Risk']}")
            print(f"Leverage: {signal['Leverage']}x")
    else:
        print("\nNo trading opportunities found meeting the criteria.")
        # Save empty array to signals.json
        with open('signals.json', 'w') as f:
            json.dump([], f)

# Ensure the script is executed as a main program
if __name__ == "__main__":
    main()


