# Pipette MoveIt Configuration

MoveIt configuration package for standalone pipette motion planning and control.

## Overview

This package provides a complete MoveIt setup for the pipette tool, enabling motion planning, visualization, and RViz integration with the Motion Planning plugin. It's designed for standalone pipette control with GUI sliders and hardware integration.

### Features
- **MoveIt Motion Planning**: OMPL-based path planning for pipette joints
- **RViz Integration**: Motion Planning plugin with interactive markers
- **Hardware Control**: Integrates with pipette_driver action server
- **GUI Control**: Joint sliders for manual position control
- **Predefined States**: Common pipette positions (retracted, extended, etc.)
- **Real-time Visualization**: Live robot model updates

## Package Contents

### Configuration Files
- **`config/kinematics.yaml`** - Kinematics solver configuration
- **`config/joint_limits.yaml`** - Joint velocity and acceleration limits
- **`config/moveit_controllers.yaml`** - Controller interface configuration
- **`srdf/pipette.srdf`** - Semantic robot description with planning groups

### Launch Files
- **`launch/driver_with_rviz.launch.py`** - Complete setup with RViz + hardware control + GUI sliders

### RViz Configuration
- **`rviz/moveit.rviz`** - Pre-configured RViz with Motion Planning plugin

## Quick Start

### Prerequisites
```bash
# Install MoveIt and dependencies
sudo apt install ros-humble-moveit ros-humble-moveit-planners-ompl ros-humble-moveit-simple-controller-manager

# Build required packages
cd /path/to/your/workspace
colcon build --packages-select pipette_driver pipette_description pipette_moveit_config
source install/setup.bash
```

### Launch Complete System
```bash
# Launch with hardware control and GUI sliders
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Custom serial port
ros2 launch pipette_moveit_config driver_with_rviz.launch.py serial_port:=/dev/ttyUSB0
```

**What you get:**
- RViz with Motion Planning plugin
- Joint sliders for manual control
- Real-time hardware control
- 3D robot visualization

## Usage

### Manual Control with GUI Sliders
1. **Launch the system**:
   ```bash
   ros2 launch pipette_moveit_config driver_with_rviz.launch.py
   ```

2. **Use Joint State Publisher GUI**:
   - Move `plunger_joint` slider (0-10mm range)
   - Move `tip_eject_joint` slider (0-5mm range)
   - Robot model updates in RViz in real-time
   - Hardware moves correspondingly

3. **Monitor hardware response**:
   - Arduino receives `SETPOSITION x y` commands
   - LED updates based on joint positions (if using LED test firmware)

### Motion Planning (Future Enhancement)
The package is set up for motion planning but currently optimized for direct control:

1. **Planning Group**: `pipette_tool` (contains both pipette joints)
2. **Predefined States**: 
   - `retracted` - Both joints at 0mm
   - `extended` - Plunger at 5mm, tip eject at 2mm

## Configuration Details

### Planning Group
```yaml
# In srdf/pipette.srdf
group name="pipette_tool":
  joints:
    - plunger_joint
    - tip_eject_joint
```

### Joint Limits
```yaml
# In config/joint_limits.yaml
plunger_joint:
  max_velocity: 0.005      # 5mm/s
  max_acceleration: 0.001  # 1mm/s²
  min_position: 0.0
  max_position: 0.010      # 10mm

tip_eject_joint:
  max_velocity: 0.002      # 2mm/s  
  max_acceleration: 0.001  # 1mm/s²
  min_position: 0.0
  max_position: 0.005      # 5mm
```

### Controller Integration
```yaml
# In config/moveit_controllers.yaml
pipette_controller:
  type: FollowJointTrajectory
  joints:
    - plunger_joint
    - tip_eject_joint
  action_ns: follow_joint_trajectory  # Connects to pipette_driver_node
```

## Launch Arguments

### driver_with_rviz.launch.py
- **`serial_port`** - Arduino serial port (default: `/tmp/ttyUR`)
- **`baudrate`** - Serial communication baud rate (default: `115200`)
- **`use_sim_time`** - Use simulation time (default: `false`)

### Usage Examples
```bash
# Default setup
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Custom hardware
ros2 launch pipette_moveit_config driver_with_rviz.launch.py serial_port:=/dev/ttyUSB0 baudrate:=9600

# With simulation time
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_sim_time:=true
```

## System Architecture

### Node Communication Flow
```
Joint Sliders (GUI) 
    ↓ /joint_states
joint_state_bridge_node
    ↓ /follow_joint_trajectory (action)
pipette_driver_node (namespace: pipette_controller)
    ↓ SETPOSITION commands (serial)
Arduino Hardware
```

### Key Nodes
1. **`joint_state_publisher_gui`** - Provides manual joint sliders
2. **`joint_state_bridge`** - Converts slider positions to trajectory actions
3. **`pipette_driver_node`** - Hardware interface with action server
4. **`robot_state_publisher`** - Publishes TF transforms for visualization
5. **`static_transform_publisher`** - Provides world→tool0 transform

## Troubleshooting

### MoveIt Can't Connect to Controllers
```bash
# Check if pipette_driver_node is running in correct namespace
ros2 node list | grep pipette_controller

# Verify action server is available
ros2 action list | grep follow_joint_trajectory

# Check controller configuration
ros2 param get /move_group moveit_simple_controller_manager
```

### Joint Sliders Don't Control Hardware
```bash
# Check if joint_state_bridge is running
ros2 node list | grep joint_state_bridge

# Verify joint states are being published
ros2 topic echo /joint_states

# Test trajectory action directly
ros2 action send_goal /pipette_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "..."
```

### RViz Motion Planning Plugin Issues
```bash
# Verify planning group exists
ros2 service call /move_group/get_planning_scene moveit_msgs/srv/GetPlanningScene "{}"

# Check SRDF loading
ros2 param get /move_group robot_description_semantic

# Restart with debug logging
ros2 launch pipette_moveit_config driver_with_rviz.launch.py --ros-args --log-level debug
```

### Hardware Not Responding
```bash
# Test serial communication first
ros2 run pipette_driver serial_terminal

# Check pipette driver logs
ros2 launch pipette_moveit_config driver_with_rviz.launch.py 2>&1 | grep pipette_driver

# Verify Arduino firmware matches expected commands
# Should respond to: SETPOSITION 5 2
```

## Development

### Adding New Predefined States
Edit `srdf/pipette.srdf`:
```xml
<group_state name="my_new_state" group="pipette_tool">
    <joint name="plunger_joint" value="0.008"/>
    <joint name="tip_eject_joint" value="0.003"/>
</group_state>
```

### Modifying Joint Limits
Edit `config/joint_limits.yaml` and update URDF accordingly:
```yaml
plunger_joint:
  max_position: 0.015  # Increase to 15mm
```

### Adding Motion Planning
The package is set up for motion planning. To enable:
1. Use Motion Planning plugin in RViz
2. Set planning group to "pipette_tool"
3. Set goal states and plan/execute

## Integration Notes

### Standalone vs UR Robot
- **This package**: Standalone pipette control
- **ur5e_pipette_moveit_config**: Complete UR5e + pipette system

### Working with UR Tool Communication
When using with actual UR robot:
```bash
# Terminal 1: Pipette MoveIt
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Terminal 2: UR tool communication
ros2 run ur_robot_driver tool_communication.py --ros-args -p robot_ip:=192.168.1.101
```

## Related Packages

This package depends on:
- **`pipette_driver`** - Hardware control and action server
- **`pipette_description`** - URDF robot description

This package is used by:
- **`ur5e_pipette_moveit_config`** - Combined UR5e + pipette planning

## Files Overview

### Core Configuration
- `srdf/pipette.srdf` - Planning groups and predefined states
- `config/moveit_controllers.yaml` - Controller interface setup
- `config/kinematics.yaml` - Kinematics solver configuration
- `config/joint_limits.yaml` - Motion limits and safety parameters

### Launch Files
- `launch/driver_with_rviz.launch.py` - Complete system with GUI control

### Visualization
- `rviz/moveit.rviz` - Pre-configured RViz with Motion Planning plugin