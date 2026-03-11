from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description() -> LaunchDescription:
    bridge_config = PathJoinSubstitution([FindPackageShare("dggrs_bringup"), "config", "bridge.yaml"])
    spatial_math_config = PathJoinSubstitution(
        [FindPackageShare("dggrs_bringup"), "config", "spatial_math.yaml"]
    )
    return LaunchDescription(
        [
            Node(
                package="dggrs_bridge",
                executable="bridge_node",
                name="bridge_node",
                output="screen",
                parameters=[bridge_config],
            ),
            Node(
                package="dggrs_spatial_math",
                executable="spatial_math_node",
                name="spatial_math_node",
                output="screen",
                parameters=[spatial_math_config],
            ),
        ]
    )
