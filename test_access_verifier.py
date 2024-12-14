import requests

# Adres URL mikroserwisu AccessVerifier
access_verifier_url = 'http://localhost:5000/verify' 

# Lista testowych adresów IP
test_ips = [
    "3.4.12.4",      # Dozwolony (eu-west-1)
    "3.5.140.0",     # Niedozwolony (ap-northeast-2)
    "15.190.244.0",  # Niedozwolony (ap-east-2)
    "15.230.15.29",  # Niedozwolony (eu-central-1)
    "15.230.15.76",  # Niedozwolony (eu-central-1)
    "15.230.221.0",  # Niedozwolony (us-east-1)
    "35.180.0.0",    # Niedozwolony (brak regionu eu-west-1)
    "192.168.1.1",    # Niedozwolony (lokalny)
    "127.0.0.1"      #  Niedozwolony (lokalny)
]

# Funkcja do testowania adresów IP
def test_ip(ip):
    # Wysyłanie żądania POST z nagłówkiem X-Forwarded-For
    response = requests.post(access_verifier_url, headers={'X-Forwarded-For': ip})
    print(f"Testing IP: {ip} - Status Code: {response.status_code} - Response: {response.text}")

# Testowanie wszystkich adresów IP
for ip in test_ips:
    test_ip(ip)
