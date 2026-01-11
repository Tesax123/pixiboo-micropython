"""
Display Demo - Shows how to use the display() function

This example demonstrates:
- Displaying text messages
- Using different colors
- Showing numbers and symbols
- Creating scrolling messages
"""

from pixiboo import *

# Simple greeting
display("HELLO", RED)
sleep(1000)

# Math symbols
display("2+2=4", YELLOW)
sleep(1000)

# Slower display (custom delay of 1000ms per character)
display("SLOW", GREEN, delay=1000)
sleep(500)

# Faster display (custom delay of 300ms per character)
display("FAST", CYAN, delay=300)
sleep(1000)

# All symbols
display(":+-=*!?.,", WHITE)
sleep(1000)

# All available characters
display("ABCDEFGHIJKLMNOPQRSTUVWXYZ", GREEN)
sleep(1000)
display("0123456789", BLUE)
sleep(1000)
display("!?.,:-+=*", YELLOW)
sleep(1000)

# Clear screen
clear()
