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
    Launch file for pipette MoveIt demo with action-based control.
    This connects our pipette_driver_node to MoveIt for motion planning.
    """
    
    ## Arguments
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')
    serial_port_arg = DeclareLaunchArgument('serial_port', default_value='/tmp/ttyUR')
    baudrate_arg = DeclareLaunchArgument('baudrate', default_value='115200')
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    serial_port = LaunchConfiguration('serial_port')
    baudrate = LaunchConfiguration('baudrate')

    # MoveIt Configuration
    moveit_config = (
        MoveItConfigsBuilder("ur", package_name="ur5e_pipette_moveit_config")
        .robot_description(file_path=os.path.join(
            get_package_share_directory("pipette_description"), 
            "urdf", 
            "pipette.urdf.xacro"
        ), mappings={
            "use_fake_hardware": "true",  # Use fake hardware for visualization
            "serial_port": "/tmp/ttyUR",
            "baudrate": "115200"
        })
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=True, 
            publish_robot_description_semantic=True
        )
        .planning_pipelines(pipelines=["ompl", "pilz_industrial_motion_planner"])
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
            get_package_share_directory("ur5e_pipette_moveit_config"), 
            "rviz", 
            "view_robot.rviz"
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

    # Joint State Publisher (for fake hardware)
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        parameters=[
            moveit_config.robot_description,
            {"use_sim_time": use_sim_time},
        ],
    )

    # Pipette Driver Node (our action-based controller)
    pipette_driver_node = Node(
        package='pipette_driver',
        executable='pipette_driver_node',
        name='pipette_driver_node',
        output='screen',
        parameters=[{
            'serial_port': serial_port,
            'baudrate': baudrate,
            'use_sim_time': use_sim_time,
        }],
    )

    # Static transform publisher (map to base_link)
    static_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0", "0", "0", "0", "0", "0", "map", "base_link"],
    )

    return LaunchDescription([
        # Arguments
        use_sim_time_arg,
        serial_port_arg,
        baudrate_arg,
        
        # Nodes
        static_tf_node,
        robot_state_publisher,
        joint_state_publisher,
        move_group_node,
        rviz_node,
        pipette_driver_node,
    ])