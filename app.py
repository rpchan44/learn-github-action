# app.py
from flask import Flask, render_template
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
app_name = config.get('app_name', 'app_name')
app_title = config.get('app_title', 'app_title')

vault_path='/vault/secrets/db/dbcred'
config = load_config(vault_path)
db_host = config('DB_HOST','DB_HOST')
db_name = config('DB_NAME','DB_NAME')
db_user = config('DB_USERNAME','DB_USERNAME')
db_password = config('DB_PASSWORD','DB_PASSWORD')

# MySQL configuration
app.config['MYSQL_HOST'] = db_host
app.config['MYSQL_USER'] = db_user
app.config['MYSQL_PASSWORD'] = db_password
app.config['MYSQL_DB'] = db_name

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

    return render_template(
        'index.html',
        app_dbname=app_dbname,
        app_name=app_name,
        app_title=app_title,
        hostname=hostname,
        data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

