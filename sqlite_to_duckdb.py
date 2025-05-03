import sqlite3
import duckdb
from pathlib import Path

def convert_to_duckdb():
    # Paths to the databases
    sqlite_path = Path(__file__).parent / 'exchange_rates.db'
    duckdb_path = Path(__file__).parent / 'exchange_rates.duckdb'
    
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to DuckDB (creates it if it doesn't exist)
    duckdb_conn = duckdb.connect(str(duckdb_path))
    
    try:
        # Create table in DuckDB
        duckdb_conn.execute('''
        CREATE TABLE IF NOT EXISTS exchange_rates (
            currency_pair TEXT,
            rate DOUBLE
        )
        ''')
        
        # Read all data from SQLite
        sqlite_cursor.execute('SELECT * FROM exchange_rates')
        rows = sqlite_cursor.fetchall()
        
        # Insert data into DuckDB
        for row in rows:
            duckdb_conn.execute(
                'INSERT INTO exchange_rates (currency_pair, rate) VALUES (?, ?)',
                row
            )
        
        print(f"Successfully converted SQLite database to DuckDB at {duckdb_path}")
        
        # Verify the data
        result = duckdb_conn.execute('SELECT COUNT(*) FROM exchange_rates').fetchone()
        print(f"Total records in DuckDB: {result[0]}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close connections
        sqlite_conn.close()
        duckdb_conn.close()

if __name__ == "__main__":
    convert_to_duckdb() 