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

# Ustalamy nazwę pliku logu z aktualną datą i godziną
log_filename = f'logs/access_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, filename=log_filename, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Lista dozwolonych adresów IP oraz zmienna do śledzenia ostatniej aktualizacji
allowed_ips = []
last_updated = datetime.min

def fetch_aws_ip_ranges():
    global allowed_ips, last_updated
    # Sprawdzamy, czy ostatnia aktualizacja miała miejsce mniej niż 24 godziny temu
    if datetime.now() - last_updated < timedelta(days=1):
        return allowed_ips  # Zwracamy już pobrane adresy, jeśli są aktualne

    try:
        # Pobieramy dane o adresach IP z AWS
        aws_ip_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        response = requests.get(aws_ip_url)
        response.raise_for_status()  # Sprawdzamy, czy odpowiedź jest błędem
        ip_ranges = response.json()
        allowed_ips = []
        # Przechodzimy przez wszystkie prefiksy i dodajemy te z regionu 'eu-west-1'
        for prefix in ip_ranges['prefixes']:
            if prefix['region'] == 'eu-west-1':  
                allowed_ips.append(ip_network(prefix['ip_prefix']))
        
        last_updated = datetime.now()  # Aktualizujemy czas ostatniej aktualizacji
        logging.info("AWS IP ranges fetched successfully.")  # Logujemy sukces
        return allowed_ips
    except requests.RequestException as e:
        logging.error(f"Error fetching AWS IP ranges: {e}")  # Logujemy błąd, jeśli coś poszło nie tak
        return allowed_ips  # Zwracamy poprzednie dozwolone IP, jeśli wystąpił błąd 
    
# Funkcja sprawdzająca, czy dany adres IP jest dozwolony
def is_ip_allowed(ip):
    allowed_ranges = fetch_aws_ip_ranges()  # Pobieramy dozwolone adresy IP

    # Sprawdzamy, czy IP znajduje się w dozwolonych zakresach
    for network in allowed_ranges:
        if ip in network:
            return True
    return False  # IP nie jest dozwolone

@app.route('/verify', methods=['POST'])
def verify_request():
    # Odczytanie adresu IP z nagłówka X-Forwarded-For
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Logowanie nagłówków żądania
    logging.info(f"Received request from IP: {client_ip}")
    logging.info(f"Request headers: {request.headers}")

    # Sprawdzamy, czy IP jest dozwolone
    if is_ip_allowed(ip_address(client_ip)):
        logging.info(f"IP {client_ip} is allowed.")  # Logujemy, że IP jest dozwolone
        response_message = "OK\n" + str(request.headers)  # Dodajemy nagłówki do odpowiedzi
        return Response(response_message, status=200, mimetype='text/plain')  # Zwracamy odpowiedź 200 OK z nagłówkami
    else:
        logging.warning(f"IP {client_ip} is not authorized.")  # Logujemy, że IP nie jest autoryzowane
        response_message = "Unauthorized \n" + str(request.headers)  # Dodajemy nagłówki do odpowiedzi
        return Response(response_message, status=401, mimetype='text/plain')  # Zwracamy odpowiedź 401 Unauthorized z nagłówkami

# Uruchamiamy aplikację
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
