# End Effectors

This directory contains drivers and configuration for robot end effectors like grippers and vacuum systems.

## Getting the Drivers

The actual driver code lives in separate repositories. To download them:

```bash
vcs import src/end_effectors < src/end_effectors/end_effectors.repos
```

This pulls in:
- `serial` - ROS2 serial communication
- `robotiq_hande` - Robotiq HandE gripper driver and URDF models
- `ros2_epick_gripper` - EPick vacuum gripper driver
- `pipettor` - Custom pipettor developed at CMS NSLS-2
    
    
**Note:** The `ros2_epick_gripper` repository includes `epick_moveit_studio` which depends on paywalled MoveIt Studio/MoveIt Pro packages. Since we don't use this package, skip it during build and dependency installation:

```bash
# Install dependencies
bash setup.sh

# Build workspace (skip epick_moveit_studio)
bash build.sh

## EPick Configuration

The `epick_config` package provides an overlay configuration (over ros2_epick_driver) for our specific setup:

- Serial port: `/tmp/ttyUR`
- Custom positioning offsets
- Hardware vs simulation mode

## Future Work

For simpler single-robot setups, we could skip the overlay package and put EPick parameters directly in the robot URDF files?