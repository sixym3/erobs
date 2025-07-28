# UR5e Pipette MoveIt Configuration

⚠️ **WARNING: This package is NOT TESTED yet** ⚠️

## Status

This package is a **work-in-progress** and has not been tested with real hardware or in simulation. It may contain outdated configurations and incompatible controller setups.

**Current Status**: 🔴 **Not Ready for Use**

## Overview

This package is intended to provide MoveIt motion planning configuration for a combined UR5e robot arm with attached pipette tool. It aims to provide:

- Complete system motion planning (UR5e arm + pipette tool)
- MoveIt integration with dual-arm coordination
- RViz motion planning interface
- Hardware controller integration

## Package Contents

```
ur5e_pipette_moveit_config/
├── config/
│   ├── moveit_controllers.yaml      # Controller configurations
│   ├── kinematics.yaml             # Inverse kinematics solvers
│   ├── joint_limits.yaml           # Combined joint limits
│   └── moveit.rviz                 # RViz configuration
├── launch/
│   ├── demo.launch.py              # Main demo launch
│   ├── move_group.launch.py        # MoveIt move_group
│   └── [multiple untested launch files]
├── srdf/
│   └── ur.srdf                     # Semantic robot description
└── package.xml
```

## Known Issues

- ⚠️ **Untested integration** - No validation with current pipette_driver
- ⚠️ **Controller conflicts** - May have conflicting controller configurations
- ⚠️ **Outdated launch files** - Multiple untested launch configurations
- ⚠️ **Unverified planning groups** - Planning groups may not work correctly
- ⚠️ **Missing dependencies** - Package dependencies may be incomplete or incorrect

## Problems with Current State

### Duplicate/Conflicting Files
This package contains multiple duplicate files that suggest incomplete setup:
- Multiple `demo.launch.py` files
- Duplicate controller configurations
- Mixed launch file locations (root + launch/ directory)

### Likely Incompatible with Current Architecture
The current working pipette system uses:
- Action-based control (`FollowJointTrajectory`)
- Standalone pipette_driver_node
- Manual joint slider control

This package likely assumes:
- ros2_control integration (which was removed)
- Different controller architecture
- Untested UR5e + pipette coordination

## Testing Required

**DO NOT RUN** the following commands until testing is complete:

```bash
# These may fail or cause issues:
# ros2 launch ur5e_pipette_moveit_config demo.launch.py
# ros2 launch ur5e_pipette_moveit_config move_group.launch.py
```

## Recommended Approach

**Instead of using this untested package, use the working approach:**

### Separate Control Strategy
```bash
# Terminal 1: UR5e robot control
ros2 launch ur_robot_driver ur_control.launch.py robot_ip:=192.168.1.101

# Terminal 2: UR5e MoveIt (standard)
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur5e

# Terminal 3: Pipette control (standalone)
ros2 launch pipette_moveit_config driver_with_rviz.launch.py

# Terminal 4: UR tool communication (if needed)
ros2 run ur_robot_driver tool_communication.py --ros-args -p robot_ip:=192.168.1.101
```

This approach gives you:
- ✅ **Tested UR5e control** with standard UR packages
- ✅ **Tested pipette control** with working pipette packages
- ✅ **Reliable operation** with known-good configurations
- ✅ **Independent debugging** of each system

## Issues to Fix Before Use

1. **Clean up duplicate files**:
   - Remove duplicate launch files
   - Consolidate controller configurations
   - Fix file organization

2. **Update controller integration**:
   - Verify compatibility with action-based pipette_driver
   - Test controller namespacing
   - Validate MoveIt controller manager setup

3. **Test planning groups**:
   - Verify SRDF planning group definitions
   - Test kinematics solvers
   - Validate joint limits for combined system

4. **Hardware validation**:
   - Test with real UR5e + pipette hardware
   - Verify coordinate frame relationships
   - Test motion planning execution

## Development Status

### Current Working Packages ✅
- `pipette_driver` - Hardware control and action server
- `pipette_description` - URDF robot description  
- `pipette_moveit_config` - Standalone pipette motion planning

### Packages Needing Work ❌
- `ur5e_pipette_robot_description` - Untested URDF integration
- `ur5e_pipette_moveit_config` - This package (untested MoveIt config)

## Future Development

To make this package functional:

1. **Start with working packages**:
   - Ensure `pipette_moveit_config` works perfectly
   - Test UR5e integration separately

2. **Gradual integration**:
   - Test URDF combination first
   - Add MoveIt configuration incrementally
   - Validate each step with hardware

3. **Clean package structure**:
   - Remove duplicate files
   - Organize launch files properly
   - Update package dependencies

4. **Comprehensive testing**:
   - Test motion planning for combined system
   - Validate collision detection
   - Test hardware integration

## Contributing

If you want to help develop this package:

1. **Start with the working standalone packages**
2. **Test integration step-by-step**
3. **Document any issues found**  
4. **Update this README when testing is complete**

## Related Packages

**Use these tested packages instead:**
- `ur_robot_driver` - ✅ UR robot control
- `ur_moveit_config` - ✅ UR MoveIt configuration
- `pipette_driver` - ✅ Pipette hardware control
- `pipette_moveit_config` - ✅ Pipette motion planning

---

**Until this package is properly tested, use the separate control strategy described above.**