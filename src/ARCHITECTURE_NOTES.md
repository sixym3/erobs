# UR5e Robot System Architecture Notes

## Current State (As of 2025-01-24)

### What Was Just Implemented
We successfully created a complete pipette integration following the existing `ur5e_hande` pattern:

1. **pipette_driver** - Python-based ros2_control hardware interface + Arduino firmware
2. **pipette_description** - Static URDF with ros2_control integration
3. **ur5e_pipette_robot_description** - UR5e + pipette integration
4. **ur5e_pipette_moveit_config** - Complete MoveIt config with `move_group.launch.py`

### Architecture Issues Identified

**PROBLEM: Package Explosion**
- Current pattern: Each tool requires 2 packages (`*_robot_description` + `*_moveit_config`)
- Results in exponential growth: N tools = 2N packages
- Massive code duplication in launch files and configs
- No runtime flexibility to switch tools

**PROBLEM: Launch File Duplication**
- Each tool gets identical `move_group.launch.py` with 95% same code
- Only differences: tool URDF file, controller config, planning groups
- Maintenance nightmare when updating base robot configs

**PROBLEM: No Runtime Tool Switching**
- Must stop entire system to change tools
- No way to switch end effectors in RViz/MoveIt
- Hard-coded tool selection in launch files

## Recommended Future Architecture

### Option A: Modular Launch System (RECOMMENDED)

**Single Robot Description Package:**
```
ur5e_system_description/
├── urdf/
│   ├── ur5e_base.xacro              # UR5e robot only
│   └── ur5e_with_tool.xacro         # Parameterized: tool:=${tool_type}
├── tools/
│   ├── pipette/
│   │   ├── pipette.urdf.xacro
│   │   ├── physical_params.yaml
│   │   └── visual_params.yaml
│   ├── hande/
│   │   └── hande.urdf.xacro
│   └── none/
│       └── no_tool.urdf.xacro       # Bare flange
└── config/
    └── tool_registry.yaml           # Available tools mapping
```

**Single MoveIt Configuration Package:**
```
ur5e_moveit_config/
├── launch/
│   └── move_group.launch.py         # ONE launch file: tool:=pipette|hande|none
├── config/
│   ├── base_controllers.yaml       # UR robot controllers (shared)
│   └── tools/
│       ├── pipette_controllers.yaml
│       ├── hande_controllers.yaml
│       └── none_controllers.yaml
├── srdf/
│   ├── base.srdf.xacro             # Base robot planning groups
│   └── tools/
│       ├── pipette.srdf.xacro      # Pipette-specific groups
│       └── hande.srdf.xacro        # Hande-specific groups
└── scripts/
    └── generate_config.py          # Dynamic config generation
```

**Usage Examples:**
```bash
# Switch tools via launch parameter
ros2 launch ur5e_moveit_config move_group.launch.py tool:=pipette robot_ip:=192.168.1.101
ros2 launch ur5e_moveit_config move_group.launch.py tool:=hande robot_ip:=192.168.1.101
ros2 launch ur5e_moveit_config move_group.launch.py tool:=none robot_ip:=192.168.1.101

# Tool-specific parameters passed through
ros2 launch ur5e_moveit_config move_group.launch.py tool:=pipette serial_port:=/dev/ttyUSB0
```

### Key Benefits of Recommended Architecture

1. **Scalability**: N tools = 1 base + N tool configs (linear growth)
2. **Maintainability**: Single source of truth for robot and MoveIt configs
3. **Flexibility**: Runtime tool selection without system restart
4. **DRY Principle**: No code duplication across tool integrations
5. **Extensibility**: Adding new tools only requires tool-specific configs

## Implementation Strategy

### Phase 1: Test Current Implementation
- Verify pipette_driver hardware interface works with Arduino
- Test pipette_description URDF visualization
- Validate ur5e_pipette_moveit_config with move_group.launch.py
- Confirm CAD integration workflow

### Phase 2: Create Unified Architecture (Future)
1. **Extract Common Base**: Create ur5e_system_description with parameterized tool inclusion
2. **Consolidate MoveIt**: Merge all *_moveit_config packages into single ur5e_moveit_config
3. **Dynamic Configuration**: Implement tool parameter parsing in launch files
4. **Tool Registry**: Create centralized tool configuration management
5. **Migration Path**: Gradual refactoring while maintaining backward compatibility

### Phase 3: Advanced Features (Optional)
- Runtime tool switching via ROS2 services
- Tool detection and auto-configuration
- GUI tool selector for RViz
- Hot-swappable tool descriptions

## Hardware Interface Status

### pipette_driver Package
- **Python-based hardware interface**: Uses existing serial communication pattern
- **Arduino firmware**: `pipette_actuator_control.ino` with actuator commands
- **ros2_control integration**: Position controllers for plunger + tip ejection
- **Backward compatibility**: Original action-based interface still available

### Integration Pattern
- **Tool attachment**: Always to UR `flange` link via fixed joint
- **Communication**: Uses UR tool communication port (`/tmp/ttyUR` at 115200 baud)
- **Controllers**: Extend base UR controllers with tool-specific ones
- **Hardware interface**: Plugin-based system for different tools

## Current Package Dependencies
```
pipette_driver → pipette_description → ur5e_pipette_robot_description → ur5e_pipette_moveit_config
     ↓                    ↓                           ↓                            ↓
Hardware Interface    Static URDF           UR+Tool Integration         MoveIt Planning
```

## Testing Status
- **Hardware interface**: Created but needs Arduino testing
- **URDF visualization**: Ready for testing with placeholder geometry
- **MoveIt integration**: Complete but untested
- **CAD integration**: Framework ready, awaiting actual CAD files

## Next Steps Priority
1. **Test current implementation** with real hardware
2. **Validate CAD integration** workflow
3. **Assess scalability needs** based on planned tools
4. **Refactor to unified architecture** if multiple tools confirmed

## Tool-Specific Notes

### Pipette Tool
- **Actuators**: 2 prismatic joints (plunger: 0-10mm, tip_eject: 0-5mm)
- **LED control**: GPIO interface for visual feedback
- **Serial protocol**: Line-based commands with Arduino
- **Safety limits**: Configurable via URDF parameters

### Future Tools Considerations
- Each tool should define its own hardware interface plugin
- Tool-specific controller configurations should be modular
- URDF tool descriptions should be self-contained
- Planning groups should be composable with base robot groups

---
**Last Updated**: 2025-01-24
**Status**: Implementation complete, testing needed, architecture refactoring planned