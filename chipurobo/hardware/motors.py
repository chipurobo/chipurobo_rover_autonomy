#!/usr/bin/env python3
"""
L298N Motor Driver for ChipuRobo
Professional motor control interface for DC motors
"""

from typing import Dict, Any
from .gpio_manager import GPIOPinManager

# Core imports with error handling
try:
    from gpiozero import PWMOutputDevice, OutputDevice
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False


class L298NMotorDriver:
    """L298N Motor Driver Interface for DC Motors with standardized GPIO pins"""
    
    def __init__(self, pwm_freq: int = 1000):
        """
        Initialize L298N motor driver with standardized pins
        
        Args:
            pwm_freq: PWM frequency in Hz
        """
        self.left_pins, self.right_pins = GPIOPinManager.get_motor_pins()
        self.pwm_freq = pwm_freq
        self.left_pwm = None
        self.right_pwm = None
        self.initialized = False
        
        if RPI_AVAILABLE:
            self.setup_gpio()
        else:
            print("🔧 Motor driver running in simulation mode")
    
    def setup_gpio(self) -> None:
        """Setup GPIO pins and PWM with gpiozero"""
        try:
            # Initialize left motor with gpiozero
            self.left_pwm = PWMOutputDevice(self.left_pins['pwm'], frequency=self.pwm_freq)
            self.left_in1 = OutputDevice(self.left_pins['in1'])
            self.left_in2 = OutputDevice(self.left_pins['in2'])
            
            # Initialize right motor with gpiozero
            self.right_pwm = PWMOutputDevice(self.right_pins['pwm'], frequency=self.pwm_freq)
            self.right_in1 = OutputDevice(self.right_pins['in1'])
            self.right_in2 = OutputDevice(self.right_pins['in2'])
            
            # Store direction control references
            self.left_dir_pins = {'in1': self.left_in1, 'in2': self.left_in2}
            self.right_dir_pins = {'in1': self.right_in1, 'in2': self.right_in2}
            
            self.initialized = True
            print("🔧 L298N Motor Driver initialized with gpiozero:")
            GPIOPinManager.print_pin_assignment()
            
        except Exception as e:
            print(f"❌ Motor driver setup failed: {e}")
    
    def set_motor_speed(self, motor: str, speed: float, direction: str) -> None:
        """
        Control individual motor
        
        Args:
            motor: 'left' or 'right'
            speed: 0.0 to 1.0 (percentage)
            direction: 'forward', 'backward', or 'stop'
        """
        if not self.initialized and RPI_AVAILABLE:
            return
            
        speed = max(0.0, min(1.0, abs(speed)))  # Clamp to 0-1
        
        if motor == 'left':
            pwm_device = self.left_pwm
            dir_pins = self.left_dir_pins
        else:
            pwm_device = self.right_pwm
            dir_pins = self.right_dir_pins
        
        if not RPI_AVAILABLE:
            print(f"🔧 {motor} motor: {direction} at {speed:.1%}")
            return
        
        # Set direction using gpiozero
        if direction == 'forward':
            dir_pins['in1'].on()
            dir_pins['in2'].off()
        elif direction == 'backward':
            dir_pins['in1'].off()
            dir_pins['in2'].on()
        else:  # stop
            dir_pins['in1'].off()
            dir_pins['in2'].off()
            speed = 0
        
        # Set speed using gpiozero PWM (value 0-1)
        if pwm_device:
            pwm_device.value = speed
    
    def drive_tank(self, left_speed: float, right_speed: float) -> None:
        """
        Tank drive control
        
        Args:
            left_speed: -1.0 to 1.0 (negative = backward)
            right_speed: -1.0 to 1.0 (negative = backward)
        """
        # Left motor
        if left_speed > 0:
            self.set_motor_speed('left', left_speed, 'forward')
        elif left_speed < 0:
            self.set_motor_speed('left', abs(left_speed), 'backward')
        else:
            self.set_motor_speed('left', 0, 'stop')
        
        # Right motor  
        if right_speed > 0:
            self.set_motor_speed('right', right_speed, 'forward')
        elif right_speed < 0:
            self.set_motor_speed('right', abs(right_speed), 'backward')
        else:
            self.set_motor_speed('right', 0, 'stop')
    
    def drive_arcade(self, forward_speed: float, turn_rate: float) -> None:
        """
        Arcade drive control
        
        Args:
            forward_speed: -1.0 to 1.0 (forward/backward)
            turn_rate: -1.0 to 1.0 (left/right turn)
        """
        # Mix arcade controls into tank drives
        left_speed = forward_speed + turn_rate
        right_speed = forward_speed - turn_rate
        
        # Normalize if any speed exceeds ±1.0
        max_speed = max(abs(left_speed), abs(right_speed))
        if max_speed > 1.0:
            left_speed /= max_speed
            right_speed /= max_speed
        
        self.drive_tank(left_speed, right_speed)
    
    def stop(self) -> None:
        """Stop all motors"""
        self.drive_tank(0, 0)
    
    def get_status(self) -> Dict[str, Any]:
        """Get motor driver status"""
        return {
            'initialized': self.initialized,
            'rpi_available': RPI_AVAILABLE,
            'pwm_frequency': self.pwm_freq,
            'pin_assignments': {
                'left_motor': self.left_pins,
                'right_motor': self.right_pins
            }
        }
    
    def cleanup(self) -> None:
        """Clean up GPIO resources"""
        if self.initialized:
            self.stop()
            # Close gpiozero devices
            if hasattr(self, 'left_pwm') and self.left_pwm:
                self.left_pwm.close()
            if hasattr(self, 'right_pwm') and self.right_pwm:
                self.right_pwm.close()
            if hasattr(self, 'left_in1') and self.left_in1:
                self.left_in1.close()
            if hasattr(self, 'left_in2') and self.left_in2:
                self.left_in2.close()
            if hasattr(self, 'right_in1') and self.right_in1:
                self.right_in1.close()
            if hasattr(self, 'right_in2') and self.right_in2:
                self.right_in2.close()
            print("🔧 Motor driver cleanup completed")