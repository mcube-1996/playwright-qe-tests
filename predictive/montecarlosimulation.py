import numpy as np
import matplotlib.pyplot as plt

# Parameters
n_trades = 2000       # Number of trades per simulation
n_simulations = 1000  # Number of simulation runs
start_balance = 1000  # Starting balance in dollars
win_rate = 0.625      # Probability of a winning trade
risk = 0.01           # Risk per trade (loss = 1% of account)
reward = 0.02         # Reward per trade (profit = 2% of account)

# Array to store final balances for each simulation run
final_balances = np.zeros(n_simulations)

for sim in range(n_simulations):
    balance = start_balance
    for _ in range(n_trades):
        if np.random.rand() < win_rate:
            balance *= (1 + reward)
        else:
            balance *= (1 - risk)
    final_balances[sim] = balance

mean_balance = np.mean(final_balances)
median_balance = np.median(final_balances)

print(f"After {n_trades} trades:")
print(f"Mean final balance: ${mean_balance:,.2f}")
print(f"Median final balance: ${median_balance:,.2f}")

# Plot the distribution of final balances
plt.figure(figsize=(10, 6))
plt.hist(final_balances, bins=50, edgecolor='black', alpha=0.7)
plt.title("Monte Carlo Simulation of 2,000 Trades")
plt.xlabel("Final Balance ($)")
plt.ylabel("Frequency")
plt.show()
