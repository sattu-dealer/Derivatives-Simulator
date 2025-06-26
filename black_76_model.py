#The implementation of black 76 model, a variant of the black-scholes model
#Works on index and stock options with monthly expiry
#Implied Volatility (IV) is calculated using bisection method from LTP
#Model was tested on live derivatives market data from NSE on NIFTY50 option chain
#Last Tested on 18th June, 2025

import numpy as np
from scipy.stats import norm

def black_76_price(futures_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type):
    if time_to_expiry <= 0:
        if option_type == 'call':
            return max(0, futures_price - strike_price)
        else:
            return max(0, strike_price - futures_price)

    if volatility <= 1e-6 or time_to_expiry <= 1e-6:
        return max(0, futures_price - strike_price) if option_type == 'call' else max(0, strike_price - futures_price)
        
    d1 = (np.log(futures_price / strike_price) + (volatility**2 / 2) * time_to_expiry) / \
         (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)

    if option_type == 'call':
        price = np.exp(-risk_free_rate * time_to_expiry) * \
                (futures_price * norm.cdf(d1) - strike_price * norm.cdf(d2))
    elif option_type == 'put':
        price = np.exp(-risk_free_rate * time_to_expiry) * \
                (strike_price * norm.cdf(-d2) - futures_price * norm.cdf(-d1))
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return price

def calculate_implied_volatility(
    market_price, futures_price, strike_price, time_to_expiry, risk_free_rate, option_type,
    tolerance=0.0001, max_iterations=200, low_vol=0.001, high_vol=5.0
):
    intrinsic_value = max(0, futures_price - strike_price) if option_type == 'call' else max(0, strike_price - futures_price)
    if market_price < intrinsic_value:
        print(f"Warning: Market price {market_price:.2f} for {option_type.upper()} {strike_price} is less than intrinsic value {intrinsic_value:.2f}. "
              "Implied volatility cannot be found. Using minimum volatility: {low_vol*100:.2f}%")
        return low_vol
    
    for i in range(max_iterations):
        mid_vol = (low_vol + high_vol) / 2
        
        if mid_vol <= 1e-6:
            mid_vol = 1e-6

        calculated_price = black_76_price(
            futures_price, strike_price, time_to_expiry, risk_free_rate, mid_vol, option_type
        )
        
        diff = calculated_price - market_price

        if abs(diff) < tolerance:
            return mid_vol
        
        if diff < 0:
            low_vol = mid_vol
        else:
            high_vol = mid_vol
        
        if abs(high_vol - low_vol) < tolerance / 100:
            break

    print(f"Warning: Could not converge to implied volatility within tolerance for market price {market_price:.2f}. "
          f"Current range: [{low_vol*100:.2f}%, {high_vol*100:.2f}%]. Returning best estimate: {mid_vol*100:.2f}%.")
    return mid_vol
