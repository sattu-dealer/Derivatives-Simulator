#Manages the data of our derivatives portfolio

from option_contract import OptionContract
from datetime import datetime

class OptionsPortfolio:
    def __init__(self):
        self.options = []

    def add_option(self, option_type, strike_price, expiry_date, quantity, position, initial_ltp,
                   futures_price_at_entry, risk_free_rate_at_entry, current_date_at_entry):
        option = OptionContract(option_type, strike_price, expiry_date, quantity, position, initial_ltp,
                                futures_price_at_entry, risk_free_rate_at_entry, current_date_at_entry)
        self.options.append(option)
        return option

    def remove_option(self, index):
        if 0 <= index < len(self.options):
            removed_option = self.options.pop(index)
            print(f"Removed Option: {removed_option.position.upper()} {removed_option.quantity} x {removed_option.strike_price} {removed_option.option_type.upper()}")
            return True
        else:
            print("Invalid index for removal.")
            return False

    def get_portfolio_pnl(self, current_futures_price, current_date, risk_free_rate):
        total_pnl = 0.0
        for option in self.options:
            current_volatility = option.initial_volatility

            pnl_per_contract = option.get_pnl_per_contract(
                current_futures_price=current_futures_price,
                current_date=current_date,
                risk_free_rate=risk_free_rate,
                volatility=current_volatility
            )
            total_pnl += pnl_per_contract * option.quantity
        return total_pnl

    def display_portfolio(self):
        if not self.options:
            print("\nPortfolio is empty.")
            return

        print("\nCurrent Portfolio:")
        for i, option in enumerate(self.options):
            print(f"{i}. {option.position.upper()} {option.quantity} x {option.strike_price:.2f} {option.option_type.upper()} "
                  f"Exp: {option.expiry_date.strftime('%Y-%m-%d')} (Initial LTP: {option.initial_ltp:.2f}, "
                  f"Calculated IV: {option.initial_volatility:.2%})")
