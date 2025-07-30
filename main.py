import time
import json
import network
import socket
import rpc
import pyb

# === Setup WiFi Interface ===
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# === Setup RPC Interface to ESP32 ===
interface = rpc.rpc_usb_vcp_slave()  # or rpc_uart_slave() if using UART

# === Globals ===
ssid = None
password = None

def connect_to_wifi(ssid, password):
    print("Connecting to WiFi:", ssid)
    wlan.connect(ssid, password)

    for _ in range(20):
        if wlan.isconnected():
            print("Connected:", wlan.ifconfig())
            return True
        time.sleep(0.5)

    print("Failed to connect.")
    return False

def ble_event_loop():
    print("BLE ready. Waiting for WiFi credentials...")
    while True:
        try:
            # Wait for BLE message
            msg = interface.recv()
            if msg:
                print("Received via BLE:", msg)

                # Parse and decode WiFi credentials
                try:
                    data = json.loads(msg)
                    ssid = data.get("ssid")
                    password = data.get("password")
                    if ssid and password:
                        print("SSID:", ssid)
                        print("Password:", "*" * len(password))
                        if connect_to_wifi(ssid, password):
                            interface.send("WiFi connected")
                        else:
                            interface.send("WiFi failed")
                    else:
                        interface.send("Invalid format. Send JSON with 'ssid' and 'password'")
                except Exception as e:
                    print("JSON Parse Error:", str(e))
                    interface.send("Invalid JSON")
        except Exception as e:
            print("RPC Error:", str(e))
            time.sleep(1)

# === Start BLE Advertising on ESP32 ===
def start_ble_on_esp32():
    try:
        interface.call("start_ble_service")  # This expects a corresponding RPC function on the ESP32
        print("Requested ESP32 to start BLE service.")
    except Exception as e:
        print("Failed to start BLE on ESP32:", str(e))

# === Main ===
def main():
    start_ble_on_esp32()
    ble_event_loop()

main()
