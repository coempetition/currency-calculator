from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)

def get_currencies():
    """Get list of unique currencies from the database"""
    db_path = Path(__file__).parent / 'exchange_rates.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all currency pairs and extract unique currencies
    cursor.execute('SELECT currency_pair FROM exchange_rates')
    pairs = cursor.fetchall()
    currencies = set()
    for pair in pairs:
        currencies.update(pair[0].split('_'))
    
    conn.close()
    return sorted(list(currencies))

def calculate_exchange_rate(from_currency, to_currency, amount):
    """Calculate exchange rate between two currencies"""
    db_path = Path(__file__).parent / 'exchange_rates.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try direct conversion first
    cursor.execute(
        'SELECT rate FROM exchange_rates WHERE currency_pair = ?',
        (f"{from_currency}_{to_currency}",)
    )
    result = cursor.fetchone()
    
    if result:
        rate = result[0]
    else:
        # Try reverse conversion
        cursor.execute(
            'SELECT rate FROM exchange_rates WHERE currency_pair = ?',
            (f"{to_currency}_{from_currency}",)
        )
        result = cursor.fetchone()
        if result:
            rate = 1 / result[0]
        else:
            # Try conversion through USD (most common base currency)
            cursor.execute(
                'SELECT rate FROM exchange_rates WHERE currency_pair = ?',
                (f"{from_currency}_USD",)
            )
            from_usd = cursor.fetchone()
            cursor.execute(
                'SELECT rate FROM exchange_rates WHERE currency_pair = ?',
                (f"{to_currency}_USD",)
            )
            to_usd = cursor.fetchone()
            
            if from_usd and to_usd:
                rate = to_usd[0] / from_usd[0]
            else:
                return None
    
    conn.close()
    return amount * rate

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
    app.run(debug=True) 