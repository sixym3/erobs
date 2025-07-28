# UR5e Pipette Robot Description

⚠️ **WARNING: This package is NOT TESTED yet** ⚠️

## Status

This package is a **work-in-progress** and has not been tested with real hardware or in simulation. It may contain outdated configurations and untested integrations.

**Current Status**: 🔴 **Not Ready for Use**

## Overview

This package is intended to provide a combined URDF description for a UR5e robot arm with an attached pipette tool. It aims to integrate:

- UR5e robot arm description
- Pipette tool description (from `pipette_description` package)
- Combined kinematics and joint limits
- Visualization and simulation support

## Package Contents

```
ur5e_pipette_robot_description/
├── urdf/
│   └── ur_with_pipette.xacro        # Combined UR5e + pipette URDF
├── config/
│   ├── ur5e/                        # UR5e specific parameters
│   ├── pipette/                     # Pipette specific parameters
│   └── initial_positions.yaml      # Default joint positions
├── meshes/
│   └── pipette/                     # Pipette mesh files
└── package.xml
```

## Known Issues

- ⚠️ **Untested integration** - May not work with current pipette_driver architecture
- ⚠️ **Outdated configurations** - May reference removed ros2_control interfaces
- ⚠️ **Unverified kinematics** - Joint limits and parameters not validated
- ⚠️ **Missing dependencies** - Package dependencies may be incomplete

## Testing Required

Before this package can be used, the following testing is needed:

### 1. URDF Validation
```bash
# Test URDF syntax (DO NOT RUN YET - may fail)
# ros2 run xacro xacro $(ros2 pkg prefix ur5e_pipette_robot_description)/share/ur5e_pipette_robot_description/urdf/ur_with_pipette.xacro
```

### 2. Visualization Testing
```bash
# Test RViz display (DO NOT RUN YET - may fail)
# ros2 launch ur5e_pipette_robot_description display.launch.py
```

### 3. Integration Testing
- Verify compatibility with current `pipette_driver` action-based architecture
- Test with `ur5e_pipette_moveit_config` package
- Validate joint limits and kinematics

## Recommended Approach

**Instead of using this untested package, use the working packages:**

### For Pipette-Only Work:
```bash
# Use the tested standalone pipette setup
ros2 launch pipette_moveit_config driver_with_rviz.launch.py
```

### For UR Robot Work:
```bash
# Use standard UR packages + separate pipette control
ros2 launch ur_robot_driver ur_control.launch.py robot_ip:=192.168.1.101

# In separate terminal:
ros2 launch pipette_moveit_config driver_with_rviz.launch.py
```

## Future Development

To make this package functional:

1. **Update URDF integration**:
   - Verify pipette attachment to UR5e tool flange
   - Update parameter passing and xacro includes

2. **Test with hardware**:
   - Validate with real UR5e + pipette setup
   - Test kinematics and joint limits

3. **Update configurations**:
   - Remove any ros2_control references if using action-based approach
   - Update to match working pipette_driver architecture

4. **Add proper launch files**:
   - Create tested launch configurations
   - Integrate with MoveIt planning

## Related Packages

**Working packages** (use these instead):
- `pipette_driver` - ✅ Tested hardware control
- `pipette_description` - ✅ Tested pipette URDF
- `pipette_moveit_config` - ✅ Tested motion planning

**Untested packages** (avoid for now):
- `ur5e_pipette_robot_description` - ❌ This package
- `ur5e_pipette_moveit_config` - ❌ Also untested

## Contributing

If you want to help test and fix this package:

1. Start with the working pipette packages
2. Test URDF integration step by step
3. Validate with real hardware
4. Update this README when testing is complete

---

**Until this package is tested, please use the standalone pipette packages for development.**