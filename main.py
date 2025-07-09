#Subhigya Priyansh
#23IE10040
#CDC 2k25

import numpy as np
from datetime import datetime, timedelta
from options_portfolio import OptionsPortfolio
from simulation_and_plot import _perform_simulations

def run_simulation():
    portfolio = OptionsPortfolio()

    print("--- Options Strategy Simulator ---")

    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    print(f"Current date fetched from system: {current_date.strftime('%Y-%m-%d')}")

    initial_futures_price = None
    while initial_futures_price is None:
        try:
            initial_futures_price = float(input("Enter initial Index/Stock Futures LTP: "))
        except ValueError:
            print("Invalid input. Please enter a numerical value for Futures LTP.")
        except EOFError:
            print("No input provided. Exiting.")
            return

    risk_free_rate = None
    while risk_free_rate is None:
        try:
            risk_free_rate = float(input("Enter annual risk-free rate (e.g. RBI T-bill rate): "))
        except ValueError:
            print("Invalid input. Please enter a numerical value for the risk-free rate.")
        except EOFError:
            print("No input provided. Exiting.")
            return

    while True:
        print("\n--- Portfolio Management ---")
        portfolio.display_portfolio()
        action = input("Enter action (add/remove/simulate/exit): ").lower()

        if action == 'add':
            try:
                option_type = input("Option Type (call/put): ").lower()
                strike_price = float(input("Strike Price: "))
                expiry_date_str = input("Expiry Date (YYYY-MM-DD): ")
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
                quantity = int(input("Quantity (e.g., 50 for 50 contracts): "))
                position = input("Position (long/short): ").lower()
                initial_ltp = float(input(f"Initial LTP for this {option_type.upper()} {strike_price} option: "))
                
                portfolio.add_option(option_type, strike_price, expiry_date, quantity, position, initial_ltp,
                                     initial_futures_price, risk_free_rate, current_date)
            except ValueError as e:
                print(f"Invalid input: {e}. Please try again.")
            except Exception as e:
                print(f"An error occurred: {e}. Please check your inputs.")

        elif action == 'remove':
            if not portfolio.options:
                print("No options to remove.")
                continue
            try:
                index_to_remove = int(input("Enter index of option to remove: "))
                portfolio.remove_option(index_to_remove)
            except ValueError:
                print("Invalid index. Please enter a number.")

        elif action == 'simulate':
            if not portfolio.options:
                print("Portfolio is empty. Add options before simulating.")
                continue
            _perform_simulations(portfolio, current_date, initial_futures_price, risk_free_rate)

        elif action == 'exit':
            print("Exiting program.")
            return

        else:
            print("Invalid action. Please choose 'add', 'remove', 'simulate', or 'exit'.")

if __name__ == "__main__":
    run_simulation()
