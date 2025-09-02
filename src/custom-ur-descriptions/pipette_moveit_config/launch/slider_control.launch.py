#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """
    Launch pipette driver with RViz visualization and manual joint control.
    Provides joint sliders to manually set joint positions without MoveIt.
    Alternative to full MoveIt Motion Planning interface.
    """
    
    # Arguments
    serial_port_arg = DeclareLaunchArgument('serial_port', default_value='/dev/ttyUR')
    baudrate_arg = DeclareLaunchArgument('baudrate', default_value='115200')
    use_fake_hardware_arg = DeclareLaunchArgument('use_fake_hardware', default_value='false')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')
    
    serial_port = LaunchConfiguration('serial_port')
    baudrate = LaunchConfiguration('baudrate')
    use_fake_hardware = LaunchConfiguration('use_fake_hardware')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Get URDF content
    pipette_description_path = get_package_share_directory("pipette_description")
    urdf_file = os.path.join(pipette_description_path, "urdf", "pipette.urdf.xacro")
    
    # Robot description parameter (processed URDF)
    from launch.substitutions import Command
    robot_description_content = Command([
        'xacro ', urdf_file,
        ' parent:=tool0'
    ])
    
    robot_description = {'robot_description': robot_description_content}

    # Robot State Publisher - publishes TF from URDF
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[
            robot_description,
            {"use_sim_time": use_sim_time},
        ],
    )

    # Joint State Publisher GUI - provides sliders for manual control
    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        parameters=[
            robot_description,
            {"use_sim_time": use_sim_time},
        ],
    )

    # RViz with basic robot model visualization
    rviz_config_path = os.path.join(
        get_package_share_directory("pipette_description"), 
        "rviz", 
        "pipette_demo.rviz"
    )
    
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_path],
        parameters=[
            robot_description,
            {"use_sim_time": use_sim_time},
        ],
    )

    # Pipette Driver Node - for actual hardware control
    pipette_driver_node = Node(
        package='pipette_driver',
        executable='pipette_driver_node',
        name='pipette_driver_node',
        output='screen',
        parameters=[{
            'serial_port': serial_port,
            'baudrate': baudrate,
            'use_fake_hardware': use_fake_hardware,
            'use_sim_time': use_sim_time,
        }],
    )

    # Joint State Bridge - converts GUI slider positions to hardware commands
    joint_state_bridge_node = Node(
        package='pipette_driver',
        executable='joint_state_bridge',
        name='joint_state_bridge',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
        }],
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
        serial_port_arg,
        baudrate_arg,
        use_fake_hardware_arg,
        use_sim_time_arg,
        
        # Nodes
        static_tf_node,
        robot_state_publisher,
        joint_state_publisher_gui,  # This gives you manual sliders
        rviz_node,
        pipette_driver_node,
        joint_state_bridge_node,  # Converts slider positions to hardware commands
    ])