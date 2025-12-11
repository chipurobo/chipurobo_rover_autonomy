#!/usr/bin/env python3
"""
Integration example showing how to integrate the path planner with actual robot code
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from robot_interface import RobotMissionInterface

# Import Raspberry Pi robot modules
try:
    from raspberry_pi_robot import RaspberryPiRobot
    print("✅ Raspberry Pi robot modules imported successfully")
    robot_modules_available = True
except ImportError as e:
    print(f"⚠️ Raspberry Pi robot modules not available: {e}")
    print("   This is normal if running without Raspberry Pi hardware")
    robot_modules_available = False

class RobotMissionController:
    def __init__(self):
        self.mission_interface = RobotMissionInterface()
        self.current_trajectory = None
        
        if robot_modules_available:
            # Initialize Raspberry Pi robot with default configuration
            self.robot = RaspberryPiRobot()
            print("🤖 Raspberry Pi robot hardware initialized")
        else:
            self.robot = None
            print("🔧 Running in simulation mode (no hardware)")
    
    def load_mission(self):
        """Load mission from mission control server"""
        print("\n📥 Loading mission from server...")
        
        summary = self.mission_interface.get_mission_summary()
        
        if not summary.get('ready_for_execution'):
            print("❌ Mission not ready. Deploy a mission from web interface first.")
            return False
        
        # Get waypoints and generate trajectory
        waypoints = self.mission_interface.get_waypoints()
        if not waypoints:
            print("❌ No waypoints found")
            return False
        
        # Generate trajectory with robot constraints
        self.current_trajectory = self.mission_interface.generate_trajectory(waypoints)
        
        if not self.current_trajectory:
            print("❌ Failed to generate trajectory")
            return False
        
        print("✅ Mission loaded successfully!")
        return True
    
    def execute_mission(self):
        """Execute the loaded mission"""
        if not self.current_trajectory:
            print("❌ No trajectory loaded. Load a mission first.")
            return False
        
        print(f"\n🚀 Executing mission with {len(self.current_trajectory)} trajectory points")
        
        if robot_modules_available:
            # Execute with real hardware
            return self._execute_real_robot()
        else:
            # Simulate execution
            return self._simulate_execution()
    
    def _execute_real_robot(self):
        """Execute trajectory on Raspberry Pi robot hardware"""
        print("🤖 Executing on Raspberry Pi robot hardware...")
        
        try:
            # Execute trajectory using Raspberry Pi robot
            success = self.robot.execute_trajectory(self.current_trajectory)
            
            if success:
                print("✅ Mission executed successfully!")
                return True
            else:
                print("❌ Mission execution failed!")
                return False
                
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            return False
    
    def _simulate_execution(self):
        """Simulate mission execution for testing"""
        print("🎮 Simulating mission execution...")
        
        for i, point in enumerate(self.current_trajectory):
            print(f"   Step {i+1}/{len(self.current_trajectory)}: "
                  f"Move to ({point['x']:.1f}ft, {point['y']:.1f}ft) "
                  f"at {point['velocity']:.1f} ft/s, heading {point['heading']:.1f}°")
        
        print("✅ Simulation completed successfully!")
        return True
    
    def get_robot_status(self):
        """Get current robot status"""
        if robot_modules_available and self.robot:
            # Get real status from Raspberry Pi robot
            try:
                status = self.robot.get_status()
                status['mission_loaded'] = self.current_trajectory is not None
                
                print(f"🤖 Raspberry Pi Robot Status:")
                print(f"   Position: ({status['position']['x']:.1f}, {status['position']['y']:.1f}) ft")
                print(f"   Heading: {status['position']['heading']:.1f}°")
                print(f"   Hardware: {status['hardware']}")
                print(f"   Motor Driver: L298N {'✅ OK' if status['initialized'] else '❌ ERROR'}")
                print(f"   Mission Loaded: {'✅' if status['mission_loaded'] else '❌'}")
                
                return status
            except Exception as e:
                print(f"⚠️ Error getting robot status: {e}")
                return {'hardware_connected': False, 'error': str(e)}
        else:
            return {
                'position': {'x': 0.0, 'y': 0.0, 'heading': 0.0},
                'velocity': {'linear': 0.0, 'angular': 0.0},
                'mission_loaded': self.current_trajectory is not None,
                'hardware_connected': False,
                'simulation_mode': True,
                'platform': 'raspberry_pi_simulation'
            }

def main():
    """Main function demonstrating the full workflow"""
    print("🚀 ChipuRobo Mission Controller")
    print("=" * 50)
    
    # Create mission controller
    controller = RobotMissionController()
    
    # Check robot status
    print("\n📊 Robot Status Check:")
    status = controller.get_robot_status()
    
    # Load mission from server
    print("\n📥 Mission Loading:")
    mission_loaded = controller.load_mission()
    
    if mission_loaded:
        print("\n🚀 Mission Execution:")
        controller.execute_mission()
    else:
        print("\n💡 Next Steps:")
        print("1. Open the web interface at http://localhost:8081/web_editor.html")
        print("2. Design your field and create waypoints")
        print("3. Configure robot parameters")
        print("4. Click 'Test Connection' to verify server connection")
        print("5. Click 'Deploy to Robot' to send the mission")
        print("6. Run this script again to execute the mission")

if __name__ == '__main__':
    main()