# ChipuRobo Path Planning & Mission Control System

A complete web-based field designer, path planner, and mission control system for autonomous robots, similar to FIRST Robotics trajectory planning tools.

## 🏗️ System Architecture

```
Web Interface (Port 8081)     Backend Server (Port 5001)     Robot Interface
┌─────────────────────────┐   ┌──────────────────────────┐   ┌─────────────────┐
│ • Field Designer        │──▶│ • Mission Storage        │◀──│ • Mission Loader│
│ • Path Planner          │   │ • Trajectory Generation  │   │ • Robot Control │
│ • Robot Configuration   │   │ • Robot Communication    │   │ • Hardware API  │
└─────────────────────────┘   └──────────────────────────┘   └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the System
```bash
cd /Users/kevinirungu/Desktop/chipurobo_rover_autonomy/tools/path_editor

# Start the robot backend server (Terminal 1)
python3 robot_server.py

# Start the web interface server (Terminal 2)  
python3 -m http.server 8081
```

### 2. Open Web Interface
Navigate to: **http://localhost:8081/web_editor.html**

### 3. Design Your Mission
1. **Configure Field**: Set field dimensions (default: 16.5ft × 8.2ft)
2. **Place Elements**: Use mode buttons to add obstacles 🚧, zones 🎪, start positions 🚀
3. **Create Path**: Switch to Path mode 🎯 and click waypoints
4. **Configure Robot**: Set physical parameters and motion limits
5. **Deploy**: Click "🚀 Deploy to Robot" to send mission to backend

### 4. Execute on Robot
```bash
# Test the integration
python3 test_integration.py

# Or integrate with your robot code
python3 robot_interface.py
```

## 📋 Features

### 🏟️ Field Designer
- **Configurable field dimensions** (feet)
- **Visual grid** with 1-foot intervals  
- **FIRST Robotics style** green field with white boundaries
- **Field elements**:
  - 🚧 Obstacles (brown squares)
  - 🎪 Scoring zones (orange circles)
  - 🚀 Starting positions (green arrows)

### 🎯 Path Planner  
- **Click-to-create** waypoints
- **Numbered waypoints** with directional arrows
- **Real-time coordinate** display (feet from field origin)
- **Export/Import** path files (.json)

### 🤖 Robot Configuration
- **Physical parameters**: Length, width (feet)
- **Motion limits**: Max speed, acceleration
- **Network settings**: Robot IP address
- **Live connection testing**

### 🔧 Backend Server
- **Mission storage** and retrieval
- **Trajectory generation** with robot constraints
- **RESTful API** for robot communication
- **Data persistence** (missions saved as JSON)

## 📁 File Structure

```
tools/path_editor/
├── web_editor.html          # Web-based mission planner UI
├── robot_server.py          # Backend server (Flask)
├── robot_interface.py       # Python API for robot integration
├── test_integration.py      # Integration testing script
├── robot_data/             # Mission storage directory
│   ├── missions/           # Deployed missions
│   └── configs/            # Robot configurations
└── README.md               # This file
```

## 🔌 API Endpoints

### Backend Server (Port 5001)
- `GET /status` - Server status and mission count
- `POST /deploy` - Deploy mission from web interface  
- `GET /mission/current` - Get currently deployed mission
- `GET /missions` - List all stored missions
- `GET /robot/config` - Get robot configuration
- `POST /path/generate` - Generate trajectory from waypoints

## 🎮 Usage Examples

### Web Interface Workflow
1. **Field Setup**: "📏 Update Field Size" → Place obstacles/zones
2. **Path Creation**: Select "🎯 Path" mode → Click waypoints  
3. **Robot Config**: Set dimensions, speed limits, IP address
4. **Connection Test**: "🔗 Test Connection" (should show ✅)
5. **Deployment**: "🚀 Deploy to Robot"

### Robot Integration
```python
from robot_interface import RobotMissionInterface

# Connect to mission control
robot = RobotMissionInterface()

# Load current mission
mission = robot.get_current_mission()
waypoints = robot.get_waypoints()
config = robot.get_robot_config()

# Generate trajectory  
trajectory = robot.generate_trajectory(waypoints)

# Execute on your robot hardware
for point in trajectory:
    # Move robot to point['x'], point['y']
    # At velocity point['velocity']  
    # With heading point['heading']
    pass
```

## 🔧 Integration with Robot Code

The system integrates with your existing robot modules:

```python
# In your main robot code
from tools.path_editor.robot_interface import RobotMissionInterface

class AutonomousMode:
    def __init__(self):
        self.mission_control = RobotMissionInterface()
        self.drivetrain = Drivetrain()  # Your robot's drivetrain
        self.odometry = Odometry()      # Your robot's odometry
        
    def run_autonomous(self):
        # Load mission from web interface
        waypoints = self.mission_control.get_waypoints()
        trajectory = self.mission_control.generate_trajectory(waypoints)
        
        # Execute trajectory
        for point in trajectory:
            self.drivetrain.drive_to_position(point['x'], point['y'])
```

## 🛠️ Configuration

### Field Settings
- Default: 16.5ft × 8.2ft (FRC field size)
- Configurable width/height
- 1-foot grid resolution
- Real-world coordinate system

### Robot Parameters
- **Length/Width**: Physical robot dimensions (feet)
- **Max Speed**: Maximum velocity (ft/s) 
- **Max Accel**: Maximum acceleration (ft/s²)
- **IP Address**: Network address for deployment

### Network Settings
- **Web Interface**: Port 8081
- **Backend Server**: Port 5001  
- **Robot Connection**: Configurable IP

## ✅ Fixed Issues
- ✅ **Clear Field button** now works properly
- ✅ **Robot connection** with backend server
- ✅ **Trajectory planning** with robot constraints  
- ✅ **Mission deployment** from web to robot
- ✅ **Real-world coordinates** in feet
- ✅ **CORS enabled** for web interface communication

## 🚀 Next Steps

1. **Test the system**: Create a field, path, and deploy to robot
2. **Integrate with hardware**: Connect robot_interface.py to your robot's drivetrain
3. **Customize trajectory generation**: Add more sophisticated path planning algorithms
4. **Add safety features**: Obstacle avoidance, collision detection
5. **Extend field elements**: Custom scoring zones, game-specific objects

## 📞 Troubleshooting

### Connection Issues
- Ensure backend server is running on port 5001
- Check robot IP address in configuration
- Verify firewall allows connections

### Field/Path Issues
- Click within white field boundaries
- Select correct mode before placing elements
- Check that waypoints form a valid path

### Mission Deployment
- Test connection first (🔗 button should show ✅)
- Ensure robot configuration is complete
- Check backend server logs for errors

---

**🤖 Ready for autonomous robot missions!** 

Open the web interface and start designing your robot's mission!