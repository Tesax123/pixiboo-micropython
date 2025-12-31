"""
Brute-force I2C scanner for Pixiboo.

Tries multiple SDA/SCL pin pairs to discover where the BNO055 is wired.
Use this if the normal scanner finds no devices.
"""

import time
from machine import Pin, I2C

# Candidate (sda, scl) pin pairs to try.
# First pair is the expected one; others cover likely PCB rewires.
CANDIDATE_PAIRS = [
    (16, 15),  # expected from docs (SDA=16, SCL=15)
    (15, 16),
    (41, 42),
    (42, 41),
    (45, 41),
    (41, 45),
    (45, 42),
    (42, 45),
    (17, 18),
    (18, 17),
]

KNOWN = {
    0x28: "BNO055 (9-axis IMU)",
    0x29: "BNO055 (alt address)",
    0x68: "MPU6050/MPU9250",
    0x69: "MPU6050 (alt address)",
    0x6A: "LSM6DS3",
    0x76: "BME280/BMP280",
    0x77: "BME280/BMP280 (alt)",
}


def main():
    print("=" * 60)
    print("Pixiboo I2C Brute-Force Scanner")
    print("=" * 60)
    print("Trying multiple SDA/SCL pin pairs to find the IMU.")
    print("Waiting 1s for IMU to power up...")
    time.sleep(1.0)

    for sda_pin, scl_pin in CANDIDATE_PAIRS:
        print("\n" + "─" * 60)
        print(f"Trying SDA=GPIO{sda_pin}, SCL=GPIO{scl_pin} @ 100kHz")
        print("─" * 60)
        try:
            i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000)
            time.sleep(0.02)
            devices = i2c.scan()
            if devices:
                print(f"✓ Found {len(devices)} device(s):")
                for addr in devices:
                    name = KNOWN.get(addr, "Unknown device")
                    print(f"  • {hex(addr)} ({addr}) - {name}")
                print("\nStop here: use this pin pair in your code.")
                return
            else:
                print("✗ No devices found on this pair.")
        except Exception as e:
            print(f"✗ Error on this pair: {e}")

    print("\n" + "=" * 60)
    print("No I2C devices detected on tried pin pairs.")
    print("If you know the IMU pins, use those explicitly.")
    print("=" * 60)


if __name__ == "__main__":
    main()


