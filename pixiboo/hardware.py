"""
Hardware constants for the Pixiboo board.

Keep all pin knowledge in one place; no logic here.
"""

LED_PIN = 18
NUM_LEDS = 49

BUTTON_LEFT = 12
BUTTON_CENTER = 11
BUTTON_RIGHT = 13

BUZZER_PIN = 38

EYE_LEFT_PIN = 21
EYE_RIGHT_PIN = 14

# I2C pins for external IMU
I2C_SCL_PIN = 15
I2C_SDA_PIN = 16
IMU_RESET_PIN = 48
IMU_INTERRUPT_PIN = 47
IMU_ADDRESS_SELECT_PIN = 45

__all__ = [
    "LED_PIN",
    "NUM_LEDS",
    "BUTTON_LEFT",
    "BUTTON_CENTER",
    "BUTTON_RIGHT",
    "BUZZER_PIN",
    "EYE_LEFT_PIN",
    "EYE_RIGHT_PIN",
    "I2C_SCL_PIN",
    "I2C_SDA_PIN",
    "IMU_RESET_PIN",
    "IMU_INTERRUPT_PIN",
    "IMU_ADDRESS_SELECT_PIN",
]

