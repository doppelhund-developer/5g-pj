import json
import random
import time
import uuid
from datetime import datetime
import requests

def generate_gps_data(device_id):
    """Generate random GPS data with auxiliary fields."""
    latitude = random.uniform(-90.0, 90.0)
    longitude = random.uniform(-180.0, 180.0)
    speed = round(random.uniform(0, 120), 2)  # km/h
    altitude = round(random.uniform(0, 10000), 2)  # meters
    accuracy = round(random.uniform(1, 50), 2)  # meters
    battery = round(random.uniform(0, 100), 2)  # percentage
    is_moving = random.choice([True, False])

    gps_data = {
        "device_id": device_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "accuracy": accuracy
        },
        "speed_kmh": speed,
        "is_moving": is_moving,
        "battery_level": battery
    }
    return gps_data

def send_gps_data(endpoint, data):
    """Send GPS data to the server via HTTPS POST."""
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(endpoint, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        print(f"[{datetime.utcnow().isoformat()}] Data sent successfully (Status {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.utcnow().isoformat()}] Failed to send data: {e}")

def main():
    device_id = str(uuid.uuid4())  # simulate a unique device ID
    interval = 5  # seconds between transmissions
    endpoint = "https://your-server.com/api/gps"  # Replace with your endpoint

    print(f"Starting GPS data simulation for device {device_id}...\n")

    try:
        while True:
            data = generate_gps_data(device_id)
            print(json.dumps(data, indent=2))  # Optional: local log
            send_gps_data(endpoint, data)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSimulation stopped.")

if __name__ == "__main__":
    main()
