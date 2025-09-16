# UR5e Pipette Robot Description

Complete robot description package for UR5e arm with static pipette tool. Provides unified URDF model combining UR5e arm with pipette geometry for visualization and collision checking.

## Overview

This package provides the complete URDF description for the UR5e robot arm with an attached pipette tool. The pipette is treated as a static end effector with visual and collision geometry for motion planning and safety.

### Features
- **Complete System URDF** - Unified description of UR5e + pipette
- **Static End Effector** - Pipette as fixed geometry for collision checking
- **UR Integration** - Built on standard UR description packages
- **MoveIt Compatible** - Works with MoveIt motion planning
- **Hardware Agnostic** - Supports both simulation and real hardware
- **Modular Design** - Easy to modify or replace end effector

## Package Structure

```
ur5e_pipette_robot_description/
├── urdf/
│   └── ur_with_pipette.xacro      # Main URDF file combining UR5e + pipette
├── launch/
│   └── display.launch.py          # Visualization launch file
├── config/
│   └── initial_positions.yaml     # Default joint positions for simulation
└── CMakeLists.txt
└── package.xml
```

## Quick Start

### Build the Package
```bash
cd /path/to/your/workspace
colcon build --packages-select ur5e_pipette_robot_description pipette_description
source install/setup.bash
```

### View Robot Model
```bash
# Launch RViz with robot model
ros2 launch ur5e_pipette_robot_description display.launch.py

# Expected behavior:
# - RViz opens with UR5e robot and pipette displayed
# - Joint state sliders for arm joints only
# - Static pipette geometry attached to tool flange
```

## URDF Architecture

### Main Components

1. **UR5e Base**: Standard UR5e arm description from `ur_description`
2. **Pipette Tool**: Static pipette geometry from `pipette_description`
3. **Integration**: Pipette attached to UR `tool0` frame

### Link Structure
```
map (world frame)
└── base_link (UR5e base)
    └── ... (UR5e arm links)
        └── tool0 (UR flange)
            └── pipette_base_link
                ├── pipette_body_link (main geometry)
                ├── pipette_tip_link (TCP reference)
                └── led_strip_link (visual only)
```

### Joint Structure
- **UR5e joints**: 6 DOF arm (shoulder_pan, shoulder_lift, elbow, wrist_1/2/3)
- **Pipette joints**: All fixed (no movable pipette joints in MoveIt)
- **Total DOF**: 6 (arm only, pipette is static)

## URDF Parameters

The main URDF file accepts these xacro arguments:

### Standard UR Parameters
```xml
<!-- Robot configuration -->
<xacro:arg name="name" default="ur"/>
<xacro:arg name="ur_type" default="ur5e"/>
<xacro:arg name="tf_prefix" default=""/>

<!-- Hardware configuration -->
<xacro:arg name="use_fake_hardware" default="false"/>
<xacro:arg name="robot_ip" default="0.0.0.0"/>

<!-- Joint limits and calibration -->
<xacro:arg name="joint_limit_params" default="..."/>
<xacro:arg name="kinematics_params" default="..."/>
<xacro:arg name="physical_params" default="..."/>
```

### Pipette-Specific Parameters
```xml
<!-- Pipette tool configuration -->
<xacro:arg name="pipette_mass" default="0.200"/>
<xacro:arg name="pipette_xyz" default="0 0 0"/>
<xacro:arg name="pipette_rpy" default="0 0 0"/>
```

## Usage Examples

### Basic Visualization
```bash
# Launch with default parameters
ros2 launch ur5e_pipette_robot_description display.launch.py
```

### Custom Configuration
```bash
# Custom pipette positioning
ros2 launch ur5e_pipette_robot_description display.launch.py \
  pipette_xyz:="0 0 0.05" \
  pipette_rpy:="0 0 1.57" \
  pipette_mass:=0.250

# With TF prefix for multi-robot setups
ros2 launch ur5e_pipette_robot_description display.launch.py \
  tf_prefix:=robot1_ \
  name:=robot1
```

### Generate URDF
```bash
# Generate complete URDF for inspection
ros2 run xacro xacro \
  $(ros2 pkg prefix ur5e_pipette_robot_description)/share/ur5e_pipette_robot_description/urdf/ur_with_pipette.xacro \
  name:=ur ur_type:=ur5e > robot.urdf

# Validate URDF structure
check_urdf robot.urdf
```

## Integration with MoveIt

This package is used by:
- **`ur5e_pipette_moveit_config`** - MoveIt motion planning configuration
- **MoveIt Setup Assistant** - For generating new configurations
- **RViz** - For robot visualization with motion planning

### Key Integration Points
- **Planning frame**: `base_link` or `map`
- **End effector frame**: `pipette_tip_link`
- **Collision checking**: Includes pipette geometry
- **Joint limits**: Standard UR5e limits only (no pipette joints)

## Hardware Compatibility

### Simulation Mode
```xml
<!-- For fake hardware -->
<xacro:arg name="use_fake_hardware" value="true"/>
```
- Works with MoveIt fake controllers
- Joint state publisher for visualization
- No real hardware required

### Real Hardware Mode
```xml
<!-- For real UR5e robot -->
<xacro:arg name="use_fake_hardware" value="false"/>
<xacro:arg name="robot_ip" value="192.168.1.100"/>
```
- Connects to real UR5e robot
- Uses UR robot driver
- Pipette control handled by separate driver

## Customization

### Modify Pipette Attachment
Edit `urdf/ur_with_pipette.xacro`:

```xml
<!-- Change pipette mounting position -->
<xacro:pipette
  name="pipette"
  prefix="$(arg tf_prefix)"
  parent="$(arg tf_prefix)tool0"
  pipette_mass="0.300"          <!-- Custom mass -->
  xyz="0 0 0.02"               <!-- Custom position -->
  rpy="0 0 1.57"/>              <!-- Custom orientation -->
```

### Replace with Different Tool
1. **Create new tool description package** (e.g., `gripper_description`)
2. **Update URDF include**:
   ```xml
   <!-- Replace pipette include -->
   <xacro:include filename="$(find gripper_description)/urdf/gripper_macro.urdf.xacro"/>
   
   <!-- Replace pipette macro call -->
   <xacro:gripper parent="$(arg tf_prefix)tool0" .../>
   ```
3. **Update package dependencies** in `package.xml`
4. **Test with visualization**

### Add Tool Communication
For tools requiring UR tool communication:

```xml
<!-- Enable tool communication -->
<xacro:arg name="use_tool_communication" default="true"/>
<xacro:arg name="tool_voltage" default="24"/>
<xacro:arg name="tool_tcp_port" default="54321"/>
```

## Validation and Testing

### URDF Syntax Validation
```bash
# Check URDF syntax
ros2 run xacro xacro $(ros2 pkg prefix ur5e_pipette_robot_description)/share/ur5e_pipette_robot_description/urdf/ur_with_pipette.xacro > /tmp/robot.urdf
check_urdf /tmp/robot.urdf

# Should output successful parsing and joint/link counts
# Expected: ~12 joints (6 UR5e + various fixed), ~15 links
```

### Visualization Testing
```bash
# Test complete visualization
ros2 launch ur5e_pipette_robot_description display.launch.py

# Verify in RViz:
# - Robot model appears correctly
# - UR5e joint sliders work (no pipette joint sliders)
# - TF frames are published correctly
# - No error messages in console
```

### TF Tree Validation
```bash
# Check TF tree structure
ros2 run tf2_tools view_frames

# Verify expected frame hierarchy:
# map → base_link → ... → tool0 → pipette_base_link → pipette_tip_link

# Test specific transformations
ros2 run tf2_ros tf2_echo base_link pipette_tip_link
```

## Troubleshooting

### URDF Not Loading
```bash
# Check xacro processing
ros2 run xacro xacro src/ur5e_pipette_robot_description/urdf/ur_with_pipette.xacro

# Check for missing dependencies
colcon build --packages-select ur5e_pipette_robot_description --cmake-args -DCMAKE_VERBOSE_MAKEFILE=ON
```

### Missing Pipette Geometry
```bash
# Verify pipette_description package
ros2 pkg list | grep pipette_description

# Check pipette URDF
ros2 run xacro xacro $(ros2 pkg prefix pipette_description)/share/pipette_description/urdf/pipette_macro.urdf.xacro
```

### RViz Visualization Issues
```bash
# Check robot_description topic
ros2 topic echo /robot_description --once

# Verify TF tree
ros2 run tf2_tools view_frames

# Check for missing mesh files
ls $(ros2 pkg prefix pipette_description)/share/pipette_description/meshes/
```

## Related Packages

### Dependencies
- **`ur_description`** - Base UR robot descriptions
- **`pipette_description`** - Pipette tool URDF
- **`xacro`** - URDF macro processing

### Used By
- **`ur5e_pipette_moveit_config`** - MoveIt configuration
- **Launch files** - Robot bringup and demo scripts
- **Simulation packages** - Gazebo and other simulators

## Development Notes

### Modifying the URDF
1. **Test changes** with `display.launch.py` first
2. **Validate syntax** with xacro and check_urdf
3. **Update dependent packages** if link names change
4. **Test integration** with MoveIt configuration

### Adding New Robot Types
To support other UR models (ur3e, ur10e, etc.):

1. **Update launch arguments**: Add new `ur_type` options
2. **Test compatibility**: Verify pipette attachment works
3. **Update documentation**: Include new robot type examples
4. **Create specific packages**: Consider separate packages for different robots

### Performance Considerations
- **Mesh complexity**: Keep pipette meshes reasonably detailed for collision checking
- **Joint limits**: Ensure UR joint limits account for pipette tool mass
- **Inertial properties**: Update if pipette mass significantly affects dynamics

## Future Modularity Recommendations

To make this system more modular for easy end effector swapping:

### 1. Parameter-Driven Tool Selection
```xml
<!-- Future enhancement: tool selection via parameter -->
<xacro:arg name="end_effector_type" default="pipette"/>
<xacro:if value="${end_effector_type == 'pipette'}">
  <xacro:include filename="$(find pipette_description)/urdf/pipette_macro.urdf.xacro"/>
  <xacro:pipette parent="$(arg tf_prefix)tool0" .../>
</xacro:if>
<xacro:if value="${end_effector_type == 'gripper'}">
  <xacro:include filename="$(find gripper_description)/urdf/gripper_macro.urdf.xacro"/>
  <xacro:gripper parent="$(arg tf_prefix)tool0" .../>
</xacro:if>
```

### 2. Standardized Tool Interface
- Common mounting interface at `tool0`
- Standardized parameter naming conventions
- Consistent end effector reference frame naming

### 3. Configuration Templates
- Tool-specific configuration files
- Automated MoveIt configuration updates
- Launch file templates for different tools