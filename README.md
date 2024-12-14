# Access Verifier

The `AccessVerifier` microservice is used to verify if a given IP address is allowed based on data retrieved from AWS IP Ranges.

## Requirements

- Python 3.6 or newer
- pip (Python package installer)

## Installation

1. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Unix/Linux systems
   ```

2. **Install required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:

   To run the `AccessVerifier`, execute:

   ```bash
   python access_verifier.py
   ```

   Example output for a test run:

   ```bash
   python3 -m unittest test_access_verifier.py
   Testing IP: 3.4.12.4 - Status Code: 200 - Response: OK
   Testing IP: 3.5.140.0 - Status Code: 401 - Response: Unauthorized
   Testing IP: 15.190.244.0 - Status Code: 401 - Response: Unauthorized
   Testing IP: 15.230.15.29 - Status Code: 401 - Response: Unauthorized
   Testing IP: 15.230.15.76 - Status Code: 401 - Response: Unauthorized
   Testing IP: 15.230.221.0 - Status Code: 401 - Response: Unauthorized
   Testing IP: 35.180.0.0 - Status Code: 401 - Response: Unauthorized
   Testing IP: 192.168.1.1 - Status Code: 401 - Response: Unauthorized
   Testing IP: 127.0.0.1 - Status Code: 401 - Response: Unauthorized
   ```

4. **Testing**:

   To run the tests:

   ```bash
   python test_access_verifier.py
   ```

   Or, use `curl` to test the verification endpoint:

   ```bash
   curl -X POST http://localhost:5000/verify -H "X-Forwarded-For: <IP_ADDRESS>"
   ```

   Example:

   ```bash
   curl -X POST http://localhost:5000/verify -H "X-Forwarded-For: 3.4.12.4"
   ```
