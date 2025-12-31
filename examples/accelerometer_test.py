"""
Accelerometer raw data test for Pixiboo.

Simply reads and displays accelerometer data to verify it's working.
No LED matrix, just debug output.
"""

import pixiboo
import time

def main():
    """Main test loop."""
    print("Accelerometer Raw Data Test")
    print("=" * 60)
    
    # Initialize accelerometer (must be done after import)
    print("\nInitializing accelerometer...")
    accelerometer = pixiboo.init_accelerometer()
    
    # Check if accelerometer is available
    if accelerometer is None:
        print("\n✗ ERROR: Accelerometer initialization failed!")
        print("The BNO055 was not detected.")
        print("\nTroubleshooting:")
        print("  1. Run: %Run examples/i2c_scanner.py")
        print("  2. Check if BNO055 is found at 0x28 or 0x29")
        print("  3. If found, press RESET on Pixiboo and try again")
        return
    
    # Check accelerometer status
    print(f"\n✓ Accelerometer initialized!")
    print(f"Type: {accelerometer._imu_type}")
    if accelerometer._addr:
        print(f"I2C address: {hex(accelerometer._addr)}")
    
    print("\nReading accelerometer data...")
    print("Format: X (left/right), Y (forward/back), Z (up/down)")
    print("Values in milli-g (mg), where 1000 mg = 1g (gravity)")
    print("\nPress Ctrl+C to stop\n")
    
    # Sample counters for statistics
    sample_count = 0
    x_min, x_max = 0, 0
    y_min, y_max = 0, 0
    z_min, z_max = 0, 0
    
    try:
        while True:
            # Read values
            x, y, z = accelerometer.get_values()
            
            # Update statistics
            sample_count += 1
            if sample_count == 1:
                x_min = x_max = x
                y_min = y_max = y
                z_min = z_max = z
            else:
                x_min = min(x_min, x)
                x_max = max(x_max, x)
                y_min = min(y_min, y)
                y_max = max(y_max, y)
                z_min = min(z_min, z)
                z_max = max(z_max, z)
            
            # Print current reading
            print(f"Sample {sample_count:4d} | X:{x:6d} Y:{y:6d} Z:{z:6d} mg")
            
            # Print statistics every 50 samples
            if sample_count % 50 == 0:
                print("-" * 60)
                print(f"Statistics (last {sample_count} samples):")
                print(f"  X range: {x_min:6d} to {x_max:6d} (span: {x_max-x_min:6d} mg)")
                print(f"  Y range: {y_min:6d} to {y_max:6d} (span: {y_max-y_min:6d} mg)")
                print(f"  Z range: {z_min:6d} to {z_max:6d} (span: {z_max-z_min:6d} mg)")
                print("-" * 60 + "\n")
            
            # Delay
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print(f"\n\nTest stopped after {sample_count} samples")
        print("\nFinal statistics:")
        print(f"  X range: {x_min:6d} to {x_max:6d} (span: {x_max-x_min:6d} mg)")
        print(f"  Y range: {y_min:6d} to {y_max:6d} (span: {y_max-y_min:6d} mg)")
        print(f"  Z range: {z_min:6d} to {z_max:6d} (span: {z_max-z_min:6d} mg)")

if __name__ == "__main__":
    main()

