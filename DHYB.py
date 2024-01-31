from bleak import BleakScanner
import asyncio
import numpy as np
from tqdm import tqdm
import argparse
from PolarH10 import PolarH10
from BreathingAnalyser import BreathingAnalyser

import random
import time

from paho.mqtt import client as mqtt_client

""" DHYB.py
Scan and connect to Polar H10 device
Retrieve basic sensor information including battery level and serial number
- Stream accelerometer data simultaneously with heart rate data
- Alternatively read sample data from a file
"""

async def main():
    
    devices = await BleakScanner.discover()
    polar_device_found = False
    
    broker = 'localhost'
    port = 1883
    client_id = f'publish-{random.randint(0, 1000)}'

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            return True
        else:
            print("Failed to connect, return code %d\n", rc)
            return False

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    
    client_mqtt = client
    client_mqtt.loop_start()

    for device in devices:
        if device.name is not None and "Polar" in device.name:
            polar_device_found = True
            polar_device = PolarH10(device, client_mqtt)
            await polar_device.connect()
            await polar_device.get_device_info()
            await polar_device.print_device_info()

            await polar_device.start_hr_stream()
            while True:
                await asyncio.sleep(1)
            # await polar_device.stop_acc_stream()
            # await polar_device.stop_hr_stream()

            # await polar_device.disconnect()
    
    if not polar_device_found:
        print("No Polar device found")

def get_arguments():
    parser = argparse.ArgumentParser(description="Polar H10 Heart Rate Variability and Breathing Rate Monitor")
    # parser.add_argument("--record-len", type=int, default=20, help="Length of recording in seconds")
    return parser.parse_args()

if __name__ == "__main__":

    args = get_arguments()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    acc_data, ibi_data = loop.run_until_complete(main())
