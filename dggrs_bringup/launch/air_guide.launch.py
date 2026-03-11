from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    vision_config = PathJoinSubstitution([FindPackageShare("dggrs_bringup"), "config", "vision.yaml"])
    streamer_config = PathJoinSubstitution([FindPackageShare("dggrs_bringup"), "config", "streamer.yaml"])
    bridge_config = PathJoinSubstitution([FindPackageShare("dggrs_bringup"), "config", "bridge.yaml"])
    spatial_math_config = PathJoinSubstitution(
        [FindPackageShare("dggrs_bringup"), "config", "spatial_math.yaml"]
    )
    mock_inputs_config = PathJoinSubstitution(
        [FindPackageShare("dggrs_bringup"), "config", "mock_inputs.yaml"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("detection_backend", default_value="apriltag"),
            DeclareLaunchArgument("stream_mode", default_value="rtsp"),
            DeclareLaunchArgument("overlay_enabled", default_value="false"),
            DeclareLaunchArgument("use_mock_inputs", default_value="false"),
            Node(
                package="dggrs_bringup",
                executable="mock_inputs_node",
                name="mock_inputs_node",
                output="screen",
                parameters=[mock_inputs_config],
                condition=IfCondition(LaunchConfiguration("use_mock_inputs")),
            ),
            Node(
                package="dggrs_vision",
                executable="vision_node",
                name="vision_node",
                output="screen",
                parameters=[
                    vision_config,
                    {"detection_backend": LaunchConfiguration("detection_backend")},
                ],
            ),
            Node(
                package="dggrs_streamer",
                executable="streamer_node",
                name="streamer_node",
                output="screen",
                parameters=[
                    streamer_config,
                    {
                        "transport_mode": LaunchConfiguration("stream_mode"),
                        "overlay_enabled": LaunchConfiguration("overlay_enabled"),
                    },
                ],
            ),
            Node(
                package="dggrs_spatial_math",
                executable="spatial_math_node",
                name="spatial_math_node",
                output="screen",
                parameters=[spatial_math_config],
            ),
            Node(
                package="dggrs_bridge",
                executable="bridge_node",
                name="bridge_node",
                output="screen",
                parameters=[bridge_config],
            ),
        ]
    )
