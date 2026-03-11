from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from geometry_msgs.msg import Point, PoseStamped
from rclpy.node import Node
import rclpy

from .core import Click, validate_click


class BridgeNode(Node):
    """Bridge scaffold that keeps ROS-side contracts stable while transport work is pending."""

    def __init__(self) -> None:
        super().__init__("bridge_node")
        self.declare_parameter("ui_transport", "websocket")
        self.declare_parameter("ui_bind_host", "0.0.0.0")
        self.declare_parameter("ui_bind_port", 9000)
        self.declare_parameter("ground_robot_transport", "ros2")
        self.declare_parameter("allowed_origin", "*")
        self.declare_parameter("click_timeout_ms", 500)
        self.declare_parameter("goal_retry_count", 3)
        self.declare_parameter("image_width", 1280)
        self.declare_parameter("image_height", 720)
        self.declare_parameter("mock_click_enabled", False)
        self.declare_parameter("mock_click_x", 640.0)
        self.declare_parameter("mock_click_y", 480.0)
        self.declare_parameter("mock_click_period_s", 2.0)

        self._goal_count = 0
        self._click_pub = self.create_publisher(Point, "/ui/target_click", 10)
        self._status_pub = self.create_publisher(DiagnosticArray, "/bridge/status", 10)
        self.create_subscription(PoseStamped, "/ground_robot/goal_pose", self._on_goal, 10)
        self.create_timer(1.0, self._publish_status)

        if bool(self.get_parameter("mock_click_enabled").value):
            period = float(self.get_parameter("mock_click_period_s").value)
            self.create_timer(period, self._publish_mock_click)

        self.get_logger().info(
            "dggrs_bridge scaffold started using '%s' UI transport."
            % self.get_parameter("ui_transport").value
        )

    def _publish_mock_click(self) -> None:
        click = Point()
        click.x = float(self.get_parameter("mock_click_x").value)
        click.y = float(self.get_parameter("mock_click_y").value)
        if not self._click_in_bounds(click):
            self.get_logger().warn("Mock click is outside configured image bounds; skipping publish.")
            return
        self._click_pub.publish(click)

    def _click_in_bounds(self, click: Point) -> bool:
        return validate_click(
            Click(x=click.x, y=click.y),
            image_width=int(self.get_parameter("image_width").value),
            image_height=int(self.get_parameter("image_height").value),
        )

    def _on_goal(self, msg: PoseStamped) -> None:
        self._goal_count += 1
        self.get_logger().info(
            "Forwarding placeholder goal #%d at (%.3f, %.3f) in %s."
            % (
                self._goal_count,
                msg.pose.position.x,
                msg.pose.position.y,
                msg.header.frame_id,
            )
        )

    def _publish_status(self) -> None:
        status = DiagnosticStatus()
        status.name = "dggrs_bridge"
        status.hardware_id = "placeholder"
        status.level = DiagnosticStatus.OK
        status.message = "ROS interface active; external transport scaffold only"
        status.values = [
            KeyValue(key="ui_transport", value=str(self.get_parameter("ui_transport").value)),
            KeyValue(key="ui_bind_host", value=str(self.get_parameter("ui_bind_host").value)),
            KeyValue(key="ui_bind_port", value=str(self.get_parameter("ui_bind_port").value)),
            KeyValue(
                key="ground_robot_transport",
                value=str(self.get_parameter("ground_robot_transport").value),
            ),
            KeyValue(key="goals_seen", value=str(self._goal_count)),
        ]

        msg = DiagnosticArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.status = [status]
        self._status_pub.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = BridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
