#!/usr/bin/env python3
"""
Motor Encoder Interface for ChipuRobo
Built-in motor encoder interface (Hall effect encoders in DC motors)
"""

import time
import math
import threading
from typing import Dict, Any

# Core imports with error handling
try:
    from gpiozero import Button
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False


class MotorEncoder:
    """Built-in motor encoder interface (Hall effect encoders in DC motors)"""
    
    def __init__(self, pin_a: int, pin_b: int, pulses_per_revolution: int = 11, 
                 wheel_diameter: float = 4.0, gear_ratio: float = 1.0):
        """
        Initialize motor encoder
        
        Args:
            pin_a, pin_b: GPIO pins for encoder channels A and B
            pulses_per_revolution: PPR of encoder (typically 11-40 for geared motors)
            wheel_diameter: Wheel diameter in inches
            gear_ratio: Motor gearbox ratio (if applicable)
        """
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.ppr = pulses_per_revolution
        self.wheel_diameter = wheel_diameter
        self.gear_ratio = gear_ratio
        self.wheel_circumference = math.pi * wheel_diameter
        
        # Thread-safe counters
        self.count = 0
        self.count_lock = threading.Lock()
        self.last_time = time.time()
        self.velocity = 0.0  # inches per second
        self.active = False
        
        if RPI_AVAILABLE:
            self.setup_gpio()
        else:
            print(f"🔄 Encoder (simulation): Pin A={pin_a}, Pin B={pin_b}")
    
    def setup_gpio(self) -> None:
        """Setup GPIO pins and interrupts using gpiozero"""
        try:
            # Use gpiozero Button for encoder channels with pull-up
            self.channel_a = Button(self.pin_a, pull_up=True, bounce_time=0.001)
            self.channel_b = Button(self.pin_b, pull_up=True, bounce_time=0.001)
            
            # Set up callbacks for both edges (press and release)
            self.channel_a.when_pressed = self._encoder_callback_pressed
            self.channel_a.when_released = self._encoder_callback_released
            
            self.active = True
            print(f"🔄 Encoder initialized with gpiozero: Pin A={self.pin_a}, Pin B={self.pin_b}")
        except Exception as e:
            print(f"❌ Encoder setup failed: {e}")
    
    def _encoder_callback_pressed(self) -> None:
        """Callback for channel A pressed (falling edge)"""
        self._process_encoder_pulse()
    
    def _encoder_callback_released(self) -> None:
        """Callback for channel A released (rising edge)"""
        self._process_encoder_pulse()
    
    def _process_encoder_pulse(self) -> None:
        """Process encoder pulse and determine direction"""
        if not self.active:
            return
            
        current_time = time.time()
        dt = current_time - self.last_time
        
        with self.count_lock:
            # Read both pins to determine direction using gpiozero
            pin_a_state = not self.channel_a.is_pressed  # Button pressed = low signal
            pin_b_state = not self.channel_b.is_pressed
            
            # Quadrature encoding - determine direction
            if pin_a_state == pin_b_state:
                self.count += 1  # Forward
            else:
                self.count -= 1  # Backward
            
            # Calculate velocity
            if dt > 0.001:  # Avoid division by zero
                pulse_rate = 1.0 / dt  # pulses per second
                self.velocity = (pulse_rate / self.ppr) * self.wheel_circumference
        
        self.last_time = current_time
    
    def get_distance(self) -> float:
        """Get distance traveled in inches (thread-safe)"""
        with self.count_lock:
            revolutions = self.count / self.ppr
            return revolutions * self.wheel_circumference
    
    def get_velocity(self) -> float:
        """Get current velocity in inches/second"""
        return self.velocity
    
    def get_count(self) -> int:
        """Get raw encoder count"""
        with self.count_lock:
            return self.count
    
    def reset(self) -> None:
        """Reset encoder count"""
        with self.count_lock:
            self.count = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get encoder status"""
        return {
            'active': self.active,
            'pin_a': self.pin_a,
            'pin_b': self.pin_b,
            'ppr': self.ppr,
            'wheel_diameter': self.wheel_diameter,
            'current_count': self.get_count(),
            'distance_inches': self.get_distance(),
            'velocity_ips': self.get_velocity(),
            'rpi_available': RPI_AVAILABLE
        }
    
    def cleanup(self) -> None:
        """Clean up GPIO resources"""
        self.active = False
        if RPI_AVAILABLE:
            try:
                if hasattr(self, 'channel_a') and self.channel_a:
                    self.channel_a.close()
                if hasattr(self, 'channel_b') and self.channel_b:
                    self.channel_b.close()
            except Exception:
                pass