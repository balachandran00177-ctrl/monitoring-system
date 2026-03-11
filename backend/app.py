from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import sqlite3
import json
import os
import random
otp_storage = {}
from ai_predictor import EnergyPredictor
from anomaly_detector import AnomalyDetector

app = Flask(
    __name__,
    template_folder='../frontend',
    static_folder='../frontend',
    static_url_path=''
)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yourgmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_gmail_app_password'
mail = Mail(app)
CORS(app)

# Initialize AI models
predictor = EnergyPredictor()
anomaly_detector = AnomalyDetector()

# Database connection
def get_db():
    import sqlite3, os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "energy.db")
    return sqlite3.connect(db_path)

# Initialize database
def init_db():
    db = get_db()
    cursor = db.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Energy consumption table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS energy_consumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            consumption_kwh REAL NOT NULL,
            cost REAL NOT NULL,
            device_name TEXT,
            location TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prediction_date DATE NOT NULL,
            predicted_consumption REAL NOT NULL,
            confidence_score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    db.commit()
    db.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# API Endpoints



# User Registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    otp = data.get('otp')
    
    if otp_storage.get(email) != otp:
        return jsonify({"success": False, "message": "Invalid OTP"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      (username, email, password))
        db.commit()
        return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    finally:
        db.close()
        
# Send OTP
@app.route('/api/send-otp', methods=['POST'])
def send_otp():

    data = request.json
    email = data.get('email')

    otp = str(random.randint(100000,999999))

    otp_storage[email] = otp

    msg = Message(
        "Energy Monitoring OTP",
        sender="yourgmail@gmail.com",
        recipients=[email]
    )

    msg.body = f"Your OTP is: {otp}"

    mail.send(msg)

    return jsonify({
        "success": True,
        "message": "OTP sent to your email"
    })

# User Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    db.close()

    if user:
        return jsonify({
            'success': True,
            'user_id': user['id'],
            'username': user['username'],
            'email': user['email']
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Add Energy Consumption
@app.route('/api/consumption/add', methods=['POST'])
def add_consumption():
    data = request.json
    user_id = data.get('user_id')
    consumption_kwh = data.get('consumption_kwh')
    rate = 8
    cost = float(consumption_kwh) * rate
    device_name = data.get('device_name', 'Unknown')
    location = data.get('location', 'Home')

    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        INSERT INTO energy_consumption (user_id, consumption_kwh, cost, device_name, location)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, consumption_kwh, cost, device_name, location))

    db.commit()
    consumption_id = cursor.lastrowid

    # Check for anomalies using AI
    cursor.execute('''
        SELECT consumption_kwh FROM energy_consumption
        WHERE user_id = ?
        ORDER BY timestamp DESC LIMIT 30
    ''', (user_id,))

    historical_data = [row['consumption_kwh'] for row in cursor.fetchall()]

    if len(historical_data) > 10:
        is_anomaly = anomaly_detector.detect(historical_data, consumption_kwh)

        if is_anomaly:
            cursor.execute('''
                INSERT INTO alerts (user_id, alert_type, message, severity)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 'anomaly',
                  f'Unusual consumption detected: {consumption_kwh} kWh is significantly higher than your average.',
                  'high'))
            db.commit()

    db.close()

    return jsonify({
        'success': True,
        'consumption_id': consumption_id,
        'message': 'Consumption data added successfully'
    }), 201

# Get Consumption Data
@app.route('/api/consumption/<int:user_id>', methods=['GET'])
def get_consumption(user_id):
    period = request.args.get('period', 'week')  # week, month, year

    db = get_db()
    cursor = db.cursor()

    if period == 'week':
        days = 7
    elif period == 'month':
        days = 30
    else:
        days = 365

    cursor.execute('''
        SELECT * FROM energy_consumption
        WHERE user_id = ? AND timestamp >= datetime('now', '-' || ? || ' days')
        ORDER BY timestamp DESC
    ''', (user_id, days))

    data = [dict(row) for row in cursor.fetchall()]
    db.close()

    return jsonify({'success': True, 'data': data}), 200

 # Delete energy reading
@app.route('/api/consumption/delete/<int:reading_id>', methods=['DELETE'])
def delete_reading(reading_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM energy_consumption WHERE id = ?",
        (reading_id,)
    )

    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "message": "Reading deleted successfully"
    })

# Get Statistics
@app.route('/api/stats/<int:user_id>', methods=['GET'])
def get_stats(user_id):
    db = get_db()
    cursor = db.cursor()

    # Total consumption
    cursor.execute('''
        SELECT SUM(consumption_kwh) as total_consumption, SUM(cost) as total_cost
        FROM energy_consumption WHERE user_id = ?
    ''', (user_id,))
    totals = cursor.fetchone()

    # Today's consumption
    cursor.execute('''
        SELECT SUM(consumption_kwh) as today_consumption, SUM(cost) as today_cost
        FROM energy_consumption
        WHERE user_id = ? AND DATE(timestamp) = DATE('now')
    ''', (user_id,))
    today = cursor.fetchone()
    

    # This month's consumption
    cursor.execute('''
        SELECT SUM(consumption_kwh) as month_consumption, SUM(cost) as month_cost
        FROM energy_consumption
        WHERE user_id = ? AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
    ''', (user_id,))
    month = cursor.fetchone()

    # Average daily consumption
    cursor.execute('''
        SELECT AVG(daily_consumption) as avg_daily
        FROM (
            SELECT DATE(timestamp) as date, SUM(consumption_kwh) as daily_consumption
            FROM energy_consumption
            WHERE user_id = ?
            GROUP BY DATE(timestamp)
        )
    ''', (user_id,))
    avg = cursor.fetchone()

    db.close()

    return jsonify({
        'success': True,
        'stats': {
            'total_consumption': totals['total_consumption'] or 0,
            'total_cost': totals['total_cost'] or 0,
            'today_consumption': today['today_consumption'] or 0,
            'today_cost': today['today_cost'] or 0,
            'month_consumption': month['month_consumption'] or 0,
            'month_cost': month['month_cost'] or 0,
            'avg_daily_consumption': avg['avg_daily'] or 0
        }
    }), 200

# AI Prediction Endpoint
@app.route('/api/predict/<int:user_id>', methods=['GET'])
def predict_consumption(user_id):
    days = int(request.args.get('days', 7))

    db = get_db()
    cursor = db.cursor()

    # Get historical data
    cursor.execute('''
        SELECT DATE(timestamp) as date, SUM(consumption_kwh) as daily_consumption
        FROM energy_consumption
        WHERE user_id = ?
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        LIMIT 30
    ''', (user_id,))

    historical_data = [row['daily_consumption'] for row in cursor.fetchall()]

    if len(historical_data) < 7:
        db.close()
        return jsonify({
            'success': False,
            'message': 'Not enough historical data for prediction'
        }), 400

    # Generate predictions
    predictions = predictor.predict(historical_data, days)

    # Store predictions
    for i, pred in enumerate(predictions):
        prediction_date = (datetime.now() + timedelta(days=i+1)).date()
        cursor.execute('''
            INSERT INTO predictions (user_id, prediction_date, predicted_consumption, confidence_score)
            VALUES (?, ?, ?, ?)
        ''', (user_id, prediction_date, pred['value'], pred['confidence']))

    db.commit()
    db.close()

    return jsonify({
        'success': True,
        'predictions': predictions
    }), 200

# Get Alerts
@app.route('/api/alerts/<int:user_id>', methods=['GET'])
def get_alerts(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT * FROM alerts
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 20
    ''', (user_id,))

    alerts = [dict(row) for row in cursor.fetchall()]
    db.close()

    return jsonify({'success': True, 'alerts': alerts}), 200

# Mark alert as read
@app.route('/api/alerts/<int:alert_id>/read', methods=['PUT'])
def mark_alert_read(alert_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('UPDATE alerts SET is_read = 1 WHERE id = ?', (alert_id,))
    db.commit()
    db.close()

    return jsonify({'success': True}), 200

# AI Recommendations
@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    db = get_db()
    cursor = db.cursor()

    # Get consumption patterns
    cursor.execute('''
        SELECT AVG(consumption_kwh) as avg_consumption,
               MAX(consumption_kwh) as max_consumption,
               MIN(consumption_kwh) as min_consumption
        FROM energy_consumption
        WHERE user_id = ?
    ''', (user_id,))

    stats = cursor.fetchone()
    db.close()

    recommendations = []

    avg_consumption = stats['avg_consumption'] or 0

    if avg_consumption > 50:
        recommendations.append({
            'type': 'high_usage',
            'title': 'High Energy Consumption Detected',
            'message': 'Your average consumption is above normal. Consider using energy-efficient appliances.',
            'savings_potential': '15-20%'
        })

    recommendations.append({
        'type': 'peak_hours',
        'title': 'Avoid Peak Hours',
        'message': 'Use heavy appliances during off-peak hours (10 PM - 6 AM) to save costs.',
        'savings_potential': '10-15%'
    })

    recommendations.append({
        'type': 'monitoring',
        'title': 'Regular Monitoring',
        'message': 'Check your dashboard daily to identify unusual consumption patterns early.',
        'savings_potential': '5-10%'
    })

    return jsonify({'success': True, 'recommendations': recommendations}), 200

# Export data
@app.route('/api/export/<int:user_id>', methods=['GET'])
def export_data(user_id):
    format_type = request.args.get('format', 'json')

    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT * FROM energy_consumption
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (user_id,))

    data = [dict(row) for row in cursor.fetchall()]
    db.close()

    if format_type == 'json':
        return jsonify({'success': True, 'data': data}), 200
    elif format_type == 'csv':
        # Convert to CSV format
        csv_data = "ID,User ID,Timestamp,Consumption (kWh),Cost (INR ₹),Device,Location\n"
        for row in data:
            csv_data += f"{row['id']},{row['user_id']},{row['timestamp']},{row['consumption_kwh']},{row['cost']},{row['device_name']},{row['location']}\n"

        return csv_data, 200, {'Content-Type': 'text/csv',
                                'Content-Disposition': 'attachment; filename=energy_data.csv'}

if __name__ == '__main__':
    init_db()
    
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)