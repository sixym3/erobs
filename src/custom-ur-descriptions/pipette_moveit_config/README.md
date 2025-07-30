# Pipette MoveIt Configuration

MoveIt configuration package for standalone pipette motion planning and control with real hardware integration.

## Overview

This package provides a complete MoveIt setup for the pipette tool, enabling motion planning, visualization, and RViz integration with the Motion Planning plugin. It's designed for standalone pipette control using **[0,1) percentage scaling** for real hardware control.

### Features
- **MoveIt Motion Planning**: OMPL-based path planning for pipette joints
- **RViz Integration**: Motion Planning plugin with interactive markers and drag-and-drop control
- **Real Hardware Control**: ros2_control integration with pipette hardware interface
- **Percentage Scaling**: Uses [0,1) range matching Arduino firmware expectations
- **Predefined States**: Common pipette positions (retracted, extended, etc.)
- **Real-time Visualization**: Live robot model updates from hardware feedback

## Package Contents

### Configuration Files
- **`config/kinematics.yaml`** - Kinematics solver configuration
- **`config/joint_limits.yaml`** - Joint velocity/acceleration limits (**[0,1) scaling**)
- **`config/moveit_controllers.yaml`** - MoveIt-ros2_control interface configuration
- **`srdf/pipette.srdf`** - Semantic robot description with planning groups and predefined states

### Launch Files
- **`launch/driver_with_rviz.launch.py`** - Complete MoveIt setup with RViz Motion Planning + real hardware control

### RViz Configuration
- **`rviz/moveit.rviz`** - Pre-configured RViz with Motion Planning plugin

## Quick Start

### Prerequisites
```bash
# Install MoveIt and ros2_control dependencies
sudo apt install ros-humble-moveit ros-humble-moveit-planners-ompl 
sudo apt install ros-humble-controller-manager ros-humble-joint-trajectory-controller
sudo apt install ros-humble-joint-state-broadcaster

# Build required packages
cd /path/to/your/workspace
colcon build --packages-select pipette_driver pipette_description pipette_moveit_config
source install/setup.bash
```

### Launch Complete MoveIt System
```bash
# Launch with MoveIt Motion Planning and real hardware control
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Custom serial port (default is /dev/ttyUSB0)
ros2 launch pipette_moveit_config driver_with_rviz.launch.py serial_port:=/dev/ttyACM0
```

**What you get:**
- RViz with MoveIt Motion Planning plugin
- Interactive markers for drag-and-drop control
- Real-time hardware control with [0,1) percentage scaling
- Motion planning and execution capabilities
- 3D robot visualization with live feedback

## Usage

### MoveIt Motion Planning Interface
1. **Launch the MoveIt system**:
   ```bash
   ros2 launch pipette_moveit_config driver_with_rviz.launch.py
   ```

2. **Use MoveIt Motion Planning Plugin in RViz**:
   - **Planning Group**: Select "pipette_tool"
   - **Interactive Markers**: Drag orange balls to set target positions
   - **Predefined States**: Use buttons for common positions
   - **Plan & Execute**: Click "Plan" then "Execute" to move hardware
   - **Real-time Control**: Values are in [0,1) percentage range

3. **Predefined States Available**:
   - **`retracted`** - Both joints at 0% (fully retracted)
   - **`plunger_extended`** - Plunger at 80%, tip at 0%
   - **`tip_ejected`** - Plunger at 0%, tip at 80%
   - **`both_extended`** - Plunger at 50%, tip at 40%

4. **Hardware Communication**:
   - Arduino receives position commands in [0,1) percentage format
   - Real-time position feedback via ros2_control
   - LED control available via separate topics

## Configuration Details

### Planning Group
```yaml
# In srdf/pipette.srdf
group name="pipette_tool":
  joints:
    - plunger_joint
    - tip_eject_joint
```

### Joint Limits ([0,1) Percentage Scaling)
```yaml
# In config/joint_limits.yaml
plunger_joint:
  max_velocity: 0.5        # 50% per second
  max_acceleration: 0.1    # 10% per second²
  min_position: 0.0
  max_position: 1.0        # [0,1) percentage range

tip_eject_joint:
  max_velocity: 0.4        # 40% per second  
  max_acceleration: 0.1    # 10% per second²
  min_position: 0.0
  max_position: 1.0        # [0,1) percentage range
```

### Controller Integration (ros2_control)
```yaml
# In config/moveit_controllers.yaml
pipette_controller:
  type: FollowJointTrajectory
  joints:
    - plunger_joint
    - tip_eject_joint
  action_ns: follow_joint_trajectory  # Connects via ros2_control

# In pipette_controllers.yaml (ros2_control)
pipette_controller:
  type: joint_trajectory_controller/JointTrajectoryController
  joints: [plunger_joint, tip_eject_joint]
```

## Launch Arguments

### driver_with_rviz.launch.py
- **`serial_port`** - Arduino serial port (default: `/dev/ttyUSB0`)
- **`baudrate`** - Serial communication baud rate (default: `115200`)
- **`use_sim_time`** - Use simulation time (default: `false`)

### Usage Examples
```bash
# Default setup
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Custom hardware port
ros2 launch pipette_moveit_config driver_with_rviz.launch.py serial_port:=/dev/ttyACM0

# Different baudrate
ros2 launch pipette_moveit_config driver_with_rviz.launch.py baudrate:=9600

# With simulation time
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_sim_time:=true
```

## System Architecture

### Node Communication Flow
```
MoveIt Motion Planning (RViz)
    ↓ /follow_joint_trajectory (action)
ros2_control (controller_manager)
    ↓ /pipette_controller/follow_joint_trajectory
joint_trajectory_controller
    ↓ position commands [0,1) range
pipette_hardware_interface
    ↓ SETPOSITION commands (serial)
Arduino Hardware
```

### Key Nodes
1. **`move_group`** - MoveIt motion planning node
2. **`controller_manager`** - ros2_control controller management
3. **`joint_state_broadcaster`** - Publishes joint states from hardware
4. **`pipette_controller`** - Joint trajectory controller for both joints
5. **`robot_state_publisher`** - Publishes TF transforms for visualization
6. **`rviz2_moveit`** - RViz with Motion Planning plugin

## Troubleshooting

### MoveIt Can't Connect to Controllers
```bash
# Check if ros2_control is running
ros2 node list | grep controller_manager

# Verify controllers are loaded and active
ros2 control list_controllers

# Check MoveIt controller configuration
ros2 param get /move_group moveit_simple_controller_manager

# Test trajectory action directly
ros2 action list | grep pipette_controller
```

### Hardware Interface Issues
```bash
# Check if hardware interface is loaded
ros2 control list_hardware_interfaces

# Verify joint states are being published
ros2 topic echo /joint_states

# Check controller status
ros2 control switch_controllers --activate pipette_controller
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

# Check hardware interface logs
ros2 launch pipette_moveit_config driver_with_rviz.launch.py 2>&1 | grep hardware

# Verify Arduino firmware uses [0,1) percentage scaling
# Should respond to: SETPOSITION 0.5 0.3 (not mm values)

# Check serial port permissions
ls -la /dev/ttyUSB* # or /dev/ttyACM*
sudo chmod 666 /dev/ttyUSB0  # if needed
```

## Development

### Adding New Predefined States
Edit `srdf/pipette.srdf` using [0,1) percentage values:
```xml
<group_state name="my_new_state" group="pipette_tool">
    <joint name="plunger_joint" value="0.75"/>
    <joint name="tip_eject_joint" value="0.25"/>
</group_state>
```

### Modifying Joint Limits
Edit `config/joint_limits.yaml` for [0,1) percentage scaling:
```yaml
plunger_joint:
  max_velocity: 0.8    # 80% per second
  max_acceleration: 0.2 # 20% per second²
```

### Motion Planning Usage
The package is fully configured for motion planning:
1. Launch: `ros2 launch pipette_moveit_config driver_with_rviz.launch.py`
2. In RViz: Set planning group to "pipette_tool"
3. Use interactive markers or predefined states
4. Click "Plan" then "Execute" to move real hardware

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