#!/usr/bin/env python3
"""
Test script to spin the robot wheels using the corrected gpiozero motor setup.
Run this script on your Pi (with the web server running) to verify motor control.
"""


import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from chipurobo.hardware.motors import forward, backward, left, right, stop

print("Testing robot wheels...")

try:
    print("Spinning FORWARD for 2 seconds...")
    forward()
    time.sleep(2)
    stop()
    time.sleep(1)

    print("Spinning BACKWARD for 2 seconds...")
    backward()
    time.sleep(2)
    stop()
    time.sleep(1)

    print("Turning LEFT for 1.5 seconds...")
    left()
    time.sleep(1.5)
    stop()
    time.sleep(1)

    print("Turning RIGHT for 1.5 seconds...")
    right()
    time.sleep(1.5)
    stop()
    time.sleep(1)

    print("Test complete. Motors stopped.")
except KeyboardInterrupt:
    stop()
    print("Test interrupted. Motors stopped.")
