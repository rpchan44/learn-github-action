from flask import Flask, render_template, request
import mysql.connector
import os
import logging
import socket  # Import socket library to get the hostname
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.mysql import MySQLInstrumentor
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from prometheus_client.exposition import basic_auth_handler
import time

app = Flask(__name__)
# Create metrics
REQUEST_COUNT = Counter(
    'webapp_requests_total', 'Total number of requests received', ['method', 'endpoint']
)

REQUEST_LATENCY = Histogram(
    'webapp_request_latency_seconds', 'Histogram of request latencies', ['method', 'endpoint']
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Track request count
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    
    # Track request latency
    duration = time.time() - request.start_time
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.endpoint).observe(duration)
    
    return response




# Function to load configuration from a properties file (optional)
def load_config(config_file):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    return config

FlaskInstrumentor().instrument_app(app)
MySQLInstrumentor().instrument()
tracer = trace.get_tracer(__name__)

# Set up logging configuration with timestamp, process id, and log level
logging.basicConfig(
    format='[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'  # Custom date format
)

# Load configuration from config.properties (optional)
config_path = os.getenv('CONFIG_FILE_PATH', '/app/config.properties')
config = load_config(config_path)
app_name = config.get('app_name', 'app_name')
app_title = config.get('app_title', 'app_title')

try:
    # Load the configuration from Vault
    vault_path = '/vault/secrets/dbcred'
    config = load_config(vault_path)

    # Get the database credentials
    db_host = config.get('DB_HOST')
    db_name = config.get('DB_NAME')
    db_user = config.get('DB_USERNAME')
    db_password = config.get('DB_PASSWORD')

    # Check if any value is missing
    if not all([db_host, db_name, db_user, db_password]):
        raise ValueError("One or more database configuration values are missing.")

    # MySQL configuration
    app.config['MYSQL_HOST'] = db_host
    app.config['MYSQL_USER'] = db_user
    app.config['MYSQL_PASSWORD'] = db_password
    app.config['MYSQL_DB'] = db_name

except KeyError:
    # Handle case where a key is missing from the config dictionary
    logging.info("Configuration error: Missing key(s)")
    # Optionally, log the error or raise an exception depending on your requirements
except Exception: 
    logging.info("Webapp is running locally not in k8s vault is not loaded!")
   

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
        app_dbname=db_name,
        app_name=app_name,
        app_title=app_title,
        hostname=hostname,
        data=data)

@app.route('/health')
def probe():
    return 'Ok', 200

@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

