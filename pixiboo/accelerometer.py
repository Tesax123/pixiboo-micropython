"""
Accelerometer access for Pixiboo, similar to micro:bit API.

Supports common I2C accelerometers/IMUs like MPU6050, MPU9250, LSM6DS3.
"""

from .hardware import I2C_SCL_PIN, I2C_SDA_PIN, IMU_RESET_PIN, IMU_ADDRESS_SELECT_PIN

try:
    from machine import Pin, I2C
except ImportError:  # pragma: no cover - host fallback
    class Pin:  # type: ignore
        OUT = 1

        def __init__(self, *_, **__):
            pass

        def value(self, val=None):
            if val is None:
                return 0
            return None

    class I2C:  # type: ignore
        def __init__(self, *_, **__):
            self._x = 0
            self._y = 0
            self._z = 0

        def readfrom_mem(self, addr, reg, nbytes):
            return bytes([0] * nbytes)

        def writeto_mem(self, addr, reg, buf):
            pass

        def scan(self):
            return []

try:
    import utime as _time
    import math
except ImportError:  # pragma: no cover
    import time as _time
    try:
        import math
    except ImportError:
        # Fallback if math not available
        import sys
        math = sys.modules.get('math', None)


def _sleep_ms(ms: int) -> None:
    if hasattr(_time, "sleep_ms"):
        _time.sleep_ms(ms)  # type: ignore[attr-defined]
    else:
        _time.sleep(ms / 1000.0)


# Common IMU I2C addresses
MPU6050_ADDR = 0x68
MPU6050_ADDR_ALT = 0x69
LSM6DS3_ADDR = 0x6A
MPU9250_ADDR = 0x68
BNO055_ADDR = 0x28
BNO055_ADDR_ALT = 0x29

# MPU6050 register addresses
MPU6050_REG_PWR_MGMT_1 = 0x6B
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_WHO_AM_I = 0x75

# LSM6DS3 register addresses
LSM6DS3_REG_CTRL1_XL = 0x10
LSM6DS3_REG_OUTX_L_XL = 0x28
LSM6DS3_REG_WHO_AM_I = 0x0F

# BNO055 register addresses
BNO055_REG_CHIP_ID = 0x00
BNO055_REG_PAGE_ID = 0x07
BNO055_REG_OPR_MODE = 0x3D
BNO055_REG_PWR_MODE = 0x3E
BNO055_REG_SYS_TRIGGER = 0x3F
BNO055_REG_ACCEL_DATA_X_LSB = 0x08
BNO055_REG_ACCEL_DATA_X_MSB = 0x09
BNO055_REG_ACCEL_DATA_Y_LSB = 0x0A
BNO055_REG_ACCEL_DATA_Y_MSB = 0x0B
BNO055_REG_ACCEL_DATA_Z_LSB = 0x0C
BNO055_REG_ACCEL_DATA_Z_MSB = 0x0D

# BNO055 constants
BNO055_ID = 0xA0
BNO055_OPERATION_MODE_CONFIG = 0x00
BNO055_OPERATION_MODE_NDOF = 0x0C  # 9-DOF fusion mode
BNO055_POWER_MODE_NORMAL = 0x00


class Accelerometer:
    """
    Accelerometer interface similar to micro:bit API.
    
    Returns acceleration values in milli-g (mg) units, similar to micro:bit.
    Values typically range from -2000 to +2000 mg (±2g range).
    """

    def __init__(self, i2c_freq: int = 100000):
        """
        Initialize the accelerometer.
        
        Args:
            i2c_freq: I2C bus frequency in Hz (default 100kHz - matches working config)
        """
        # Try multiple I2C configurations to find what works
        # The scanner found it, so we need to match that configuration exactly
        self._i2c = None
        self._addr = None
        self._imu_type = None
        
        # Give BNO055 time to boot FIRST (brute-force scanner confirmed 1s wait works)
        # Match the scanner exactly - no pin manipulation before I2C init
        print("[Accelerometer] Waiting for BNO055 to boot (1s)...")
        _sleep_ms(1000)
        
        # Try I2C configuration that worked in brute-force scanner
        # SDA=GPIO16, SCL=GPIO15 @ 100kHz on I2C(0)
        try:
            print(f"[Accelerometer] Creating I2C(0) with SDA=GPIO{I2C_SDA_PIN}, SCL=GPIO{I2C_SCL_PIN} @ 100kHz...")
            self._i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=100000)
            _sleep_ms(20)  # Small delay after creating I2C (like scanner)
            
            # Scan for devices
            devices = self._i2c.scan()
            if devices:
                print(f"[Accelerometer] I2C scan found devices: {[hex(d) for d in devices]}")
            else:
                print("[Accelerometer] I2C scan found no devices")
                self._i2c = None
        except Exception as err:
            print(f"[Accelerometer] I2C initialization failed: {err}")
            self._i2c = None
        
        # Fallback: try other configs if first one failed
        if self._i2c is None:
            print("[Accelerometer] Trying fallback I2C configurations...")
            i2c_configs = [
                (0, 400000),  # I2C0 @ 400kHz
                (1, 100000),  # I2C1 @ 100kHz
            ]
            
            for i2c_id, freq in i2c_configs:
                try:
                    self._i2c = I2C(i2c_id, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=freq)
                    _sleep_ms(20)
                    devices = self._i2c.scan()
                    if devices:
                        print(f"[Accelerometer] I2C({i2c_id}) @ {freq}Hz found devices: {[hex(d) for d in devices]}")
                        break
                    else:
                        self._i2c = None
                except Exception as err:
                    print(f"[Accelerometer] I2C({i2c_id}) @ {freq}Hz failed: {err}")
                    self._i2c = None
                    continue
        
        if self._i2c is None:
            raise RuntimeError("Failed to initialize I2C bus - no working configuration found")
        
        # Auto-detect IMU
        self._detect_imu()
        
        # Calibration offsets (can be set by user)
        self._offset_x = 0
        self._offset_y = 0
        self._offset_z = 0
        
        # Last read values
        self._x = 0
        self._y = 0
        self._z = 0
        
        # Shake detection state
        self._shake_threshold = 1500  # mg - threshold for shake detection
        self._shake_detected = False  # True if shake was detected
        self._last_shake_time = 0  # Timestamp of last shake detection
        self._shake_debounce_ms = 500  # Debounce time in milliseconds

    def _detect_imu(self) -> None:
        """Auto-detect which IMU is connected."""
        devices = self._i2c.scan()
        
        print(f"[Accelerometer] I2C scan found devices: {[hex(d) for d in devices]}")
        
        if not devices:
            # No I2C device found
            print("[Accelerometer] ERROR: No I2C devices found!")
            print("[Accelerometer] Check:")
            print("  - Is the BNO055 powered (VCC/GND connected)?")
            print("  - Are I2C pins correct (SDA=GPIO16, SCL=GPIO15)?")
            print("  - Are pullup resistors present on SDA/SCL?")
            raise RuntimeError("No accelerometer detected on I2C bus")
        
        # Try BNO055 first (Pixiboo uses this!)
        if BNO055_ADDR in devices:
            self._addr = BNO055_ADDR
            self._imu_type = "bno055"
            print(f"[Accelerometer] Detected BNO055 at address {hex(self._addr)}")
            self._init_bno055()
        elif BNO055_ADDR_ALT in devices:
            self._addr = BNO055_ADDR_ALT
            self._imu_type = "bno055"
            print(f"[Accelerometer] Detected BNO055 at alternate address {hex(self._addr)}")
            self._init_bno055()
        # Try MPU6050/MPU9250
        elif MPU6050_ADDR in devices:
            self._addr = MPU6050_ADDR
            self._imu_type = "mpu6050"
            print(f"[Accelerometer] Detected MPU6050 at address {hex(self._addr)}")
            self._init_mpu6050()
        elif MPU6050_ADDR_ALT in devices:
            self._addr = MPU6050_ADDR_ALT
            self._imu_type = "mpu6050"
            print(f"[Accelerometer] Detected MPU6050 at alternate address {hex(self._addr)}")
            self._init_mpu6050()
        elif LSM6DS3_ADDR in devices:
            self._addr = LSM6DS3_ADDR
            self._imu_type = "lsm6ds3"
            print(f"[Accelerometer] Detected LSM6DS3 at address {hex(self._addr)}")
            self._init_lsm6ds3()
        else:
            # Unknown device
            print(f"[Accelerometer] ERROR: Unknown I2C device at {[hex(d) for d in devices]}")
            print("[Accelerometer] Expected BNO055 at 0x28 or 0x29")
            raise RuntimeError(f"Unknown accelerometer at address {[hex(d) for d in devices]}")

    def _init_mpu6050(self) -> None:
        """Initialize MPU6050/MPU9250."""
        # Wake up the MPU6050 (clear sleep mode)
        self._i2c.writeto_mem(self._addr, MPU6050_REG_PWR_MGMT_1, bytes([0]))
        _sleep_ms(10)

    def _init_lsm6ds3(self) -> None:
        """Initialize LSM6DS3."""
        # Enable accelerometer at 104 Hz, ±2g range
        self._i2c.writeto_mem(self._addr, LSM6DS3_REG_CTRL1_XL, bytes([0x40]))
        _sleep_ms(10)

    def _init_bno055(self) -> None:
        """Initialize BNO055 - follows Adafruit library initialization sequence."""
        print("[Accelerometer] Initializing BNO055...")
        
        # BNO055 can take up to 850ms to boot - wait for it
        timeout = 850
        chip_id = 0
        while timeout > 0:
            try:
                chip_id = self._i2c.readfrom_mem(self._addr, BNO055_REG_CHIP_ID, 1)[0]
                if chip_id == BNO055_ID:
                    break
            except Exception:
                pass
            _sleep_ms(10)
            timeout -= 10
        
        if chip_id != BNO055_ID:
            # Try one more time after longer delay
            _sleep_ms(100)
            try:
                chip_id = self._i2c.readfrom_mem(self._addr, BNO055_REG_CHIP_ID, 1)[0]
            except Exception as e:
                raise RuntimeError(f"BNO055 not responding: {e}")
            
            if chip_id != BNO055_ID:
                raise RuntimeError(f"BNO055 wrong chip ID: got {hex(chip_id)}, expected {hex(BNO055_ID)}")
        
        print(f"[Accelerometer] BNO055 Chip ID verified: {hex(chip_id)}")
        
        # Switch to config mode (required before changing settings)
        self._i2c.writeto_mem(self._addr, BNO055_REG_OPR_MODE, bytes([BNO055_OPERATION_MODE_CONFIG]))
        _sleep_ms(25)
        
        # Note: some boards fail after reset. Try without reset first.
        # Set to normal power mode
        self._i2c.writeto_mem(self._addr, BNO055_REG_PWR_MODE, bytes([BNO055_POWER_MODE_NORMAL]))
        _sleep_ms(10)
        
        # Set page ID to 0
        self._i2c.writeto_mem(self._addr, BNO055_REG_PAGE_ID, bytes([0x00]))
        _sleep_ms(10)
        
        # Clear system trigger
        self._i2c.writeto_mem(self._addr, BNO055_REG_SYS_TRIGGER, bytes([0x00]))
        _sleep_ms(10)
        
        # Set to NDOF mode (9-DOF fusion mode)
        print("[Accelerometer] Setting BNO055 to NDOF mode...")
        self._i2c.writeto_mem(self._addr, BNO055_REG_OPR_MODE, bytes([BNO055_OPERATION_MODE_NDOF]))
        _sleep_ms(20)
        
        print("[Accelerometer] BNO055 initialized successfully!")

    def _read_mpu6050(self) -> tuple[int, int, int]:
        """Read acceleration from MPU6050/MPU9250."""
        # Read 6 bytes starting from ACCEL_XOUT_H
        data = self._i2c.readfrom_mem(self._addr, MPU6050_REG_ACCEL_XOUT_H, 6)
        
        # Convert to signed 16-bit values
        x = (data[0] << 8) | data[1]
        y = (data[2] << 8) | data[3]
        z = (data[4] << 8) | data[5]
        
        # Convert to signed integers
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536
        
        # Convert from raw values (±16384 = ±2g) to milli-g
        # Scale factor: 2000 mg / 16384 = 0.122 mg/LSB
        x_mg = int(x * 0.122)
        y_mg = int(y * 0.122)
        z_mg = int(z * 0.122)
        
        return (x_mg, y_mg, z_mg)

    def _read_lsm6ds3(self) -> tuple[int, int, int]:
        """Read acceleration from LSM6DS3."""
        # Read 6 bytes starting from OUTX_L_XL
        data = self._i2c.readfrom_mem(self._addr, LSM6DS3_REG_OUTX_L_XL, 6)
        
        # LSM6DS3 is little-endian
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        
        # Convert to signed integers
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536
        
        # Convert from raw values (±16384 = ±2g) to milli-g
        x_mg = int(x * 0.122)
        y_mg = int(y * 0.122)
        z_mg = int(z * 0.122)
        
        return (x_mg, y_mg, z_mg)

    def _read_bno055(self) -> tuple[int, int, int]:
        """Read acceleration from BNO055."""
        # Read 6 bytes starting from ACCEL_DATA_X_LSB
        data = self._i2c.readfrom_mem(self._addr, BNO055_REG_ACCEL_DATA_X_LSB, 6)
        
        # BNO055 is little-endian
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        
        # Convert to signed integers
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536
        
        # BNO055 accelerometer data is in m/s²
        # 1 m/s² = ~102 mg (milligravity)
        # BNO055 scale: 1 LSB = 0.01 m/s² = 1.02 mg
        # So multiply by ~1.02 to convert to mg
        # Or more accurately: 100 m/s² = 1g = 1000 mg, so 1 m/s² = 102 mg
        # BNO055 LSB = 0.01 m/s², so 1 LSB = 1.02 mg
        x_mg = int(x * 1.02)
        y_mg = int(y * 1.02)
        z_mg = int(z * 1.02)
        
        return (x_mg, y_mg, z_mg)

    def _read_raw(self) -> tuple[int, int, int]:
        """Read raw acceleration values from the IMU."""
        if self._imu_type == "bno055":
            return self._read_bno055()
        elif self._imu_type == "mpu6050":
            return self._read_mpu6050()
        elif self._imu_type == "lsm6ds3":
            return self._read_lsm6ds3()
        else:
            raise RuntimeError("No accelerometer initialized")

    def get_x(self) -> int:
        """
        Get acceleration in X axis in milli-g (mg).
        
        Returns:
            Acceleration value in mg, typically -2000 to +2000
        """
        self._x, self._y, self._z = self._read_raw()
        return self._x - self._offset_x

    def get_y(self) -> int:
        """
        Get acceleration in Y axis in milli-g (mg).
        
        Returns:
            Acceleration value in mg, typically -2000 to +2000
        """
        self._x, self._y, self._z = self._read_raw()
        return self._y - self._offset_y

    def get_z(self) -> int:
        """
        Get acceleration in Z axis in milli-g (mg).
        
        Returns:
            Acceleration value in mg, typically -2000 to +2000
        """
        self._x, self._y, self._z = self._read_raw()
        return self._z - self._offset_z

    def get_values(self) -> tuple[int, int, int]:
        """
        Get acceleration values for all axes as a tuple (x, y, z).
        
        Returns:
            Tuple of (x, y, z) acceleration values in mg
        """
        self._x, self._y, self._z = self._read_raw()
        return (
            self._x - self._offset_x,
            self._y - self._offset_y,
            self._z - self._offset_z,
        )

    def calibrate(self) -> None:
        """
        Calibrate the accelerometer by assuming it's at rest.
        This sets the current orientation as the zero point.
        """
        # Take multiple samples and average
        samples = 10
        sum_x, sum_y, sum_z = 0, 0, 0
        
        for _ in range(samples):
            x, y, z = self._read_raw()
            sum_x += x
            sum_y += y
            sum_z += z
            _sleep_ms(10)
        
        self._offset_x = sum_x // samples
        self._offset_y = sum_y // samples
        self._offset_z = sum_z // samples - 1000  # Assume gravity on Z axis

    def was_shaken(self) -> bool:
        """
        Check if the device was shaken since the last call.
        
        This method detects shake gestures by monitoring acceleration magnitude.
        Once a shake is detected, it returns True until the next call, then resets.
        This allows for event-driven programming patterns.
        
        Returns:
            True if a shake was detected since last call, False otherwise
        """
        # Read current acceleration values
        x, y, z = self.get_values()
        
        # Calculate acceleration magnitude (total acceleration vector length)
        # Using integer math to avoid floating point operations
        magnitude_squared = x * x + y * y + z * z
        
        # Compare against threshold squared (avoid sqrt for performance)
        threshold_squared = self._shake_threshold * self._shake_threshold
        
        # Get current time for debouncing
        if hasattr(_time, "ticks_ms"):
            current_time = _time.ticks_ms()  # type: ignore[attr-defined]
        else:
            current_time = int(_time.time() * 1000)
        
        # Check if acceleration exceeds threshold and debounce period has passed
        if magnitude_squared > threshold_squared:
            # Check debounce - only detect new shake if enough time has passed
            if hasattr(_time, "ticks_diff"):
                time_since_last = _time.ticks_diff(current_time, self._last_shake_time)  # type: ignore[attr-defined]
            else:
                time_since_last = current_time - self._last_shake_time
            
            if time_since_last >= self._shake_debounce_ms:
                self._shake_detected = True
                self._last_shake_time = current_time
        
        # Return and reset the shake state
        result = self._shake_detected
        self._shake_detected = False
        return result

    def set_shake_threshold(self, threshold_mg: int) -> None:
        """
        Set the shake detection threshold.
        
        Args:
            threshold_mg: Acceleration threshold in milli-g (mg). 
                         Higher values require stronger shakes to trigger.
                         Default is 1500 mg.
        """
        self._shake_threshold = threshold_mg


def on_shake(callback, threshold_mg: int = 1500):
    """
    Register a callback function to be called when a shake gesture is detected.
    
    This function continuously monitors the accelerometer and calls the callback
    whenever a shake is detected. It runs in a loop, so it should be used as
    an entry point in your program.
    
    Button event handlers (on_button_pressed) work alongside this function
    because they use GPIO interrupts which run asynchronously. However, if you
    want to combine shake detection with other polling-based code, use
    was_shaken() in your own loop instead.
    
    Args:
        callback: Function to call when shake is detected (takes no arguments)
        threshold_mg: Acceleration threshold in milli-g (mg) for shake detection.
                      Higher values require stronger shakes. Default is 1500 mg.
    
    Example:
        # Simple usage - shake only
        def handle_shake():
            print("Device was shaken!")
            matrix.fill(RED)
            matrix.show()
        
        on_shake(handle_shake)
    
    Example:
        # Combined with button handlers (buttons work via interrupts)
        from pixiboo import on_button_pressed, Button
        
        def handle_shake():
            print("Shaken!")
        
        def handle_button():
            print("Button pressed!")
        
        on_button_pressed(Button.LEFT, handle_button)
        on_shake(handle_shake)  # This blocks, but button interrupts still work
    
    Example:
        # Better: use was_shaken() in your own loop for full control
        while True:
            if accelerometer.was_shaken():
                handle_shake()
            # Check other things here too
            time.sleep_ms(50)
    """
    # Import here to avoid circular imports
    # Access the module-level accelerometer instance from the parent package
    import sys
    pixiboo_module = sys.modules.get('pixiboo')
    if pixiboo_module is None:
        # If pixiboo module not loaded, import it
        try:
            import pixiboo
            pixiboo_module = pixiboo
        except ImportError:
            raise RuntimeError("Cannot access pixiboo module. Make sure pixiboo is imported.")
    
    # Get or initialize accelerometer
    acc = getattr(pixiboo_module, 'accelerometer', None)
    if acc is None:
        # Try to initialize if not already done
        try:
            init_func = getattr(pixiboo_module, 'init_accelerometer', None)
            if init_func:
                acc = init_func()
        except Exception:
            pass
    
    if acc is None:
        raise RuntimeError("Accelerometer not available. Call init_accelerometer() first.")
    
    # Set threshold if different from default
    if threshold_mg != 1500:
        acc.set_shake_threshold(threshold_mg)
    
    # Continuous monitoring loop
    while True:
        if acc.was_shaken():
            try:
                callback()
            except Exception as e:
                # Don't let callback errors break the shake detection
                print(f"Error in shake callback: {e}")
        
        # Small delay to avoid excessive CPU usage
        _sleep_ms(50)


__all__ = ["Accelerometer", "on_shake"]

