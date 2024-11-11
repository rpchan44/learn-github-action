# app.py
from flask import Flask, render_template_string
import mysql.connector

import os
import socket  # Import socket library to get the hostname

# Function to load configuration from a properties file (optional)
def load_config(config_file):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    return config

# Initialize Flask app
app = Flask(__name__)

# Load configuration from config.properties (optional)
config_path = os.getenv('CONFIG_FILE_PATH', '/app/config.properties')
config = load_config(config_path)
app_dbname =  config.get('app_dbname', 'app_dbname')
app_name = config.get('app_name', 'app_name')
app_title = config.get('app_title', 'app_title')

# MySQL configuration
app.config['MYSQL_HOST'] = '192.168.99.4'
app.config['MYSQL_USER'] = app_dbname
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'demo'

# Get the hostname of the container
hostname = socket.gethostname()

def get_db_connection():
        return mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )

@app.route('/')
def home():
    # Render a simple HTML page with the app name and hostname of the container
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM demo")
    data = cursor.fetchall()  # Get all rows
    cursor.close()
    connection.close()

    return render_template_string("""
        <html>
            <head><title>{{ app_title }}</title></head>
            <body>
                <center>
                   <h1><img src="https://getcomposer.org/img/logo-composer-transparent5.png"></img></h1>
	        {% for row in data %}
                   <p>{{ row.message }}</p>
                {% endfor %}
                   <p>{{ app_name }} served from {{ hostname }}</p>
                </center>
            </body>
        </html>
    """, app_dbname=app_dbname,app_name=app_name, app_title=app_title,hostname=hostname,data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

