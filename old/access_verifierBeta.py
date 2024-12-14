from flask import Flask, request, Response
import requests
import time
import threading

app = Flask(__name__)

allowed_ips = set()

def update_allowed_ips():
    global allowed_ips
    while True:

        allowed_ips = {"127.0.0.2", "192.168.1.2"}  
        print("Zaktualizowano dozwolone adresy IP:", allowed_ips)
        time.sleep(86400)

@app.route('/verify', methods=['POST'])
def verify_access():

    headers = request.headers
    client_ip = request.remote_addr

    if client_ip in allowed_ips:
        return Response("OK", status=200)
    else:
        return Response("Unauthorized", status=401)

if __name__ == '__main__':
    threading.Thread(target=update_allowed_ips, daemon=True).start()

    app.run(host='0.0.0.0', port=5000)