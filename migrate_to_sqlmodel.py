import sqlite3
from sqlmodel import SQLModel, Session, create_engine, select
from pathlib import Path
from app_v2 import ExchangeRate

def migrate_data():
    # Paths
    old_db_path = Path(__file__).parent / 'exchange_rates.db'
    new_db_path = Path(__file__).parent / 'exchange_rates_v2.db'
    
    # Create new engine
    engine = create_engine(f"sqlite:///{new_db_path}")
    
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    # Connect to old database
    old_conn = sqlite3.connect(old_db_path)
    old_cursor = old_conn.cursor()
    
    # Get all data from old database
    old_cursor.execute('SELECT * FROM exchange_rates')
    rows = old_cursor.fetchall()
    
    # Insert data into new database
    with Session(engine) as session:
        for row in rows:
            currency_pair, rate = row
            # Check if the record already exists
            existing = session.exec(
                select(ExchangeRate).where(ExchangeRate.currency_pair == currency_pair)
            ).first()
            
            if existing:
                # Delete existing record
                session.delete(existing)
                session.commit()
            
            # Create new record
            exchange_rate = ExchangeRate(currency_pair=currency_pair, rate=rate)
            session.add(exchange_rate)
            session.commit()
    
    # Close old connection
    old_conn.close()
    
    print(f"Successfully migrated data to {new_db_path}")

if __name__ == '__main__':
    migrate_data() 