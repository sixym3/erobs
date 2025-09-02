# Pipette MoveIt Configuration

MoveIt configuration package for standalone pipette motion planning and control with real hardware integration.

## Overview

This package provides a complete MoveIt setup for the pipette tool, enabling motion planning, visualization, and RViz integration with the Motion Planning plugin. It uses an **action-server based architecture** for direct hardware control without ros2_control complexity.

### Features
- **MoveIt Motion Planning**: OMPL-based path planning for pipette joints
- **RViz Integration**: Motion Planning plugin with interactive markers and drag-and-drop control
- **Action Server Integration**: Direct FollowJointTrajectory action server communication
- **Fake Hardware Support**: Test without Arduino using simulated hardware
- **Real Hardware Control**: Direct Arduino communication with joint state feedback
- **Percentage Scaling**: Uses [0,1) range matching Arduino firmware expectations
- **Manual Control Option**: GUI sliders for direct hardware control
- **Action Server Discovery**: Robust startup without race conditions

## Package Contents

### Configuration Files
- **`config/kinematics.yaml`** - Kinematics solver configuration
- **`config/joint_limits.yaml`** - Joint velocity/acceleration limits ([0,1) scaling)
- **`config/moveit_controllers.yaml`** - MoveIt action-server interface configuration
- **`srdf/pipette.srdf`** - Semantic robot description with planning groups

### Launch Files
- **`launch/driver_with_rviz.launch.py`** - Complete MoveIt setup with Motion Planning + hardware control
- **`launch/slider_control.launch.py`** - Manual control with GUI sliders (alternative to MoveIt)

### RViz Configuration
- **`rviz/moveit.rviz`** - Pre-configured RViz with Motion Planning plugin

## Quick Start

### Prerequisites
```bash
# Install MoveIt dependencies
sudo apt install ros-humble-moveit ros-humble-moveit-planners-ompl 
sudo apt install ros-humble-joint-state-publisher-gui

# Build required packages
cd /path/to/your/workspace
colcon build --packages-select pipette_driver pipette_description pipette_moveit_config
source install/setup.bash
```

## Usage Options

### 1. MoveIt Motion Planning (Recommended)
Complete MoveIt interface with motion planning capabilities:

```bash
# With fake hardware (no Arduino needed)
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_fake_hardware:=true

# With real Arduino hardware
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Custom serial port
ros2 launch pipette_moveit_config driver_with_rviz.launch.py serial_port:=/dev/ttyACM0
```

**What you get:**
- RViz with MoveIt Motion Planning plugin
- Interactive markers for drag-and-drop control  
- Real-time hardware control with [0,1) percentage scaling
- Motion planning and execution capabilities
- Joint state feedback from actual hardware

### 2. Manual GUI Control (Alternative)
Simple slider-based control without motion planning:

```bash
# Manual control with fake hardware
ros2 launch pipette_moveit_config slider_control.launch.py use_fake_hardware:=true

# Manual control with real hardware
ros2 launch pipette_moveit_config slider_control.launch.py
```

**What you get:**
- RViz visualization with robot model
- Joint sliders for direct manual control
- Real-time position feedback
- No motion planning (direct control only)

## MoveIt Motion Planning Usage

### Using the Motion Planning Plugin

1. **Launch the MoveIt system**:
   ```bash
   ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_fake_hardware:=true
   ```

2. **In RViz Motion Planning Plugin**:
   - **Planning Group**: Select "pipette_tool" 
   - **Interactive Markers**: Drag orange spheres to set target positions
   - **Goal State**: Set target joint values manually
   - **Plan**: Click "Plan" to generate motion plan
   - **Execute**: Click "Execute" to move hardware
   - **Values**: All positions in [0,1) percentage range

3. **Planning Group Definition**:
   ```yaml
   # Planning group "pipette_tool" includes:
   joints:
     - plunger_joint    # [0,1) range
     - tip_eject_joint  # [0,1) range
   ```

### Testing MoveIt Commands

```bash
# Start MoveIt system
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_fake_hardware:=true

# In another terminal, test direct action server
ros2 action send_goal /follow_joint_trajectory control_msgs/action/FollowJointTrajectory \
"{trajectory: {
  joint_names: ['plunger_joint', 'tip_eject_joint'], 
  points: [{
    positions: [0.5, 0.3], 
    time_from_start: {sec: 2}
  }]
}}"
```

## Launch Arguments

### driver_with_rviz.launch.py
- **`serial_port`** - Arduino serial port (default: `/dev/ttyUR`)
- **`baudrate`** - Serial communication baud rate (default: `115200`)
- **`use_fake_hardware`** - Use fake hardware for testing (default: `false`)
- **`use_sim_time`** - Use simulation time (default: `false`)

### slider_control.launch.py  
- **`serial_port`** - Arduino serial port (default: `/dev/ttyUR`)
- **`baudrate`** - Serial communication baud rate (default: `115200`)
- **`use_fake_hardware`** - Use fake hardware for testing (default: `false`)
- **`use_sim_time`** - Use simulation time (default: `false`)

### Usage Examples
```bash
# MoveIt with fake hardware (testing)
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_fake_hardware:=true

# MoveIt with real Arduino
ros2 launch pipette_moveit_config driver_with_rviz.launch.py serial_port:=/dev/ttyACM0

# Manual sliders with fake hardware
ros2 launch pipette_moveit_config slider_control.launch.py use_fake_hardware:=true

# Manual sliders with real hardware
ros2 launch pipette_moveit_config slider_control.launch.py
```

## System Architecture

### Action-Server Based Control
This package uses a **simplified action-server architecture** instead of ros2_control:

```
MoveIt Motion Planning (RViz)
    ↓ /follow_joint_trajectory (action)
pipette_driver_node (action server)
    ↓ SETPOSITION commands (serial) + joint state publishing
Arduino Hardware
    ↓ Position feedback
pipette_driver_node
    ↓ /joint_states topic (10Hz)
RViz Visualization
```

### Key Nodes
1. **`move_group`** - MoveIt motion planning node
2. **`pipette_driver_node`** - Action server + hardware interface + joint state publisher
3. **`robot_state_publisher`** - Publishes TF transforms for visualization  
4. **`rviz2_moveit`** - RViz with Motion Planning plugin
5. **`joint_state_bridge`** - Converts GUI slider positions to action goals (slider_control only)

### No ros2_control Complexity
- **Direct action server**: No controller manager or ros2_control overhead
- **Simplified startup**: No controller spawning or hardware interface loading
- **Real joint states**: Direct publishing from hardware feedback
- **Robust discovery**: Action client waits for server availability

## Configuration Details

### Joint Limits ([0,1) Percentage Scaling)
```yaml
# In config/joint_limits.yaml
plunger_joint:
  max_velocity: 0.5        # 50% per second
  max_acceleration: 0.1    # 10% per second²
  min_position: 0.0
  max_position: 0.999      # [0,1) percentage range

tip_eject_joint:
  max_velocity: 0.4        # 40% per second  
  max_acceleration: 0.1    # 10% per second²
  min_position: 0.0
  max_position: 0.999      # [0,1) percentage range
```

### MoveIt Controller Integration (Action-Server)
```yaml
# In config/moveit_controllers.yaml
moveit_simple_controller_manager:
  controller_names:
    - pipette_controller

  pipette_controller:
    type: FollowJointTrajectory
    joints:
      - plunger_joint
      - tip_eject_joint
    action_ns: follow_joint_trajectory  # Direct action server connection
    default: true
```

## Testing and Validation

### Test Fake Hardware Mode
```bash
# Start system with fake hardware
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_fake_hardware:=true

# Verify nodes are running
ros2 node list
# Should see: move_group, pipette_driver_node, robot_state_publisher, rviz2

# Check joint states publishing
ros2 topic echo /joint_states
# Should see plunger_joint and tip_eject_joint positions updating

# Test action server
ros2 action list
# Should see: /follow_joint_trajectory

# Test action call
ros2 action send_goal /follow_joint_trajectory control_msgs/action/FollowJointTrajectory \
"{trajectory: {joint_names: ['plunger_joint', 'tip_eject_joint'], points: [{positions: [0.5, 0.3], time_from_start: {sec: 1}}]}}"
```

### Test Real Hardware Integration  
```bash
# Connect Arduino to /dev/ttyUR (or your port)
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Check hardware connection logs
ros2 node info pipette_driver_node

# Test serial communication
ros2 topic echo /joint_states
# Should show actual hardware positions, not just commanded positions
```

### Test Manual Control
```bash
# Start slider control
ros2 launch pipette_moveit_config slider_control.launch.py use_fake_hardware:=true

# Verify joint state bridge connection
ros2 node list | grep joint_state_bridge
# Should start after action server discovery completes

# Move GUI sliders - hardware should respond
# Joint states in RViz should update in real-time
```

## Troubleshooting

### MoveIt Can't Connect to Action Server
```bash
# Check if action server is available
ros2 action list | grep follow_joint_trajectory

# Check action server status
ros2 action info /follow_joint_trajectory

# Verify pipette_driver_node is running
ros2 node list | grep pipette_driver_node

# Check MoveIt controller configuration
ros2 param get /move_group moveit_simple_controller_manager
```

### Fake Hardware Not Working
```bash
# Check driver startup logs
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_fake_hardware:=true

# Should see:
# "Pipette driver started with FAKE HARDWARE - no Arduino needed"
# "FollowJointTrajectory action server ready"

# Verify joint states are being published
ros2 topic hz /joint_states
# Should show ~10 Hz publishing rate
```

### Joint State Bridge Connection Issues
```bash
# Check if bridge is waiting for action server
ros2 launch pipette_moveit_config slider_control.launch.py use_fake_hardware:=true

# Should see discovery messages:
# "Joint State Bridge starting - waiting for action server..."
# "Action server found and ready" 
# "Joint State Bridge ready - GUI sliders will control hardware"

# If stuck, check action server availability
ros2 action list
```

### Hardware Not Responding
```bash
# Test serial communication first
ls -la /dev/ttyUR  # or your port

# Check driver logs
ros2 run pipette_driver pipette_driver_node --ros-args -p serial_port:=/dev/ttyUR

# Verify Arduino firmware expects [0,1) percentage scaling
# Should respond to: SETPOSITION 0.5 0.3 (not mm values)

# Check permissions
sudo chmod 666 /dev/ttyUR  # if needed
```

### RViz Motion Planning Plugin Issues
```bash
# Verify planning group exists
ros2 service call /move_group/get_planning_scene moveit_msgs/srv/GetPlanningScene "{}"

# Check SRDF loading
ros2 param get /move_group robot_description_semantic

# Restart with debug logging
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_fake_hardware:=true --ros-args --log-level debug
```

## Development

### Adding New Planning Groups
Edit `srdf/pipette.srdf`:
```xml
<group name="pipette_tool">
    <joint name="plunger_joint"/>
    <joint name="tip_eject_joint"/>
</group>
```

### Modifying Joint Limits
Edit `config/joint_limits.yaml` using [0,1) percentage values:
```yaml
plunger_joint:
  max_velocity: 0.8    # 80% per second
  max_acceleration: 0.2 # 20% per second²
  min_position: 0.0
  max_position: 0.999  # Avoid exactly 1.0 (exclusive upper bound)
```

### Testing Changes
```bash
# Always test with fake hardware first
ros2 launch pipette_moveit_config driver_with_rviz.launch.py use_fake_hardware:=true

# Test action server integration
ros2 action send_goal /follow_joint_trajectory control_msgs/action/FollowJointTrajectory \
"{trajectory: {joint_names: ['plunger_joint', 'tip_eject_joint'], points: [{positions: [0.8, 0.2], time_from_start: {sec: 2}}]}}"

# Verify changes with real hardware
ros2 launch pipette_moveit_config driver_with_rviz.launch.py
```

## Integration Notes

### Standalone vs UR Robot System
- **This package**: Standalone pipette motion planning
- **ur5e_pipette_moveit_config**: Complete UR5e + pipette system (untested)

### Working with UR Tool Communication
When using with actual UR robot and tool communication:
```bash
# Terminal 1: Pipette MoveIt
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Terminal 2: UR tool communication (forwards /dev/ttyUR)
ros2 run ur_robot_driver tool_communication.py --ros-args -p robot_ip:=192.168.1.101
```

### Comparison: MoveIt vs Manual Control

| Feature | driver_with_rviz.launch.py | slider_control.launch.py |
|---------|---------------------------|--------------------------|
| Interface | MoveIt Motion Planning Plugin | GUI Sliders |
| Planning | ✅ OMPL motion planning | ❌ Direct control only |
| Complexity | Higher (full MoveIt stack) | Lower (simple GUI) |
| Use Case | Motion planning, complex trajectories | Testing, manual operation |
| Learning Curve | Steeper (MoveIt knowledge) | Minimal (just sliders) |

## Related Packages

This package depends on:
- **`pipette_driver`** - Action server and hardware interface
- **`pipette_description`** - URDF robot description

This package is used by:
- **`ur5e_pipette_moveit_config`** - Combined UR5e + pipette planning (needs testing)

## Files Overview

### Core Configuration
- `srdf/pipette.srdf` - Planning groups and semantic description
- `config/moveit_controllers.yaml` - Action server interface setup
- `config/kinematics.yaml` - Kinematics solver configuration  
- `config/joint_limits.yaml` - Motion limits and safety parameters

### Launch Files
- `launch/driver_with_rviz.launch.py` - Complete MoveIt system with Motion Planning GUI
- `launch/slider_control.launch.py` - Simple manual control with GUI sliders

### Visualization
- `rviz/moveit.rviz` - Pre-configured RViz with Motion Planning plugin

## Performance Notes

- **Fake hardware mode**: Instant response, good for testing algorithms
- **Real hardware mode**: Limited by Arduino communication speed (~100Hz max)
- **Joint state publishing**: 10Hz rate provides smooth visualization
- **Action server discovery**: Robust startup without artificial delays