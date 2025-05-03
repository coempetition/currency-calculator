from sqlmodel import SQLModel, Session, create_engine, select
from pathlib import Path
from app_v2 import Currency

# Currency data from ISO 4217
CURRENCY_DATA = {
    "AUD": "Australian Dollar",
    "BGN": "Bulgarian Lev",
    "BRL": "Brazilian Real",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",
    "CZK": "Czech Koruna",
    "DKK": "Danish Krone",
    "EUR": "Euro",
    "GBP": "British Pound",
    "HKD": "Hong Kong Dollar",
    "HUF": "Hungarian Forint",
    "IDR": "Indonesian Rupiah",
    "ILS": "Israeli New Shekel",
    "INR": "Indian Rupee",
    "ISK": "Icelandic Króna",
    "JPY": "Japanese Yen",
    "KRW": "South Korean Won",
    "MXN": "Mexican Peso",
    "MYR": "Malaysian Ringgit",
    "NOK": "Norwegian Krone",
    "NZD": "New Zealand Dollar",
    "PHP": "Philippine Peso",
    "PLN": "Polish Złoty",
    "RON": "Romanian Leu",
    "SEK": "Swedish Krona",
    "SGD": "Singapore Dollar",
    "THB": "Thai Baht",
    "TRY": "Turkish Lira",
    "USD": "US Dollar",
    "ZAR": "South African Rand"
}

def populate_currencies():
    # Database setup
    db_path = Path(__file__).parent / 'exchange_rates_v2.db'
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Create tables if they don't exist
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Check if currencies already exist
        existing_currencies = session.exec(select(Currency)).all()
        existing_codes = {c.code for c in existing_currencies}
        
        # Add new currencies
        for code, name in CURRENCY_DATA.items():
            if code not in existing_codes:
                currency = Currency(code=code, name=name)
                session.add(currency)
        
        session.commit()
        print("Currency data populated successfully!")

if __name__ == '__main__':
    populate_currencies() 