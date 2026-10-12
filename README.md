# INA219 Reporter

Streams voltage, current, and power readings from an INA219 sensor to a Grafana
Live stream.

## Requirements

- A Raspberry Pi or other supported Linux board with an INA219 sensor connected
  over I²C
- Python 3.11 or newer
- I²C enabled on the board

On Raspberry Pi OS, enable I²C using `sudo raspi-config` (Interface Options →
I2C), then reboot if prompted.

## Install

From the repository directory, create and activate a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```sh
python -m pip install -r requirements.txt
```

## Configure

Edit `config.toml`:

```toml
grafana_url = "https://your-grafana.example.com"
stream_id = "ina219"
api_token = ""
target_fps = 30
```

Set `grafana_url` to the Grafana base URL, `stream_id` to the target Grafana
Live stream, and `target_fps` to the desired sampling rate. Set `api_token` to
your Grafana API token when authentication is required.

## Run

With the virtual environment activated and the sensor connected, run:

```sh
python ina219-reporter.py
```

Stop the reporter with `Ctrl+C`.
