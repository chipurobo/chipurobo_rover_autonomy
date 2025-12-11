#!/bin/bash
# ChipuRobo Mission Control - Quick Launcher
# Simply run: ./start.sh

echo "🚀 Starting ChipuRobo Mission Control System..."
echo ""

cd "$(dirname "$0")"

# Check if required files exist
if [ ! -f "web_editor.html" ]; then
    echo "❌ Error: web_editor.html not found!"
    exit 1
fi

if [ ! -f "robot_server.py" ]; then
    echo "❌ Error: robot_server.py not found!"
    exit 1
fi

# Run the Python launcher
/usr/bin/python3 launch_mission_control.py