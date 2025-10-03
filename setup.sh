#!/bin/bash
set -e

vcs import < src/ros2.repos src
vcs import < src/end_effectors/end_effectors.repos src/end_effectors
sudo apt-get update
rosdep update

# Skip moveit_studio_behavior_interface because we are not using it and is paywalled
rosdep install --from-paths src --ignore-src -y --skip-keys moveit_studio_behavior_interface
