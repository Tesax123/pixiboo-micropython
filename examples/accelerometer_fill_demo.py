"""
Accelerometer fill demo for Pixiboo.

Tilt the Pixiboo to move a "cursor" around the LED matrix.
The cursor leaves a trail, filling the screen as you move it.
Based on micro:bit accelerometer LED control examples.
"""

from pixiboo import matrix, accelerometer
from pixiboo.colors import CYAN, GREEN
import time

def main():
    """Main demo loop."""
    print("Accelerometer Fill Demo")
    print("Tilt the Pixiboo to move the cursor and fill the screen!")
    print("Press Ctrl+C to exit\n")
    
    # Check accelerometer status
    print(f"Accelerometer type: {accelerometer._imu_type}")
    if accelerometer._addr:
        print(f"I2C address: {hex(accelerometer._addr)}\n")
    else:
        print("Running in simulation mode\n")
    
    # Don't calibrate - we want raw tilt data
    # This makes it more responsive to actual tilting
    
    # Clear the matrix
    matrix.clear()
    matrix.show()
    
    # Track filled pixels
    filled_pixels = set()
    
    # Current cursor position (center)
    x = 3
    y = 3
    
    # Light up starting position
    matrix[y][x] = GREEN
    filled_pixels.add((y, x))
    matrix.show()
    
    loop_count = 0
    
    try:
        while True:
            # Read accelerometer - use raw values for direct tilt sensing
            accel_x = accelerometer.get_x()
            accel_y = accelerometer.get_y()
            
            # Map accelerometer to movement
            # Use lower thresholds for more sensitive/responsive control
            # Micro:bit typically uses ±150-200 for smooth movement
            
            # Move cursor based on tilt
            # X axis: tilting right = positive values, move right
            if accel_x > 150:  # Tilted right
                x = min(x + 1, 6)
            elif accel_x < -150:  # Tilted left
                x = max(x - 1, 0)
            
            # Y axis: tilting forward = positive values, move down
            if accel_y > 150:  # Tilted forward
                y = min(y + 1, 6)
            elif accel_y < -150:  # Tilted backward
                y = max(y - 1, 0)
            
            # Light up current position
            matrix[y][x] = GREEN
            filled_pixels.add((y, x))
            
            # Show the matrix
            matrix.show()
            
            # Debug output (less frequent since updates are faster)
            loop_count += 1
            if loop_count % 40 == 0:
                progress = len(filled_pixels) / 49.0 * 100
                direction = ""
                if accel_x > 150:
                    direction += "→"
                elif accel_x < -150:
                    direction += "←"
                if accel_y > 150:
                    direction += "↓"
                elif accel_y < -150:
                    direction += "↑"
                if not direction:
                    direction = "·"
                print(f"[{y},{x}] {direction} | Accel X={accel_x:5d} Y={accel_y:5d} | {len(filled_pixels)}/49 ({progress:.0f}%)")
            
            # Delay for smooth movement
            time.sleep(0.05)  # 20 updates per second - faster, more responsive
            
    except KeyboardInterrupt:
        print(f"\nDemo stopped! Filled {len(filled_pixels)}/49 pixels ({len(filled_pixels)/49.0*100:.1f}%)")
        time.sleep(2)
        matrix.clear()
        matrix.show()

if __name__ == "__main__":
    main()
