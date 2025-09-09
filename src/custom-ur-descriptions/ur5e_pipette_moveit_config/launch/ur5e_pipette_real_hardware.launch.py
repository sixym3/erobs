#!/usr/bin/env python3

from moveit_configs_utils import MoveItConfigsBuilder
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    """
    Launch file for UR5e with pipette using real hardware.
    This launch file sets up the complete MoveIt stack with real robot hardware.
    """
    
    # Arguments - robot_ip is required for real hardware
    ur_type = DeclareLaunchArgument('ur_type', default_value='ur5e')
    robot_ip = DeclareLaunchArgument('robot_ip', description='IP address of the UR5e robot (required for real hardware)')
    description_package = DeclareLaunchArgument('description_package', default_value='ur5e_pipette_robot_description')
    description_file = DeclareLaunchArgument('description_file', default_value='ur_with_pipette.xacro')
    controllers_file = DeclareLaunchArgument('controllers_file', default_value=os.path.join(get_package_share_directory("ur5e_pipette_moveit_config"), "config", "ur_pipette_controllers.yaml"))

    # Tool communication arguments (for UR tool communication)
    tool_voltage_arg = DeclareLaunchArgument('tool_voltage', default_value='24')

    # Force real hardware mode - use use_fake_hardware parameter for XACRO
    xacro_args = {
        "name": "ur", 
        "ur_type": LaunchConfiguration("ur_type"), 
        "tf_prefix": "", 
        "use_fake_hardware": "false",  # Always use real hardware
        "robot_ip": LaunchConfiguration("robot_ip")
    }

    # UR Control with real hardware - use use_fake_hardware for ur_control launch
    ur_control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare("ur_robot_driver"), "launch", "ur_control.launch.py"])
        ]),
        launch_arguments={
            "ur_type": LaunchConfiguration("ur_type"),
            "robot_ip": LaunchConfiguration("robot_ip"),
            "launch_rviz": "false",
            "description_package": LaunchConfiguration("description_package"),
            "description_file": LaunchConfiguration("description_file"),
            "controllers_file": LaunchConfiguration("controllers_file"),
            "tool_voltage": LaunchConfiguration("tool_voltage"),
            "use_fake_hardware": "false",  # Force real hardware
        }.items()
    )

    # Load MoveIt! configuration
    moveit_config = (
        MoveItConfigsBuilder("ur", package_name="ur5e_pipette_moveit_config")
        .robot_description(file_path=os.path.join(get_package_share_directory("ur5e_pipette_robot_description"), "urdf", "ur_with_pipette.xacro"), mappings=xacro_args)
        .robot_description_semantic(file_path="srdf/ur.srdf")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=True, publish_robot_description_semantic=True
        )
        .planning_pipelines(pipelines=["ompl", "pilz_industrial_motion_planner"])
        .to_moveit_configs()
    )

    run_move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
        ],
    )

    # RViz
    rviz_arg = DeclareLaunchArgument(
        "rviz_config",
        default_value="view_robot.rviz",
        description="RViz config file"
    )

    rviz_config = PathJoinSubstitution([
        FindPackageShare("ur5e_pipette_moveit_config"), "rviz", LaunchConfiguration("rviz_config")
    ])

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
        ],
    )

    # Tool Communication Node for real hardware (optional - only if needed)
    # Uncomment if pipette requires UR tool communication
    # tool_communication = Node(
    #     package="ur_robot_driver",
    #     executable="tool_communication.py",
    #     name="tool_communication_node",
    #     output="screen",
    #     parameters=[{"robot_ip": LaunchConfiguration("robot_ip")}]
    # )

    # Static TF
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["--frame-id", "map", "--child-frame-id", "base_link"],
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[moveit_config.robot_description],
    )


    return LaunchDescription([
        # Arguments 
        ur_type,
        robot_ip,
        description_package,
        description_file,
        controllers_file,
        rviz_arg,
        tool_voltage_arg,

        # Nodes
        # tool_communication,  # Commented out - uncomment if needed
        ur_control_launch,
        run_move_group_node,
        rviz_node,
        static_tf,
        robot_state_publisher,
    ])