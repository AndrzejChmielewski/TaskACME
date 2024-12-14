import os
import json
import requests
from flask import Flask, request, Response
from datetime import datetime, timedelta
from ipaddress import ip_network, ip_address
import logging

# Tworzenie katalogu na logi, jeśli nie istnieje
if not os.path.exists('logs'):
    os.makedirs('logs')

log_filename = f'logs/access_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, filename=log_filename, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

allowed_ips = []
last_updated = datetime.min

def fetch_aws_ip_ranges():
    global allowed_ips, last_updated
    if datetime.now() - last_updated < timedelta(days=1):
        return allowed_ips

    try:
        aws_ip_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        response = requests.get(aws_ip_url)
        response.raise_for_status()  # Sprawdza, czy odpowiedź jest błędem
        ip_ranges = response.json()
        allowed_ips = []
        for prefix in ip_ranges['prefixes']:
            if prefix['region'] == 'eu-west-1':  
                allowed_ips.append(ip_network(prefix['ip_prefix']))
        
        last_updated = datetime.now()
        logging.info("AWS IP ranges fetched successfully.")
        return allowed_ips
    except requests.RequestException as e:
        logging.error(f"Error fetching AWS IP ranges: {e}")
        return allowed_ips  # Zwraca poprzednie dozwolone IP, jeśli wystąpił błąd 
    
# Funkcja sprawdzająca, czy IP jest dozwolone
def is_ip_allowed(ip):
    allowed_ranges = fetch_aws_ip_ranges()
    
    # Sprawdzanie lokalnego IP
    if ip == ip_address('127.0.0.1'):
        return True
    
    for network in allowed_ranges:
        if ip in network:
            return True
    return False

@app.route('/verify', methods=['POST'])
def verify_request():
    # Odczytanie adresu IP z nagłówka X-Forwarded-For
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Logowanie nagłówków żądania
    logging.info(f"Received request from IP: {client_ip}")
    logging.info(f"Request headers: {request.headers}")

    if is_ip_allowed(ip_address(client_ip)):
        logging.info(f"IP {client_ip} is allowed.")
        return Response("OK", status=200)
    else:
        logging.warning(f"IP {client_ip} is not authorized.")
        return Response("Unauthorized", status=401)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)