from flask import Flask, render_template, request, jsonify
from sqlmodel import SQLModel, Session, create_engine, select, Field
from typing import Optional
from pathlib import Path

app = Flask(__name__)

# SQLModel models
class Currency(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str

class ExchangeRate(SQLModel, table=True):
    currency_pair: str = Field(primary_key=True)
    rate: float

# Database setup
db_path = Path(__file__).parent / 'exchange_rates_v2.db'
engine = create_engine(f"sqlite:///{db_path}")

def get_currencies():
    """Get list of currencies with their names from the database"""
    with Session(engine) as session:
        statement = select(Currency)
        currencies = session.exec(statement).all()
        return sorted(currencies, key=lambda x: x.code)

def calculate_exchange_rate(from_currency: str, to_currency: str, amount: float) -> Optional[float]:
    """Calculate exchange rate between two currencies"""
    with Session(engine) as session:
        # Try direct conversion first
        statement = select(ExchangeRate).where(ExchangeRate.currency_pair == f"{from_currency}_{to_currency}")
        result = session.exec(statement).first()
        
        if result:
            return amount * result.rate
        
        # Try reverse conversion
        statement = select(ExchangeRate).where(ExchangeRate.currency_pair == f"{to_currency}_{from_currency}")
        result = session.exec(statement).first()
        if result:
            return amount / result.rate
        
        # Try conversion through USD
        from_usd = session.exec(
            select(ExchangeRate).where(ExchangeRate.currency_pair == f"{from_currency}_USD")
        ).first()
        to_usd = session.exec(
            select(ExchangeRate).where(ExchangeRate.currency_pair == f"{to_currency}_USD")
        ).first()
        
        if from_usd and to_usd:
            return amount * (to_usd.rate / from_usd.rate)
        
        return None

@app.route('/')
def index():
    currencies = get_currencies()
    return render_template('index.html', currencies=currencies)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')
    amount = float(data.get('amount', 1))
    
    result = calculate_exchange_rate(from_currency, to_currency, amount)
    
    if result is None:
        return jsonify({'error': 'Exchange rate not available'}), 400
    
    return jsonify({
        'from_currency': from_currency,
        'to_currency': to_currency,
        'amount': amount,
        'result': round(result, 4)
    })

if __name__ == '__main__':
    # Create tables if they don't exist
    SQLModel.metadata.create_all(engine)
    app.run(debug=True) 