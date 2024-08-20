from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os
import dotenv

dotenv.load_dotenv()
password = os.getenv('PASSWORD')

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('calendar.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/calendars', methods=['GET'])
def get_calendars():
    conn = get_db_connection()
    calendars = conn.execute('SELECT * FROM calendars').fetchall()
    conn.close()
    return jsonify([dict(calendar) for calendar in calendars])

@app.route('/api/calendars', methods=['POST'])
def add_calendar():
    get_password = request.headers.get('auth')
    if get_password != password:
        return jsonify({'message': 'Invalid password'}), 401

    calendar_data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO calendars (name, color) VALUES (?, ?)',
                   (calendar_data['name'], calendar_data['color']))
    conn.commit()
    calendar_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': calendar_id, **calendar_data}), 201

@app.route('/api/calendars/<int:calendar_id>', methods=['DELETE'])
def delete_calendar(calendar_id):
    get_password = request.headers.get('auth')
    if get_password != password:
        return jsonify({'message': 'Invalid password'}), 401
    
    conn = get_db_connection()
    conn.execute('DELETE FROM calendars WHERE id = ?', (calendar_id,))
    conn.commit()
    conn.close()
    return '', 204

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    events = conn.execute('''
        SELECT events.*, calendars.color
        FROM events
        JOIN calendars ON events.calendar_id = calendars.id
    ''').fetchall()
    conn.close()
    return jsonify([dict(event) for event in events])

@app.route('/api/events', methods=['POST'])
def add_event():
    get_password = request.headers.get('auth')
    if get_password != password:
        return jsonify({'message': 'Invalid password'}), 401
    
    event_data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO events (title, start, end, calendar_id) VALUES (?, ?, ?, ?)',
                   (event_data['title'], event_data['start'], event_data['end'], event_data['calendar_id']))
    conn.commit()
    event_id = cursor.lastrowid
    
    # Fetch the color of the calendar
    calendar = conn.execute('SELECT color FROM calendars WHERE id = ?', (event_data['calendar_id'],)).fetchone()
    color = calendar['color'] if calendar else None
    
    conn.close()
    return jsonify({'id': event_id, 'color': color, **event_data}), 201

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    get_password = request.headers.get('auth')
    if get_password != password:
        return jsonify({'message': 'Invalid password'}), 401
    
    conn = get_db_connection()
    conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return '', 204

@app.route('/admin')
def admin_page():
    return render_template('admin/index.html')

@app.route('/admin/calender')
def admin_calender_page():
    return render_template('admin/calender.html')

@app.route('/admin/events')
def admin_events_page():
    return render_template('admin/events.html')

@app.route('/')
def calendar_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)