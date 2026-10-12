import time
import board
import busio
import requests
from adafruit_ina219 import INA219, ADCResolution

# --- Configuration ---
GRAFANA_URL = ""
STREAM_ID = "ina219"  # Target channel ID in Grafana Live
API_TOKEN = ""

# Target frequency setup
TARGET_FPS = 30
INTERVAL = 1.0 / TARGET_FPS

# --- Initialize Hardware ---
i2c = busio.I2C(board.SCL, board.SDA)
ina = INA219(i2c)

# Calibration
ina.set_calibration_32V_2A()

# 12BIT_1S takes ~532µs per conversion, allowing full ~60 Hz sampling speed.
ina.bus_adc_resolution = ADCResolution.ADCRES_12BIT_1S
ina.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_1S

url = f"{GRAFANA_URL}/api/live/push/{STREAM_ID}"
headers = {
    "Content-Type": "text/plain",
}
if API_TOKEN:
    headers["Authorization"] = f"Bearer {API_TOKEN}"

print(f"Streaming INA219 data to {url} at {TARGET_FPS}Hz...")

def main():
    session = requests.Session()
    session.headers.update(headers)

    next_frame_time = time.perf_counter()

    while True:
        try:
            # 1. Read sensor metrics
            voltage = ina.bus_voltage         # Voltage in volts (V)
            current = ina.current             # Current in milliamps (mA)
            power = ina.power                 # Power in watts (W)
            shunt_voltage = ina.shunt_voltage # Shunt voltage in millivolts (mV)

            # 2. Format as InfluxDB Line Protocol
            timestamp_ns = time.time_ns()
            payload = (
                f"power_monitoring,device=ina219 "
                f"bus_voltage={voltage:.4f},current_mA={current:.2f},"
                f"power_W={power:.4f},shunt_mV={shunt_voltage:.2f} "
                f"{timestamp_ns}"
            )

            # 3. Push to Grafana Live (silent on network timeouts/errors)
            try:
                response = session.post(url, data=payload, timeout=0.1)
                if response.status_code != 200:
                    print(f"Push error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException:
                # Silently ignore HTTP timeouts, connection resets, and dropped packets
                pass

        except Exception as e:
            # Only print actual hardware or unexpected runtime errors
            print(f"Sensor error: {e}")

        # 4. Precise timing loop
        next_frame_time += INTERVAL
        sleep_duration = next_frame_time - time.perf_counter()
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        else:
            next_frame_time = time.perf_counter()

if __name__ == "__main__":
    main()
