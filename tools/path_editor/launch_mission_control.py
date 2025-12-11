#!/usr/bin/env python3
"""
ChipuRobo Mission Control Launcher
Starts both the web interface server and robot backend server automatically
"""

import subprocess
import time
import os
import sys
import signal
import threading
from pathlib import Path

class MissionControlLauncher:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.web_server_process = None
        self.backend_server_process = None
        self.running = False
        
    def start_web_server(self):
        """Start the web interface server"""
        print("🌐 Starting web interface server on port 8081...")
        try:
            os.chdir(self.script_dir)
            self.web_server_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", "8081"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            print("✅ Web interface server started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            return False
    
    def start_backend_server(self):
        """Start the robot backend server"""
        print("🤖 Starting robot backend server on port 5001...")
        try:
            backend_script = self.script_dir / "robot_server.py"
            self.backend_server_process = subprocess.Popen(
                ["/usr/bin/python3", str(backend_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            print("✅ Robot backend server started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start backend server: {e}")
            return False
    
    def check_servers(self):
        """Check if servers are still running"""
        web_running = self.web_server_process and self.web_server_process.poll() is None
        backend_running = self.backend_server_process and self.backend_server_process.poll() is None
        return web_running, backend_running
    
    def stop_servers(self):
        """Stop both servers"""
        print("\n🛑 Stopping servers...")
        
        if self.web_server_process:
            try:
                os.killpg(os.getpgid(self.web_server_process.pid), signal.SIGTERM)
                self.web_server_process.wait(timeout=5)
                print("✅ Web server stopped")
            except Exception as e:
                print(f"⚠️ Error stopping web server: {e}")
        
        if self.backend_server_process:
            try:
                os.killpg(os.getpgid(self.backend_server_process.pid), signal.SIGTERM)
                self.backend_server_process.wait(timeout=5)
                print("✅ Backend server stopped")
            except Exception as e:
                print(f"⚠️ Error stopping backend server: {e}")
        
        self.running = False
    
    def start_all(self):
        """Start both servers and monitor them"""
        print("🚀 ChipuRobo Mission Control Launcher")
        print("=" * 50)
        
        # Start servers
        web_started = self.start_web_server()
        time.sleep(2)  # Give web server time to start
        
        backend_started = self.start_backend_server()
        time.sleep(3)  # Give backend server time to start
        
        if not web_started or not backend_started:
            print("❌ Failed to start servers. Stopping any running processes...")
            self.stop_servers()
            return False
        
        self.running = True
        
        print("\n🎉 SYSTEM READY!")
        print("📱 Web Interface: http://localhost:8081/web_editor.html")
        print("🔧 Backend API:   http://localhost:5001/status")
        print("\n💡 Usage:")
        print("1. Open the web interface URL in your browser")
        print("2. Design your field and create waypoints") 
        print("3. Configure robot parameters")
        print("4. Test connection and deploy to robot")
        print("5. Use robot_interface.py to execute missions")
        print("\n⌨️  Press Ctrl+C to stop all servers")
        
        # Monitor servers
        try:
            while self.running:
                web_running, backend_running = self.check_servers()
                
                if not web_running and self.running:
                    print("❌ Web server stopped unexpectedly!")
                    break
                
                if not backend_running and self.running:
                    print("❌ Backend server stopped unexpectedly!")
                    break
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\n📋 Received stop signal...")
        
        self.stop_servers()
        return True

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n📋 Stopping ChipuRobo Mission Control...")
    sys.exit(0)

def main():
    """Main launcher function"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if we're in the right directory
    script_dir = Path(__file__).parent
    web_editor_file = script_dir / "web_editor.html"
    robot_server_file = script_dir / "robot_server.py"
    
    if not web_editor_file.exists():
        print(f"❌ Error: web_editor.html not found in {script_dir}")
        print("   Please run this script from the tools/path_editor directory")
        sys.exit(1)
    
    if not robot_server_file.exists():
        print(f"❌ Error: robot_server.py not found in {script_dir}")
        print("   Please run this script from the tools/path_editor directory")
        sys.exit(1)
    
    # Start the launcher
    launcher = MissionControlLauncher()
    success = launcher.start_all()
    
    if success:
        print("\n✅ ChipuRobo Mission Control stopped successfully")
    else:
        print("\n❌ ChipuRobo Mission Control stopped with errors")
        sys.exit(1)

if __name__ == '__main__':
    main()