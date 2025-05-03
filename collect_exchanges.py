from currency_converter import CurrencyConverter
from datetime import date, timedelta
import json

# Initialize the currency converter
c = CurrencyConverter()

# Define the date range for 2024
start_date = date(2024, 1, 1)
end_date = date(2024, 12, 31)
delta = timedelta(days=1)

# Retrieve the list of available currencies
currencies = list(c.currencies)

# Dictionary to store average rates
average_rates = {}

# Iterate over all currency pairs
for base_currency in currencies:
    for target_currency in currencies:
        if base_currency == target_currency:
            continue  # Skip same currency pairs
        rates = []
        current_date = start_date
        while current_date <= end_date:
            try:
                rate = c.convert(1, base_currency, target_currency, date=current_date)
                rates.append(rate)
            except Exception:
                pass  # Skip dates with missing data
            current_date += delta
        if rates:
            average_rate = sum(rates) / len(rates)
            pair_key = f"{base_currency}_{target_currency}"
            average_rates[pair_key] = round(average_rate, 6)

# Save the average rates to a JSON file
output_filename = "average_exchange_rates_2024.json"
with open(output_filename, "w", encoding="utf-8") as json_file:
    json.dump(average_rates, json_file, indent=4, sort_keys=True, ensure_ascii=False)

print(f"Average exchange rates for 2024 have been saved to '{output_filename}'.")