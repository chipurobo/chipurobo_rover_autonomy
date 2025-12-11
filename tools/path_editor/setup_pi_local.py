#!/usr/bin/env python3
"""
Local Raspberry Pi Setup Script
Run this script directly on your Raspberry Pi to install and configure the robot system.
No SSH or remote machines needed - everything runs locally on the Pi.
"""

import os
import sys
import subprocess
import json

def run_command(cmd, description, check=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr.strip()}")
        return False

def install_dependencies():
    """Install required Python packages and system dependencies"""
    print("📦 Installing system dependencies...")
    
    # Update package list
    run_command("sudo apt update", "Updating package list")
    
    # Install Python packages
    packages = [
        "python3-pip",
        "python3-flask", 
        "python3-flask-cors",
        "python3-rpi.gpio",
        "python3-gpiozero",
    ]
    
    for package in packages:
        run_command(f"sudo apt install -y {package}", f"Installing {package}")
    
    # Install additional pip packages if needed
    pip_packages = ["flask-cors"]
    for package in pip_packages:
        run_command(f"pip3 install {package}", f"Installing {package} via pip", check=False)

def create_robot_directory():
    """Create robot project directory structure"""
    print("\n📁 Setting up project directory...")
    
    home_dir = os.path.expanduser("~")
    robot_dir = os.path.join(home_dir, "robot_mission_control")
    
    # Create directories
    dirs = [
        robot_dir,
        os.path.join(robot_dir, "missions"),
        os.path.join(robot_dir, "logs")
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created: {dir_path}")
    
    return robot_dir

def copy_project_files(robot_dir):
    """Copy project files to robot directory"""
    print("\n📋 Copying project files...")
    
    # Get current script directory (where this script is run from)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    files_to_copy = [
        "web_editor.html",
        "robot_server.py", 
        "raspberry_pi_robot.py",
        "robot_interface.py",
        "launch_mission_control.py"
    ]
    
    for file_name in files_to_copy:
        src = os.path.join(current_dir, file_name)
        dst = os.path.join(robot_dir, file_name)
        
        if os.path.exists(src):
            run_command(f"cp {src} {dst}", f"Copying {file_name}")
        else:
            print(f"⚠️  Warning: {file_name} not found in {current_dir}")

def create_startup_script(robot_dir):
    """Create startup script for easy launching"""
    startup_script = f"""#!/bin/bash
# Robot Mission Control Startup Script
echo "🚀 Starting Robot Mission Control System..."

cd {robot_dir}

# Make sure we're in the right directory
echo "📁 Working directory: $(pwd)"

# Start the mission control system
python3 launch_mission_control.py
"""
    
    script_path = os.path.join(robot_dir, "start_robot.sh")
    with open(script_path, "w") as f:
        f.write(startup_script)
    
    # Make executable
    run_command(f"chmod +x {script_path}", "Making startup script executable")
    print(f"✅ Created startup script: {script_path}")

def create_wiring_guide(robot_dir):
    """Create hardware wiring guide"""
    wiring_guide = """
# 🔌 Raspberry Pi + L298N Motor Driver Wiring Guide

## Required Hardware:
- Raspberry Pi (any model with GPIO)
- L298N Motor Driver Module
- 2x DC Motors 
- Battery pack (6-12V for motors)
- Jumper wires

## Wiring Connections:

### L298N to Raspberry Pi GPIO:
```
L298N Pin    →    Raspberry Pi Pin    →    GPIO Number
---------------------------------------------------------
IN1          →    Pin 11              →    GPIO 17
IN2          →    Pin 13              →    GPIO 27  
IN3          →    Pin 15              →    GPIO 22
IN4          →    Pin 16              →    GPIO 23
ENA (PWM)    →    Pin 12              →    GPIO 18
ENB (PWM)    →    Pin 18              →    GPIO 24
GND          →    Pin 6 (GND)         →    Ground
```

### Motor Connections to L298N:
```
Left Motor:   OUT1 and OUT2
Right Motor:  OUT3 and OUT4
```

### Power Supply:
```
Battery +12V  →  L298N VCC (Motor Power)
Battery GND   →  L298N GND (Motor Ground) 
Pi 5V         →  L298N +5V (Logic Power) - Optional if using separate power
Pi GND        →  L298N GND (Logic Ground)
```

## ⚠️ Important Notes:
1. Remove the L298N +5V jumper if using separate motor power supply
2. Use 6-12V battery pack for motors (NOT connected to Pi directly)
3. Common ground between Pi and L298N is essential
4. ENA and ENB jumpers should be removed for PWM speed control

## 🔧 Test Your Wiring:
After wiring, run: python3 test_motors.py
"""
    
    guide_path = os.path.join(robot_dir, "WIRING_GUIDE.md")
    with open(guide_path, "w") as f:
        f.write(wiring_guide)
    print(f"✅ Created wiring guide: {guide_path}")

def create_test_script(robot_dir):
    """Create motor test script"""
    test_script = '''#!/usr/bin/env python3
"""
Motor Test Script - Run this to verify your motor wiring
"""
import sys
import time

try:
    import RPi.GPIO as GPIO
    print("✅ RPi.GPIO imported successfully")
except ImportError:
    print("❌ RPi.GPIO not available. Install with: sudo apt install python3-rpi.gpio")
    sys.exit(1)

# Motor pins (matching raspberry_pi_robot.py)
MOTOR_PINS = {
    'left': {'in1': 17, 'in2': 27, 'enable': 18},
    'right': {'in1': 22, 'in2': 23, 'enable': 24}
}

def setup_gpio():
    """Setup GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for motor, pins in MOTOR_PINS.items():
        GPIO.setup(pins['in1'], GPIO.OUT)
        GPIO.setup(pins['in2'], GPIO.OUT)
        GPIO.setup(pins['enable'], GPIO.OUT)
        
        # Create PWM instance
        pwm = GPIO.PWM(pins['enable'], 1000)
        pwm.start(0)
        MOTOR_PINS[motor]['pwm'] = pwm

def test_motor(motor_name, direction, speed=50, duration=2):
    """Test a single motor"""
    pins = MOTOR_PINS[motor_name]
    print(f"Testing {motor_name} motor {direction} at {speed}% speed...")
    
    if direction == "forward":
        GPIO.output(pins['in1'], GPIO.HIGH)
        GPIO.output(pins['in2'], GPIO.LOW)
    else:  # backward
        GPIO.output(pins['in1'], GPIO.LOW)
        GPIO.output(pins['in2'], GPIO.HIGH)
    
    pins['pwm'].ChangeDutyCycle(speed)
    time.sleep(duration)
    pins['pwm'].ChangeDutyCycle(0)

def main():
    print("🔧 Motor Test Script")
    print("Make sure your motors are wired correctly and not connected to wheels yet!")
    input("Press Enter to continue...")
    
    try:
        setup_gpio()
        
        # Test each motor
        for motor in ['left', 'right']:
            test_motor(motor, 'forward', 30, 1)
            time.sleep(0.5)
            test_motor(motor, 'backward', 30, 1) 
            time.sleep(1)
        
        print("✅ Motor test complete!")
        
    except KeyboardInterrupt:
        print("\\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        # Cleanup
        for motor_pins in MOTOR_PINS.values():
            if 'pwm' in motor_pins:
                motor_pins['pwm'].stop()
        GPIO.cleanup()
        print("🧹 GPIO cleanup complete")

if __name__ == "__main__":
    main()
'''
    
    test_path = os.path.join(robot_dir, "test_motors.py")
    with open(test_path, "w") as f:
        f.write(test_script)
    
    run_command(f"chmod +x {test_path}", "Making test script executable")
    print(f"✅ Created motor test script: {test_path}")

def main():
    print("🤖 Raspberry Pi Robot Setup (Local Installation)")
    print("=" * 50)
    
    # Check if running on Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' not in f.read():
                print("⚠️  Warning: This doesn't appear to be a Raspberry Pi")
    except:
        pass
    
    # Install dependencies
    install_dependencies()
    
    # Create project directory
    robot_dir = create_robot_directory()
    
    # Copy files
    copy_project_files(robot_dir)
    
    # Create additional files
    create_startup_script(robot_dir)
    create_wiring_guide(robot_dir) 
    create_test_script(robot_dir)
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print(f"📁 Robot files installed to: {robot_dir}")
    print("\n📋 Next Steps:")
    print("1. Wire your motors according to WIRING_GUIDE.md")
    print("2. Test motors: cd ~/robot_mission_control && python3 test_motors.py")
    print("3. Start system: cd ~/robot_mission_control && ./start_robot.sh")
    print("4. Open browser to: http://localhost:8081")
    print("\n🔧 Quick Start:")
    print(f"cd {robot_dir}")
    print("./start_robot.sh")

if __name__ == "__main__":
    main()