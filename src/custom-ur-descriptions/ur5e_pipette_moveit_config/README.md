# UR5e Pipette MoveIt Configuration

MoveIt motion planning configuration package for UR5e robot arm with static pipette tool. This package provides motion planning capabilities for the UR5e arm with pipette treated as fixed end effector geometry.

## Overview

This package provides a MoveIt setup for the UR5e robot with attached pipette tool, enabling motion planning, visualization, and control of the robot arm with the pipette as a static end effector for collision checking.

### Features
- **Arm Motion Planning** - Motion planning for UR5e arm with pipette geometry
- **MoveIt Integration** - Full MoveIt stack with planning plugins
- **Dual Hardware Support** - Works with both simulated and real hardware
- **Static End Effector** - Pipette treated as fixed geometry for collision avoidance
- **RViz Visualization** - Pre-configured RViz setup with Motion Planning interface
- **External Driver Compatible** - Works with separate pipette control driver
- **Safety Features** - Joint limits and collision detection including pipette geometry

## Package Contents

```
ur5e_pipette_moveit_config/
├── config/
│   ├── moveit_controllers.yaml     # MoveIt controller configuration (arm only)
│   ├── kinematics.yaml            # Inverse kinematics solvers  
│   ├── joint_limits.yaml          # UR5e arm joint limits
│   ├── ur_pipette_controllers.yaml # Hardware controller setup
│   └── moveit.rviz                # RViz configuration
├── launch/
│   ├── ur5e_pipette_fake_hardware.launch.py  # Complete system with simulation
│   ├── ur5e_pipette_real_hardware.launch.py  # Real hardware integration
│   └── demo.launch.py                         # MoveIt demo with pipette
├── srdf/
│   └── ur.srdf                    # Semantic robot description
└── rviz/
    └── view_robot.rviz           # Robot visualization configuration
```

## Prerequisites

```bash
# Install MoveIt and UR dependencies
sudo apt install ros-humble-moveit ros-humble-moveit-planners-ompl 
sudo apt install ros-humble-ur ros-humble-ur-robot-driver
sudo apt install ros-humble-joint-state-publisher-gui

# Build required packages
cd /path/to/your/workspace
colcon build --packages-select ur5e_pipette_robot_description ur5e_pipette_moveit_config pipette_description
source install/setup.bash
```

## Quick Start

### 1. Simulation Mode (Fake Hardware)
Launch complete system with simulated hardware:

```bash
# Launch MoveIt with fake hardware
ros2 launch ur5e_pipette_moveit_config ur5e_pipette_fake_hardware.launch.py

# Expected behavior:
# - RViz opens with UR5e + pipette model
# - Motion Planning interface available
# - Can plan and execute arm motions
# - Pipette geometry included in collision checking
# - Pipette control handled by external driver (if running)
```

### 2. Real Hardware Mode
Launch with real UR5e robot:

```bash
# Launch with real hardware (replace IP address)
ros2 launch ur5e_pipette_moveit_config ur5e_pipette_real_hardware.launch.py robot_ip:=192.168.1.100

# Expected behavior:
# - Connects to real UR5e robot
# - MoveIt motion planning for arm
# - Pipette geometry for collision avoidance
# - Separate pipette driver handles pipette control
```

### 3. Demo Mode
Simple MoveIt demo with pipette:

```bash
# Launch demo mode
ros2 launch ur5e_pipette_moveit_config demo.launch.py

# Features:
# - MoveIt motion planning interface
# - Pre-configured robot with pipette
# - No hardware dependencies
```

## Launch Arguments

### Common Arguments
- **`ur_type`** - UR robot type (default: `ur5e`)
- **`robot_ip`** - Robot IP address (required for real hardware)
- **`use_fake_hardware`** - Use simulated hardware (default: `false` for real, `true` for fake)
- **`launch_rviz`** - Start RViz visualization (default: `true`)

### Hardware-Specific Arguments
- **`controllers_file`** - Controller configuration file
- **`description_package`** - Robot description package name
- **`description_file`** - Main URDF file name

## Planning Groups

The SRDF defines these planning groups:

### `ur_arm`
- **Purpose**: UR5e arm motion planning
- **Joints**: shoulder_pan, shoulder_lift, elbow, wrist_1, wrist_2, wrist_3
- **Use case**: Primary group for arm motion planning

### `ur_arm_with_pipette`
- **Purpose**: Complete system reference
- **Contains**: ur_arm group 
- **Use case**: Planning with pipette geometry for collision checking

## Architecture Notes

### Static End Effector Design
- **Fixed pipette**: No movable joints in MoveIt planning
- **Collision geometry**: Pipette shape included for path planning
- **External control**: Pipette plunger/tip ejection handled by separate driver
- **End effector reference**: `pipette_tip_link` as TCP reference point

### Controller Configuration
The system uses these controllers:
- **`scaled_joint_trajectory_controller`**: UR arm motion control
- **No pipette controllers**: Pipette control handled externally

### Integration with Drivers
- **UR arm control**: Standard UR robot drivers
- **Pipette control**: Separate pipette_driver node (external)
- **Coordination**: Both systems work independently

## Usage Patterns

### Motion Planning with Pipette
```python
# Python example using MoveIt Python interface
import moveit_commander

# Initialize MoveIt
robot = moveit_commander.RobotCommander()
scene = moveit_commander.PlanningSceneInterface()

# Plan arm motion (pipette moves with arm)
arm_group = moveit_commander.MoveGroupCommander("ur_arm")
arm_group.set_pose_target(target_pose)
plan = arm_group.plan()
arm_group.execute(plan, wait=True)

# Pipette control handled separately by pipette_driver
```

### Adding Collision Objects
```python
# Add collision objects that consider pipette geometry
scene = moveit_commander.PlanningSceneInterface()

# Add table
table_pose = geometry_msgs.msg.PoseStamped()
table_pose.header.frame_id = "base_link"
table_pose.pose.position.z = -0.1
scene.add_box("table", table_pose, size=(2.0, 2.0, 0.1))
```

## Troubleshooting

### MoveIt Planning Fails
```bash
# Check planning group configuration
ros2 param get /move_group planning_plugin

# Verify robot model loads correctly
ros2 topic echo /robot_description --once

# Check joint states are published
ros2 topic echo /joint_states
```

### RViz Visualization Issues
```bash
# Check robot model display
# - Verify Robot Description topic: /robot_description  
# - Check Fixed Frame: base_link or map
# - Verify TF tree is complete

# Check TF tree
ros2 run tf2_tools view_frames
```

### Controller Connection Issues
```bash
# List available controllers
ros2 control list_controllers

# Check controller status
ros2 control list_hardware_interfaces

# For real hardware, verify robot IP and network connection
ping <robot_ip>
```

### Missing Pipette Geometry
```bash
# Check pipette description package
ros2 pkg list | grep pipette_description

# Verify URDF includes pipette
ros2 run xacro xacro $(ros2 pkg prefix ur5e_pipette_robot_description)/share/ur5e_pipette_robot_description/urdf/ur_with_pipette.xacro | grep pipette
```

## Configuration Files

### `moveit_controllers.yaml`
Defines MoveIt controller interface:
- Maps planning groups to hardware controllers
- Configures action interfaces for arm control
- No pipette controllers (handled externally)

### `ur.srdf` 
Semantic robot description:
- Planning groups definition
- Collision avoidance rules
- End effector configuration
- Static pipette geometry integration

### `ur_pipette_controllers.yaml`
Hardware controller configuration:
- UR arm controller setup
- No pipette-specific controllers
- Compatible with standard UR drivers

## Related Packages

This package works with:
- **`ur5e_pipette_robot_description`** - Combined robot URDF
- **`pipette_description`** - Pipette URDF description
- **`pipette_driver`** - External pipette control (separate)
- **`ur_robot_driver`** - UR robot hardware interface

## Development Notes

### Modifying Planning Groups
1. Edit `srdf/ur.srdf` for group definitions
2. Update controller mappings in `config/moveit_controllers.yaml`
3. Test with `demo.launch.py` first
4. Validate with hardware launch files

### Adding New End Effectors
To replace pipette with different tool:
1. Create new tool description package
2. Update `ur5e_pipette_robot_description` URDF include
3. Modify SRDF collision rules
4. Update package dependencies