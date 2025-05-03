import json
import sqlite3
from pathlib import Path

def create_database():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('exchange_rates.db')
    cursor = conn.cursor()
    
    # Create table for exchange rates
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exchange_rates (
        currency_pair TEXT PRIMARY KEY,
        rate REAL NOT NULL
    )
    ''')
    
    return conn, cursor

def insert_exchange_rates(cursor, json_data):
    # Prepare the data for insertion
    data_to_insert = [(pair, rate) for pair, rate in json_data.items()]
    
    # Insert the data
    cursor.executemany('''
    INSERT OR REPLACE INTO exchange_rates (currency_pair, rate)
    VALUES (?, ?)
    ''', data_to_insert)

def main():
    # Get the path to the JSON file
    json_path = Path(__file__).parent / 'average_exchange_rates_2024.json'
    
    # Read the JSON file
    with open(json_path, 'r') as f:
        exchange_rates = json.load(f)
    
    # Create database and get connection objects
    conn, cursor = create_database()
    
    try:
        # Insert the data
        insert_exchange_rates(cursor, exchange_rates)
        
        # Commit the changes
        conn.commit()
        print("Successfully imported exchange rates into SQLite database!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    main() 