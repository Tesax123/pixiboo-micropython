"""
I2C Scanner for Pixiboo

Scans the I2C bus to find connected devices.
Helps debug accelerometer connection issues.
"""

from machine import Pin, I2C
import time

# Optional: toggle IMU reset if wired. Safe if not connected.
try:
    from pixiboo.hardware import IMU_RESET_PIN
except Exception:
    IMU_RESET_PIN = None

# Optional: force address select low (0x28) if exposed.
try:
    from pixiboo.hardware import IMU_ADDRESS_SELECT_PIN
except Exception:
    IMU_ADDRESS_SELECT_PIN = None

def scan_i2c():
    """Scan I2C bus and display found devices."""
    print("=" * 60)
    print("Pixiboo I2C Scanner")
    print("=" * 60)
    
    # I2C pins from hardware.py (Pixiboo external IMU header)
    SCL_PIN = 15
    SDA_PIN = 16

    # Give the BNO055 time to boot after power/reset
    print("\nBoot delay: waiting 1.0s for IMU to power up...")
    time.sleep(1.0)

    # Try to force address select to 0x28 (low) if available
    if IMU_ADDRESS_SELECT_PIN is not None:
        try:
            adr = Pin(IMU_ADDRESS_SELECT_PIN, Pin.OUT)
            adr.value(0)
            time.sleep(0.01)
            print(f"Address-select pin {IMU_ADDRESS_SELECT_PIN} set LOW (0x28)")
        except Exception as e:
            print(f"(Address-select toggle skipped: {e})")

    # Try to release reset if the pin is available
    if IMU_RESET_PIN is not None:
        try:
            rst = Pin(IMU_RESET_PIN, Pin.OUT)
            rst.value(0)
            time.sleep(0.01)
            rst.value(1)
            time.sleep(0.05)
            print(f"Reset pin {IMU_RESET_PIN} toggled before scan")
        except Exception as e:
            print(f"(Reset pin toggle skipped: {e})")
    
    print(f"\nI2C Configuration:")
    print(f"  SCL: GPIO{SCL_PIN}")
    print(f"  SDA: GPIO{SDA_PIN}")
    print(f"  Frequency: 400kHz")
    
    # Try different I2C configurations
    # Start with 100kHz since brute-force scanner confirmed that works
    configs = [
        {"id": 0, "freq": 100000, "name": "I2C0 @ 100kHz"},
        {"id": 0, "freq": 400000, "name": "I2C0 @ 400kHz"},
        {"id": 1, "freq": 100000, "name": "I2C1 @ 100kHz"},
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

