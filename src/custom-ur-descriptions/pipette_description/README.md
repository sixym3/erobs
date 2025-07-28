# Pipette Description

URDF description package for a pipette tool with geometry visualization and RViz integration.

## Overview

This package provides a URDF model of a pipette tool designed for integration with Universal Robot arms. The model includes joints for plunger and tip ejection control with RViz visualization support.

### Features
- **Visual Model**: Pipette representation with STL meshes (easily replaceable with CAD)
- **Joint Definitions**: Two linear joints for plunger and tip ejection control
- **LED Visualization**: Visual representation of LED strip
- **RViz Integration**: Joint state publisher and visualization support
- **Action-based Control**: Works with pipette_driver action server
- **UR Robot Integration Ready**: Designed to attach to robot flanges

## Package Structure

```
pipette_description/
├── urdf/
│   ├── pipette.urdf.xacro          # Main entry point
│   ├── pipette_macro.urdf.xacro    # Core pipette macro definition
│   └── pipette.ros2_control.xacro  # Legacy ros2_control config (unused)
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

### Visualization Only (No Hardware)
Test the URDF structure and visualization without hardware:

```bash
# Launch RViz with pipette model (no driver)
ros2 launch pipette_description pipette_driver_display.launch.py start_driver:=false

# Expected behavior:
# - RViz opens with pipette model displayed
# - Pipette geometry with links and joints
# - Joint State Publisher GUI with sliders for plunger/tip_eject joints
# - Moving sliders updates the model in RViz (visualization only)
```

### With Hardware Driver
Launch with actual pipette hardware control:

```bash
# Launch RViz with hardware control
ros2 launch pipette_description pipette_driver_display.launch.py

# Custom serial port
ros2 launch pipette_description pipette_driver_display.launch.py serial_port:=/dev/ttyUSB0

# Expected behavior:
# - RViz visualization 
# - Joint sliders control actual hardware
# - Arduino receives SETPOSITION commands
```

### Launch Arguments
- **`serial_port`** - Arduino serial port (default: `/tmp/ttyUR`)
- **`baudrate`** - Serial communication baud rate (default: `115200`)
- **`start_driver`** - Whether to start pipette driver node (default: `true`)
- **`start_rviz`** - Whether to start RViz visualization (default: `true`)

## URDF Parameters

The pipette URDF accepts these xacro parameters:

```xml
<!-- Hardware configuration -->
<xacro:arg name="use_fake_hardware" default="true"/>
<xacro:arg name="serial_port" default="/tmp/ttyUR"/>
<xacro:arg name="baudrate" default="115200"/>

<!-- Mounting configuration -->
<xacro:arg name="parent" default="tool0"/>
```

## Joint Definitions

### Joint Limits
- **plunger_joint**: Linear joint, 0.0 to 0.010m (10mm)
- **tip_eject_joint**: Linear joint, 0.0 to 0.005m (5mm)

### Link Structure
```
tool0 (parent)
├── pipette_base_link
├── plunger_link (moves with plunger_joint)
├── tip_eject_link (moves with tip_eject_joint)  
├── pipette_tip_link (end effector)
└── led_strip_link (visualization)
```

### Coordinate System
- **Plunger**: Positive movement = plunger depression
- **Tip Eject**: Positive movement = tip ejection
- **Base Frame**: `pipette_base_link` at tool attachment point

## Integration with Larger Systems

### Include in UR Robot URDF
```xml
<!-- Include in UR robot URDF -->
<xacro:include filename="$(find pipette_description)/urdf/pipette.urdf.xacro"/>

<!-- Attach to robot tool flange -->
<xacro:pipette parent="tool0" 
               use_fake_hardware="false"
               serial_port="/dev/ttyUSB0"/>
```

### Used by MoveIt Configuration
This package is referenced by:
- `pipette_moveit_config` - Standalone pipette motion planning
- `ur5e_pipette_moveit_config` - Combined UR5e + pipette system

## CAD Integration

### Current State: Placeholder Geometry
The URDF currently uses simple geometric shapes as placeholders.

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
   <!-- Find this section in pipette_base_link -->
   <visual>
     <geometry>
       <!-- Replace placeholder geometry -->
       <mesh filename="package://pipette_description/meshes/visual/pipette_body.stl"/>
     </geometry>
   </visual>
   ```

4. **Test the updated model**:
   ```bash
   ros2 launch pipette_description pipette_driver_display.launch.py start_driver:=false
   ```

## Troubleshooting

### RViz Not Showing Model
```bash
# Check URDF syntax
ros2 run xacro xacro $(ros2 pkg prefix pipette_description)/share/pipette_description/urdf/pipette.urdf.xacro

# Check RViz topics
ros2 topic list | grep robot_description
ros2 topic echo /robot_description --once
```

### Joint Sliders Not Working
```bash
# Check if joint_state_publisher_gui is running
ros2 node list | grep joint_state

# Check joint states topic
ros2 topic echo /joint_states

# Verify launch file includes joint_state_publisher_gui
```

### Hardware Control Not Working  
```bash
# Test pipette driver independently
ros2 run pipette_driver pipette_driver_node

# Test serial communication  
ros2 run pipette_driver serial_terminal

# Check if joint_state_bridge is running
ros2 node list | grep joint_state_bridge
```

## Files Reference

### Core URDF Files
- `urdf/pipette.urdf.xacro` - Main entry point with parameters
- `urdf/pipette_macro.urdf.xacro` - Pipette macro definition with links and joints

### Visualization Files
- `rviz/pipette_demo.rviz` - RViz display configuration
- `rviz/urdf.rviz` - Basic URDF visualization

### Launch Files
- `launch/pipette_driver_display.launch.py` - Complete visualization and driver launch

## Related Packages

This package works with:
- **`pipette_driver`** - Hardware control and ROS2 action interfaces
- **`pipette_moveit_config`** - MoveIt motion planning for standalone pipette  
- **`ur5e_pipette_robot_description`** - Combined UR5e + pipette description
- **`ur5e_pipette_moveit_config`** - Complete system MoveIt configuration

## Development Notes

### Adding New Joints
1. Modify `urdf/pipette_macro.urdf.xacro`
2. Update joint limits in the URDF  
3. Update companion packages (`pipette_driver`, `pipette_moveit_config`)
4. Test visualization and hardware control

### Testing Changes
```bash
# Always test URDF syntax first
ros2 run xacro xacro $(ros2 pkg prefix pipette_description)/share/pipette_description/urdf/pipette.urdf.xacro > /tmp/test.urdf
check_urdf /tmp/test.urdf

# Test visualization
ros2 launch pipette_description pipette_driver_display.launch.py start_driver:=false

# Test with hardware (if available)
ros2 launch pipette_description pipette_driver_display.launch.py
```