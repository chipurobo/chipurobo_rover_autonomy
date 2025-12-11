#!/usr/bin/env python3
"""
Raspberry Pi Deployment Script
Deploys the robot mission control system to a Raspberry Pi
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def deploy_to_pi(pi_ip, pi_user="pi"):
    """Deploy mission control system to Raspberry Pi"""
    print("🚀 Deploying ChipuRobo Mission Control to Raspberry Pi")
    print(f"   Target: {pi_user}@{pi_ip}")
    print("=" * 60)
    
    # Check if we can reach the Pi
    if not run_command(f"ping -c 1 {pi_ip}", f"Testing connection to {pi_ip}"):
        print("❌ Cannot reach Raspberry Pi. Check IP address and network connection.")
        return False
    
    # Create project directory on Pi
    commands = [
        (f"ssh {pi_user}@{pi_ip} 'mkdir -p ~/chipurobo_mission_control'", 
         "Creating project directory on Pi"),
        
        # Copy Python files
        (f"scp raspberry_pi_robot.py robot_interface.py robot_server.py {pi_user}@{pi_ip}:~/chipurobo_mission_control/", 
         "Copying Python robot control files"),
        
        # Copy test integration
        (f"scp test_integration.py {pi_user}@{pi_ip}:~/chipurobo_mission_control/", 
         "Copying integration test script"),
        
        # Install required Python packages on Pi
        (f"ssh {pi_user}@{pi_ip} 'cd ~/chipurobo_mission_control && pip3 install flask flask-cors requests RPi.GPIO'", 
         "Installing Python dependencies on Pi"),
        
        # Make scripts executable
        (f"ssh {pi_user}@{pi_ip} 'chmod +x ~/chipurobo_mission_control/*.py'", 
         "Making scripts executable"),
        
        # Create systemd service for auto-start (optional)
        (f"ssh {pi_user}@{pi_ip} 'sudo cp ~/chipurobo_mission_control/robot_server.py /usr/local/bin/chipurobo_server'", 
         "Installing robot server"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️ Warning: {description} failed, but continuing...")
    
    # Test the installation
    print("\n🧪 Testing Raspberry Pi installation...")
    test_command = f"ssh {pi_user}@{pi_ip} 'cd ~/chipurobo_mission_control && python3 raspberry_pi_robot.py'"
    if run_command(test_command, "Testing robot hardware interface"):
        print("✅ Raspberry Pi deployment successful!")
        
        print(f"\n📋 Next Steps:")
        print(f"1. SSH to your Pi: ssh {pi_user}@{pi_ip}")
        print(f"2. Navigate to project: cd ~/chipurobo_mission_control")
        print(f"3. Start robot server: python3 robot_server.py")
        print(f"4. Use web interface to deploy missions")
        
        return True
    else:
        print("⚠️ Deployment completed with warnings - test robot hardware connections")
        return False

def create_pi_service():
    """Create systemd service file for auto-starting robot server"""
    service_content = """[Unit]
Description=ChipuRobo Mission Control Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/chipurobo_mission_control
ExecStart=/usr/bin/python3 /home/pi/chipurobo_mission_control/robot_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    
    with open("chipurobo.service", "w") as f:
        f.write(service_content)
    
    print("✅ Created chipurobo.service file")
    print("   Copy this to your Pi and install with:")
    print("   sudo cp chipurobo.service /etc/systemd/system/")
    print("   sudo systemctl enable chipurobo")
    print("   sudo systemctl start chipurobo")

def setup_pi_wiring_guide():
    """Generate wiring guide for L298N motor driver"""
    wiring_guide = """
🔌 RASPBERRY PI + L298N WIRING GUIDE
=====================================

L298N Motor Driver Connections:
--------------------------------
L298N Pin    -> Raspberry Pi Pin    -> Purpose
---------       ---------------       -------
VCC (5V-35V) -> External 6-12V       -> Motor power supply  
GND          -> Pin 6 (GND)          -> Ground
ENA          -> Pin 12 (GPIO 18)     -> Left motor PWM
IN1          -> Pin 18 (GPIO 24)     -> Left motor direction
IN2          -> Pin 16 (GPIO 23)     -> Left motor direction
ENB          -> Pin 35 (GPIO 19)     -> Right motor PWM  
IN3          -> Pin 40 (GPIO 21)     -> Right motor direction
IN4          -> Pin 38 (GPIO 20)     -> Right motor direction
5V           -> Pin 2 (5V)           -> Logic power (if needed)

DC Motors:
----------
Connect left motor to Motor A terminals
Connect right motor to Motor B terminals

Power Supply:
-------------
- Use separate 6-12V battery pack for motors
- Connect battery + to L298N VCC
- Connect battery - to L298N GND and Pi GND (common ground)
- Pi can be powered separately via USB or GPIO

Safety Notes:
-------------
⚠️  Always connect grounds together
⚠️  Don't exceed L298N voltage ratings (35V max)
⚠️  Add heat sink to L298N if using high current
⚠️  Use appropriate fuses for motor power

Test Commands:
--------------
# Test GPIO setup
gpio readall

# Test robot control
cd ~/chipurobo_mission_control
python3 raspberry_pi_robot.py
"""
    
    with open("pi_wiring_guide.txt", "w") as f:
        f.write(wiring_guide)
    
    print("✅ Created pi_wiring_guide.txt")
    print("   Open this file for detailed wiring instructions")

def main():
    """Main deployment function"""
    if len(sys.argv) < 2:
        print("Usage: python3 deploy_to_pi.py <pi_ip_address> [pi_username]")
        print("Example: python3 deploy_to_pi.py raspberrypi.local pi")
        print("Example: python3 deploy_to_pi.py 192.168.1.100")
        sys.exit(1)
    
    pi_ip = sys.argv[1]
    pi_user = sys.argv[2] if len(sys.argv) > 2 else "pi"
    
    # Check if required files exist
    required_files = [
        "raspberry_pi_robot.py",
        "robot_interface.py", 
        "robot_server.py",
        "test_integration.py"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("   Please run this from the tools/path_editor directory")
        sys.exit(1)
    
    # Deploy to Pi
    success = deploy_to_pi(pi_ip, pi_user)
    
    # Generate additional resources
    create_pi_service()
    setup_pi_wiring_guide()
    
    if success:
        print("\n🎉 Deployment Complete!")
        print("   Your Raspberry Pi is ready for robot missions!")
    else:
        print("\n⚠️ Deployment completed with issues")
        print("   Check error messages above and verify Pi hardware setup")

if __name__ == '__main__':
    main()