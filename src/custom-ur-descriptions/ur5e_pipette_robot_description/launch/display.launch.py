#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """
    Launch UR5e + pipette robot description with RViz visualization.
    Shows the combined robot model for visualization and planning.
    """
    
    # Arguments
    name_arg = DeclareLaunchArgument('name', default_value='ur')
    ur_type_arg = DeclareLaunchArgument('ur_type', default_value='ur5e')
    tf_prefix_arg = DeclareLaunchArgument('tf_prefix', default_value='')
    use_fake_hardware_arg = DeclareLaunchArgument('use_fake_hardware', default_value='false')
    pipette_mass_arg = DeclareLaunchArgument('pipette_mass', default_value='0.200')
    pipette_xyz_arg = DeclareLaunchArgument('pipette_xyz', default_value='0 0 0')
    pipette_rpy_arg = DeclareLaunchArgument('pipette_rpy', default_value='0 0 0')
    
    name = LaunchConfiguration('name')
    ur_type = LaunchConfiguration('ur_type')
    tf_prefix = LaunchConfiguration('tf_prefix')
    use_fake_hardware = LaunchConfiguration('use_fake_hardware')
    pipette_mass = LaunchConfiguration('pipette_mass')
    pipette_xyz = LaunchConfiguration('pipette_xyz')
    pipette_rpy = LaunchConfiguration('pipette_rpy')

    # Get URDF content
    ur5e_pipette_description_path = get_package_share_directory("ur5e_pipette_robot_description")
    urdf_file = os.path.join(ur5e_pipette_description_path, "urdf", "ur_with_pipette.xacro")
    
    # Robot description parameter (processed URDF)
    robot_description_content = Command([
        'xacro ', urdf_file,
        ' name:=', name,
        ' ur_type:=', ur_type,
        ' tf_prefix:=', tf_prefix,
        ' use_fake_hardware:=', use_fake_hardware,
        ' pipette_mass:=', pipette_mass,
        ' pipette_xyz:="', pipette_xyz, '"',
        ' pipette_rpy:="', pipette_rpy, '"'
    ])
    
    robot_description = {'robot_description': robot_description_content}

    # Robot State Publisher - publishes TF from URDF
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    # Joint State Publisher GUI - provides sliders for joint control
    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        parameters=[robot_description],
    )

    # RViz with robot model visualization
    rviz_config_path = os.path.join(
        get_package_share_directory("ur_description"), 
        "rviz", 
        "view_robot.rviz"
    )
    
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_path],
        parameters=[robot_description],
    )

    return LaunchDescription([
        # Arguments
        name_arg,
        ur_type_arg,
        tf_prefix_arg,
        use_fake_hardware_arg,
        pipette_mass_arg,
        pipette_xyz_arg,
        pipette_rpy_arg,
        
        # Nodes
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz_node,
    ])