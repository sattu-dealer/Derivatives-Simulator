#Handles the data for each put/call option in the portfolio

from datetime import datetime, timedelta
from black_76_model import black_76_price, calculate_implied_volatility

class OptionContract:
    def __init__(self, option_type, strike_price, expiry_date, quantity, position, initial_ltp,
                 futures_price_at_entry, risk_free_rate_at_entry, current_date_at_entry):
        if option_type not in ['call', 'put']:
            raise ValueError("option_type must be 'call' or 'put'")
        if position not in ['long', 'short']:
            raise ValueError("position must be 'long' or 'short'")
        if not isinstance(expiry_date, datetime):
            raise TypeError("expiry_date must be a datetime object")

        self.option_type = option_type
        self.strike_price = float(strike_price)
        self.expiry_date = expiry_date
        self.quantity = int(quantity)
        self.position = position
        self.initial_ltp = float(initial_ltp)

        time_to_expiry_days_at_entry = (self.expiry_date - current_date_at_entry).days
        time_to_expiry_years_at_entry = max(0.0001, time_to_expiry_days_at_entry / 365.0)

        self.initial_volatility = calculate_implied_volatility(
            market_price=self.initial_ltp,
            futures_price=futures_price_at_entry,
            strike_price=self.strike_price,
            time_to_expiry=time_to_expiry_years_at_entry,
            risk_free_rate=risk_free_rate_at_entry,
            option_type=self.option_type
        )
        print(f"Added Option: {self.position.upper()} {self.quantity} x {self.strike_price} {self.option_type.upper()} Exp: {self.expiry_date.strftime('%Y-%m-%d')} @ {self.initial_ltp:.2f} (Calculated IV: {self.initial_volatility:.2%})")

    def get_current_value(self, current_futures_price, current_date, risk_free_rate, volatility):
        time_to_expiry_days = (self.expiry_date - current_date).days
        time_to_expiry_years = max(0.0001, time_to_expiry_days / 365.0)

        option_price = black_76_price(
            futures_price=current_futures_price,
            strike_price=self.strike_price,
            time_to_expiry=time_to_expiry_years,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            option_type=self.option_type
        )
        return option_price

    def get_pnl_per_contract(self, current_futures_price, current_date, risk_free_rate, volatility):
        current_value = self.get_current_value(current_futures_price, current_date, risk_free_rate, volatility)
        if self.position == 'long':
            return current_value - self.initial_ltp
        else:
            return self.initial_ltp - current_value
