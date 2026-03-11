from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description() -> LaunchDescription:
    vision_config = PathJoinSubstitution([FindPackageShare("dggrs_bringup"), "config", "vision.yaml"])
    return LaunchDescription(
        [
            Node(
                package="dggrs_vision",
                executable="vision_node",
                name="vision_node",
                output="screen",
                parameters=[vision_config],
            ),
        ]
    )
