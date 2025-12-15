
from gpiozero import Motor, PWMOutputDevice

# -----------------------
# MOTOR SETUP (CORRECTED)
# -----------------------

motor_left = Motor(forward=17, backward=27)
motor_right = Motor(forward=22, backward=23)

# Enable pins required for motor power
enable_left = PWMOutputDevice(24)
enable_right = PWMOutputDevice(25)

# Set both enables HIGH (full power)
enable_left.value = 1
enable_right.value = 1

SPEED = 1.0   # 100% speed for all movements

def stop():
    motor_left.stop()
    motor_right.stop()
    print("STOP")

def forward():
    motor_left.forward(SPEED)
    motor_right.forward(SPEED)
    print("FORWARD")

def backward():
    motor_left.backward(SPEED)
    motor_right.backward(SPEED)
    print("BACKWARD")

def left():
    motor_left.backward(SPEED)
    motor_right.forward(SPEED)
    print("LEFT")

def right():
    motor_left.forward(SPEED)
    motor_right.backward(SPEED)
    print("RIGHT")