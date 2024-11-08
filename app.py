# app.py
from flask import Flask, render_template_string
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
app_name = config.get('app_name', 'Default Flask App')

# Get the hostname of the container
hostname = socket.gethostname()

@app.route('/')
def home():
    # Render a simple HTML page with the app name and hostname of the container
    return render_template_string("""
        <html>
            <head><title>{{ app_name }}</title></head>
            <body>
                <h1>Welcome to {{ app_name }}</h1>
                <p>Hello world! served from {{ hostname }}</p>
            </body>
        </html>
    """, app_name=app_name, hostname=hostname)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

