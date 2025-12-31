"""
Accelerometer fill demo for Pixiboo.

Tilt the Pixiboo to move a cursor around the LED matrix.
The cursor leaves a trail, filling the screen as you move it.
You see the cursor in a different color so you know where you are.
"""

from pixiboo import matrix, accelerometer, init_accelerometer
from pixiboo.colors import CYAN, GREEN, YELLOW
import time

def main():
    """Main demo loop."""
    print("Accelerometer Fill Demo")
    print("Tilt the Pixiboo to move the cursor and fill the screen!")
    print("Press Ctrl+C to exit\n")
    
    # Ensure accelerometer is initialized
    acc = accelerometer or init_accelerometer()
    if acc is None:
        print("ERROR: Accelerometer not available. Run i2c_scanner first.")
        return

    # Check accelerometer status
    print(f"Accelerometer type: {acc._imu_type}")
    if acc._addr:
        print(f"I2C address: {hex(acc._addr)}\n")
    else:
        print("Running in simulation mode\n")
    
    # Clear the matrix
    matrix.clear()
    matrix.show()
    
    # Track filled pixels
    filled_pixels = set()
    
    # Current cursor position (center)
    x = 3
    y = 3
    
    # Mark starting position as filled
    filled_pixels.add((y, x))
    
    # Draw starting cursor
    matrix[y][x] = YELLOW
    matrix.show()
    
    # Thresholds for movement
    THRESHOLD = 250
    
    # Movement delay to prevent zipping across screen
    last_move_time = 0
    MOVE_DELAY = 0.15  # 150ms between moves = slower, more controlled
    
    print(f"Movement threshold: ±{THRESHOLD} mg")
    print(f"Movement delay: {MOVE_DELAY}s between steps")
    print("Colors: Cursor=YELLOW, Filled=GREEN\n")
    
    try:
        while True:
            # Read accelerometer
            accel_x = acc.get_x()
            accel_y = acc.get_y()
            
            # Check if enough time has passed since last movement
            current_time = time.ticks_ms() / 1000.0
            can_move = (current_time - last_move_time) >= MOVE_DELAY
            
            # Determine movement direction
            move_x = 0
            move_y = 0
            
            if can_move:
                if accel_x > THRESHOLD:
                    move_x = 1  # Move right
                elif accel_x < -THRESHOLD:
                    move_x = -1  # Move left
                
                if accel_y > THRESHOLD:
                    move_y = -1  # Move up (tilt forward = up on screen)
                elif accel_y < -THRESHOLD:
                    move_y = 1  # Move down (tilt back = down on screen)
                
                # Apply movement if any
                if move_x != 0 or move_y != 0:
                    old_x, old_y = x, y
                    x = max(0, min(6, x + move_x))
                    y = max(0, min(6, y + move_y))
                    
                    # Only update if we actually moved to a new position
                    if x != old_x or y != old_y:
                        last_move_time = current_time
                        filled_pixels.add((y, x))
                        
                        # Change old cursor position to GREEN (filled trail)
                        matrix[old_y][old_x] = GREEN
                        
                        # Draw new cursor position in YELLOW
                        matrix[y][x] = YELLOW
                        
                        # Show the updated matrix (only update when moved)
                        matrix.show()
                        
                        # Print movement info
                        direction = ""
                        if move_x > 0:
                            direction += "→"
                        elif move_x < 0:
                            direction += "←"
                        if move_y > 0:
                            direction += "↓"
                        elif move_y < 0:
                            direction += "↑"
                        
                        progress = len(filled_pixels) / 49.0 * 100
                        print(f"[{y},{x}] {direction} | X:{accel_x:5d} Y:{accel_y:5d} | {len(filled_pixels)}/49 ({progress:.0f}%)")
            
            # Small delay for reading accelerometer
            time.sleep(0.02)
            
    except KeyboardInterrupt:
        print(f"\nDemo stopped! Filled {len(filled_pixels)}/49 pixels ({len(filled_pixels)/49.0*100:.1f}%)")
        time.sleep(2)
        matrix.clear()
        matrix.show()

if __name__ == "__main__":
    main()
