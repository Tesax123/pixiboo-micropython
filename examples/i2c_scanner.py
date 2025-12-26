"""
I2C Scanner for Pixiboo

Scans the I2C bus to find connected devices.
Helps debug accelerometer connection issues.
"""

from machine import Pin, I2C
import time

def scan_i2c():
    """Scan I2C bus and display found devices."""
    print("=" * 60)
    print("Pixiboo I2C Scanner")
    print("=" * 60)
    
    # I2C pins from hardware.py
    SCL_PIN = 15
    SDA_PIN = 16
    
    print(f"\nI2C Configuration:")
    print(f"  SCL: GPIO{SCL_PIN}")
    print(f"  SDA: GPIO{SDA_PIN}")
    print(f"  Frequency: 400kHz")
    
    # Try different I2C configurations
    configs = [
        {"id": 0, "freq": 400000, "name": "I2C0 @ 400kHz"},
        {"id": 0, "freq": 100000, "name": "I2C0 @ 100kHz"},
        {"id": 1, "freq": 400000, "name": "I2C1 @ 400kHz"},
    ]
    
    for config in configs:
        print(f"\n{'─' * 60}")
        print(f"Trying: {config['name']}")
        print(f"{'─' * 60}")
        
        try:
            i2c = I2C(config['id'], scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=config['freq'])
            devices = i2c.scan()
            
            if devices:
                print(f"✓ Found {len(devices)} device(s):")
                for addr in devices:
                    device_name = get_device_name(addr)
                    print(f"  • Address: {hex(addr)} ({addr}) - {device_name}")
            else:
                print("✗ No devices found")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n{'=' * 60}")
    print("Expected for Pixiboo:")
    print("  BNO055 at 0x28 (40) or 0x29 (41)")
    print(f"{'=' * 60}\n")
    
    # Troubleshooting tips
    print("If no devices found, check:")
    print("  1. Is BNO055 getting power (3.3V)?")
    print("  2. Are GND connections secure?")
    print("  3. Are SDA and SCL connected correctly?")
    print("  4. Are pullup resistors present? (Usually 4.7kΩ)")
    print("  5. Try pressing RESET on the Pixiboo")

def get_device_name(addr):
    """Get likely device name from I2C address."""
    known_devices = {
        0x28: "BNO055 (9-axis IMU)",
        0x29: "BNO055 (alt address)",
        0x68: "MPU6050/MPU9250",
        0x69: "MPU6050 (alt address)",
        0x6A: "LSM6DS3",
        0x76: "BME280/BMP280",
        0x77: "BME280/BMP280 (alt)",
    }
    return known_devices.get(addr, "Unknown device")

if __name__ == "__main__":
    scan_i2c()



