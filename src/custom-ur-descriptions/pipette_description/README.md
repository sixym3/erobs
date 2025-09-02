# Pipette Description

URDF description package for a pipette tool with geometry visualization and RViz integration.

## Overview

This package provides a URDF model of a pipette tool designed for integration with Universal Robot arms. The model includes joints for plunger and tip ejection control with RViz visualization support.

### Features
- **Pure URDF Description**: Clean robot description without ros2_control dependencies
- **Visual Model**: Pipette representation with STL meshes (easily replaceable with CAD)
- **Joint Definitions**: Two prismatic joints for plunger and tip ejection control
- **LED Visualization**: Visual representation of LED strip
- **RViz Integration**: Joint state publisher and visualization support
- **Action-based Control**: Works with pipette_driver action server
- **UR Robot Integration Ready**: Designed to attach to robot flanges

## Package Structure

```
pipette_description/
├── urdf/
│   ├── pipette.urdf.xacro          # Main entry point
│   └── pipette_macro.urdf.xacro    # Core pipette macro definition
├── meshes/
│   ├── visual/                     # High-quality visual meshes (your CAD here)
│   ├── collision/                  # Simplified collision meshes
│   └── README.md                   # CAD integration instructions
├── launch/
│   └── pipette_driver_display.launch.py  # Visualization + driver launch file
└── rviz/
    ├── pipette_demo.rviz           # RViz configuration for pipette display
    └── urdf.rviz                   # Basic URDF visualization
```

## Quick Start

### Prerequisites
```bash
# Ensure dependencies are installed
sudo apt install ros-humble-urdf-launch ros-humble-joint-state-publisher-gui
```

### Build the Package
```bash
cd /path/to/your/workspace
colcon build --packages-select pipette_description
source install/setup.bash
```

## Usage

### 1. URDF Visualization Only (No Hardware)
Test the URDF structure and visualization without hardware:

```bash
# Launch RViz with pipette model (no driver, no hardware)
ros2 launch pipette_description pipette_driver_display.launch.py start_driver:=false

# Expected behavior:
# - RViz opens with pipette model displayed
# - Joint State Publisher GUI with sliders for plunger_joint/tip_eject_joint
# - Moving sliders updates the model in RViz (visualization only)
# - No hardware communication
```

### 2. With Fake Hardware (Testing)
Test the complete system without real Arduino:

```bash
# Launch with fake hardware driver
ros2 launch pipette_description pipette_driver_display.launch.py use_fake_hardware:=true

# Expected behavior:
# - RViz visualization + Joint sliders
# - pipette_driver_node runs in fake hardware mode
# - Joint states published to /joint_states topic
# - Action server available for testing
# - No serial communication required
```

### 3. With Real Hardware
Launch with actual pipette hardware control:

```bash
# Launch with real Arduino hardware (default)
ros2 launch pipette_description pipette_driver_display.launch.py

# Custom serial port
ros2 launch pipette_description pipette_driver_display.launch.py serial_port:=/dev/ttyUSB0

# Expected behavior:
# - RViz visualization + Joint sliders  
# - pipette_driver_node connects to Arduino
# - Joint states reflect actual hardware positions
# - Moving sliders sends commands to Arduino
```

### Launch Arguments
- **`serial_port`** - Arduino serial port (default: `/dev/ttyUR`)
- **`baudrate`** - Serial communication baud rate (default: `115200`)
- **`use_fake_hardware`** - Use fake hardware for testing (default: `false`)
- **`start_driver`** - Whether to start pipette driver node (default: `false`)
- **`start_rviz`** - Whether to start RViz visualization (default: `true`)

## URDF Parameters

The pipette URDF accepts these xacro parameters:

```xml
<!-- Mounting configuration -->
<xacro:arg name="parent" default="tool0"/>

<!-- Physical properties -->
<xacro:arg name="pipette_mass" default="0.200"/>  # kg
<xacro:arg name="xyz" default="0 0 0"/>           # Position offset
<xacro:arg name="rpy" default="0 0 0"/>           # Orientation offset
```

## Joint Definitions

### Joint Limits (Hardware Range)
- **plunger_joint**: Prismatic joint, 0.0 to 1.0 (normalized range)
- **tip_eject_joint**: Prismatic joint, 0.0 to 1.0 (normalized range)

### Link Structure
```
parent (e.g., tool0)
└── pipette_base_link
    ├── plunger_link (controlled by plunger_joint)
    ├── tip_eject_link (controlled by tip_eject_joint)
    ├── pipette_tip_link (end effector reference)
    └── led_strip_link (visual only)
```

### Coordinate System
- **Plunger**: Positive movement = plunger depression (0.0 = retracted, 1.0 = fully depressed)
- **Tip Eject**: Positive movement = tip ejection (0.0 = tip retained, 1.0 = tip ejected)
- **Base Frame**: `pipette_base_link` at tool attachment point
- **End Effector**: `pipette_tip_link` at pipette tip

## Architecture Notes

### Action-Server Based Control
This package works with the **pipette_driver** action server architecture:

- **No ros2_control**: This URDF does not use ros2_control (removed for simplicity)
- **Action Server Integration**: Works with `FollowJointTrajectory` action server
- **Joint State Publishing**: pipette_driver publishes actual joint positions
- **MoveIt Compatible**: Works with MoveIt's action-based controller interface

### Integration with Larger Systems

#### Include in UR Robot URDF
```xml
<!-- Include in UR robot URDF -->
<xacro:include filename="$(find pipette_description)/urdf/pipette.urdf.xacro"/>

<!-- Attach to robot tool flange -->
<xacro:pipette parent="tool0" 
               pipette_mass="0.200"
               xyz="0 0 0.05"
               rpy="0 0 0"/>
```

#### Used by MoveIt Configuration
This package is referenced by:
- `pipette_moveit_config` - Standalone pipette motion planning
- `ur5e_pipette_moveit_config` - Combined UR5e + pipette system

## CAD Integration

### Current State: Placeholder Geometry
The URDF currently uses simple geometric shapes (cylinders) as placeholders.

### Integrating Your CAD Files

1. **Export your CAD model**:
   - **Visual mesh**: Export as STL/DAE with materials  
   - **Collision mesh**: Export as simplified STL

2. **Place mesh files**:
   ```bash
   # Copy your exported files to:
   meshes/visual/pipette_body.stl      # Visual representation
   meshes/collision/pipette_body.stl   # Collision detection
   ```

3. **Update URDF** (in `urdf/pipette_macro.urdf.xacro`):
   ```xml
   <!-- Find pipette_base_link visual section -->
   <visual>
     <geometry>
       <!-- Replace cylinder with your mesh -->
       <mesh filename="package://pipette_description/meshes/visual/pipette_body.stl"/>
     </geometry>
   </visual>
   ```

4. **Test the updated model**:
   ```bash
   ros2 launch pipette_description pipette_driver_display.launch.py start_driver:=false
   ```

## Testing and Validation

### Test URDF Syntax
```bash
# Validate URDF structure
ros2 run xacro xacro src/custom-ur-descriptions/pipette_description/urdf/pipette.urdf.xacro > /tmp/test.urdf
check_urdf /tmp/test.urdf

# Check for syntax errors
ros2 launch pipette_description pipette_driver_display.launch.py start_driver:=false
```

### Test Joint States Publishing
```bash
# With fake hardware
ros2 launch pipette_description pipette_driver_display.launch.py use_fake_hardware:=true

# In another terminal, check joint states
ros2 topic echo /joint_states

# Should see joint positions updating at 10Hz
```

### Test Action Server Integration
```bash
# Start fake hardware driver
ros2 launch pipette_description pipette_driver_display.launch.py use_fake_hardware:=true

# In another terminal, test action server
ros2 action list
ros2 action send_goal /follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{trajectory: {joint_names: ['plunger_joint', 'tip_eject_joint'], points: [{positions: [0.5, 0.3], time_from_start: {sec: 1}}]}}"
```

## Troubleshooting

### RViz Not Showing Model
```bash
# Check URDF processing
ros2 run xacro xacro src/custom-ur-descriptions/pipette_description/urdf/pipette.urdf.xacro

# Check robot_description topic
ros2 topic echo /robot_description --once

# Verify RViz configuration
# - Add RobotModel display
# - Set Robot Description topic to /robot_description
# - Set Fixed Frame to tool0 or world
```

### Joint Sliders Not Working
```bash
# Check joint state publisher GUI
ros2 node list | grep joint_state

# Check joint_states topic
ros2 topic echo /joint_states

# Ensure GUI is publishing correct joint names: ['plunger_joint', 'tip_eject_joint']
```

### Hardware Control Not Working
```bash
# Test pipette driver independently  
ros2 run pipette_driver pipette_driver_node --ros-args -p use_fake_hardware:=true

# Check action server availability
ros2 action list | grep follow_joint_trajectory

# Test joint state bridge
ros2 run pipette_driver joint_state_bridge
```

### No Joint State Updates
```bash
# Check if pipette_driver is publishing
ros2 topic info /joint_states

# Verify joint names match URDF
ros2 topic echo /joint_states --once

# Should see: ['plunger_joint', 'tip_eject_joint']
```

## Related Packages

This package works with:
- **`pipette_driver`** - Hardware control and action server interfaces
- **`pipette_moveit_config`** - MoveIt motion planning for standalone pipette
- **`ur5e_pipette_robot_description`** - Combined UR5e + pipette description  
- **`ur5e_pipette_moveit_config`** - Complete system MoveIt configuration

## Development Notes

### Modifying the URDF
1. **Edit** `urdf/pipette_macro.urdf.xacro` for structural changes
2. **Test syntax** with `xacro` and `check_urdf`
3. **Verify visualization** with RViz launch
4. **Update related packages** if joint names or limits change

### Adding New Joints
1. Add joint definition in `pipette_macro.urdf.xacro`
2. Update `pipette_driver` to handle new joints
3. Update `pipette_moveit_config` SRDF and controller configs
4. Test complete pipeline: URDF → driver → MoveIt

### Performance Tips
- Use simplified collision meshes for better performance
- Keep visual meshes under 10k triangles when possible
- Test with `start_driver:=false` first for pure URDF validation