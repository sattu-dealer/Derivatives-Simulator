#Only job is to plot the payoff of our portfolio on a particular day using matplotlib
#Curve is plotted as P/L on y-axis with price of Future in x-axis
#Curve is interpolation of sample points, more the points taken, the smoother the curve

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from options_portfolio import OptionsPortfolio

def _perform_simulations(portfolio: OptionsPortfolio, current_date: datetime, initial_futures_price: float, risk_free_rate: float):
    print("\n--- Running Simulation Scenarios ---")

    print("\nScenario: P&L vs. Futures Price for a Specific Date")
    simulation_target_date_str = input("Enter target date for P&L vs. Futures Price simulation (YYYY-MM-DD): ")
    try:
        simulation_target_date = datetime.strptime(simulation_target_date_str, '%Y-%m-%d')
        if simulation_target_date < current_date:
            print("Warning: Target date is in the past relative to initial current date. This means time to expiry will be negative for some options. P&L might be at intrinsic value.")
    except ValueError:
        print("Invalid date format. Using initial current date as target date for simulation.")
        simulation_target_date = current_date

    try:
        futures_price_range_start = float(input("Enter start of Futures Price range: "))
        futures_price_range_end = float(input("Enter end of Futures Price range: "))
        num_steps = int(input("Enter number of price steps (e.g., 200 for smooth curve): "))
    except ValueError:
        print("Invalid input. Using default range and steps for Futures Price simulation.")
        futures_price_range_start = initial_futures_price * 0.7
        futures_price_range_end = initial_futures_price * 1.3
        num_steps = 200

    extension_pct = 0.20
    
    full_futures_prices_for_analysis_start = futures_price_range_start * (1 - extension_pct)
    full_futures_prices_for_analysis_end = futures_price_range_end * (1 + extension_pct)
    
    if futures_price_range_start == futures_price_range_end:
        print("Warning: Start and end price range are identical. Expanding range slightly for analysis.")
        futures_price_range_start *= 0.9
        futures_price_range_end *= 1.1
        if futures_price_range_start == futures_price_range_end:
             futures_price_range_start = max(0.1, futures_price_range_start - 10)
             futures_price_range_end = futures_price_range_end + 10


    full_futures_prices_for_analysis = np.linspace(full_futures_prices_for_analysis_start,
                                                 full_futures_prices_for_analysis_end,
                                                 num_steps * 2)

    pnl_values_full_range = []
    for f_price in full_futures_prices_for_analysis:
        pnl = portfolio.get_portfolio_pnl(f_price, simulation_target_date, risk_free_rate)
        pnl_values_full_range.append(pnl)

    pnl_values_full_range_np = np.array(pnl_values_full_range)

    risk_category = "Limited Loss (Hedged)"
    MONOTONIC_CHECK_THRESHOLD = 0.01
    
    if pnl_values_full_range_np.size > 1:
        idx_start = np.searchsorted(full_futures_prices_for_analysis, futures_price_range_start, side='left')
        idx_end = np.searchsorted(full_futures_prices_for_analysis, futures_price_range_end, side='right') - 1

        is_unlimited_downside_risk = False
        is_unlimited_upside_risk = False

        check_segment_low_end_idx = idx_start
        check_segment_low_start_idx = max(0, check_segment_low_end_idx - int(num_steps * extension_pct))
        check_segment_low_pnl = pnl_values_full_range_np[check_segment_low_start_idx : check_segment_low_end_idx]

        if check_segment_low_pnl.size >= 2:
            if check_segment_low_pnl[0] - check_segment_low_pnl[-1] > MONOTONIC_CHECK_THRESHOLD * len(check_segment_low_pnl):
                 is_unlimited_downside_risk = True

        check_segment_high_start_idx = idx_end + 1
        check_segment_high_end_idx = min(pnl_values_full_range_np.size, check_segment_high_start_idx + int(num_steps * extension_pct))
        check_segment_high_pnl = pnl_values_full_range_np[check_segment_high_start_idx : check_segment_high_end_idx]

        if check_segment_high_pnl.size >= 2:
            if check_segment_high_pnl[0] - check_segment_high_pnl[-1] > MONOTONIC_CHECK_THRESHOLD * len(check_segment_high_pnl):
                is_unlimited_upside_risk = True

        if is_unlimited_downside_risk and is_unlimited_upside_risk:
            risk_category = "Potential Unlimited Loss (Both Sides - Unhedged)"
        elif is_unlimited_downside_risk:
            risk_category = "Potential Unlimited Loss (Downside Risk - Unhedged)"
        elif is_unlimited_upside_risk:
            risk_category = "Potential Unlimited Loss (Upside Risk - Unhedged)"
        else:
            risk_category = "Limited Loss (Hedged)"

        max_profit = np.max(pnl_values_full_range_np)
        max_loss = np.min(pnl_values_full_range_np)

        print(f"\nMaximum Possible Profit over analysis range: {max_profit:.2f}")
        print(f"Maximum Possible Loss over analysis range: {max_loss:.2f}")
        print(f"Position Category: {risk_category}")

    else:
        max_profit = 0
        max_loss = 0
        print("\nNo P&L data to calculate max profit/loss.")


    pnl_values_for_plot = pnl_values_full_range_np[idx_start:idx_end+1]
    futures_prices_for_plot_filtered = full_futures_prices_for_analysis[idx_start:idx_end+1]


    plt.figure(figsize=(10, 6))
    plt.plot(futures_prices_for_plot_filtered, pnl_values_for_plot, label='Portfolio P&L', linestyle='-')
    plt.axhline(0, color='grey', linestyle='--', linewidth=0.8)
    plt.axvline(initial_futures_price, color='red', linestyle=':', label='Initial Futures Price')

    if pnl_values_for_plot.size > 0:
        plt.axhline(max_profit, color='green', linestyle=':', linewidth=0.8, label=f'Max Profit: {max_profit:.2f}')
        plt.axhline(max_loss, color='red', linestyle=':', linewidth=0.8, label=f'Max Loss: {max_loss:.2f}')

    plt.title(f'Portfolio P&L vs. Futures Price (as of {simulation_target_date.strftime("%Y-%m-%d")})')
    plt.xlabel('Futures Price')
    plt.ylabel('Profit / Loss')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.show()
