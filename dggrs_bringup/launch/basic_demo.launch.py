from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    bringup_share = FindPackageShare("dggrs_bringup")
    return LaunchDescription(
        [
            Node(
                package="dggrs_bringup",
                executable="mock_inputs_node",
                name="mock_inputs_node",
                output="screen",
                parameters=[PathJoinSubstitution([bringup_share, "config", "mock_inputs.yaml"])],
            ),
            Node(
                package="dggrs_vision",
                executable="vision_node",
                name="vision_node",
                output="screen",
                parameters=[PathJoinSubstitution([bringup_share, "config", "vision.yaml"])],
            ),
            Node(
                package="dggrs_streamer",
                executable="streamer_node",
                name="streamer_node",
                output="screen",
                parameters=[PathJoinSubstitution([bringup_share, "config", "streamer.yaml"])],
            ),
            Node(
                package="dggrs_spatial_math",
                executable="spatial_math_node",
                name="spatial_math_node",
                output="screen",
                parameters=[PathJoinSubstitution([bringup_share, "config", "spatial_math.yaml"])],
            ),
            Node(
                package="dggrs_bridge",
                executable="bridge_node",
                name="bridge_node",
                output="screen",
                parameters=[
                    PathJoinSubstitution([bringup_share, "config", "bridge.yaml"]),
                    {"mock_click_enabled": True},
                ],
            ),
        ]
    )
