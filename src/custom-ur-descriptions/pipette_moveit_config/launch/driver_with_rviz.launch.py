#!/usr/bin/env python3

from moveit_configs_utils import MoveItConfigsBuilder
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """
    Launch pipette MoveIt system with RViz Motion Planning and real hardware control.
    Provides MoveIt interface for motion planning and execution on real hardware.
    """
    
    ## Arguments
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')
    serial_port_arg = DeclareLaunchArgument('serial_port', default_value='/dev/ttyUR')
    baudrate_arg = DeclareLaunchArgument('baudrate', default_value='115200')
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    serial_port = LaunchConfiguration('serial_port')
    baudrate = LaunchConfiguration('baudrate')

    # MoveIt Configuration for standalone pipette
    moveit_config = (
        MoveItConfigsBuilder("pipette", package_name="pipette_moveit_config")
        .robot_description(file_path=os.path.join(
            get_package_share_directory("pipette_description"), 
            "urdf", 
            "pipette.urdf.xacro"
        ), mappings={
            "use_fake_hardware": "false",
            "serial_port": serial_port,
            "baudrate": baudrate,
            "parent": "tool0",
            "plunger_max": "1.0",
            "tip_eject_max": "1.0"
        })
        .robot_description_semantic(file_path=os.path.join(
            get_package_share_directory("pipette_moveit_config"),
            "srdf",
            "pipette.srdf"
        ))
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=True, 
            publish_robot_description_semantic=True
        )
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    # Move Group Node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": use_sim_time},
        ],
    )

    # RViz with MoveIt Motion Planning Plugin
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        arguments=["-d", os.path.join(
            get_package_share_directory("pipette_moveit_config"), 
            "rviz", 
            "moveit.rviz"
        )],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            {"use_sim_time": use_sim_time},
        ],
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[
            moveit_config.robot_description,
            {"use_sim_time": use_sim_time},
        ],
    )

    # Controller Manager - manages ros2_control controllers
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        name="controller_manager",
        output="both",
        parameters=[
            moveit_config.robot_description,
            os.path.join(
                get_package_share_directory("pipette_description"), 
                "config", 
                "pipette_controllers.yaml"
            ),
            {"use_sim_time": use_sim_time},
        ],
    )

    # Joint State Broadcaster - publishes joint states from hardware
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="joint_state_broadcaster_spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    # Pipette Controller Spawner - spawns the pipette trajectory controller
    pipette_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="pipette_controller_spawner", 
        arguments=["pipette_controller"],
        output="screen",
    )

    # Static transform publisher (world to tool0 for visualization)
    static_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0", "0", "0", "0", "0", "0", "world", "tool0"],
    )

    return LaunchDescription([
        # Arguments
        use_sim_time_arg,
        serial_port_arg,
        baudrate_arg,
        
        # Nodes
        static_tf_node,
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        pipette_controller_spawner,
        move_group_node,
        rviz_node,
    ])