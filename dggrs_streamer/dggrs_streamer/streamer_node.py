from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rclpy.node import Node
import rclpy
from sensor_msgs.msg import Image


class StreamerNode(Node):
    """Streaming placeholder that reports health and frame activity."""

    def __init__(self) -> None:
        super().__init__("streamer_node")
        self.declare_parameter("source_topic", "/camera/image_raw")
        self.declare_parameter("transport_mode", "rtsp")
        self.declare_parameter("codec", "h264")
        self.declare_parameter("bitrate_kbps", 4000)
        self.declare_parameter("gop_size", 30)
        self.declare_parameter("bind_host", "0.0.0.0")
        self.declare_parameter("bind_port", 8554)
        self.declare_parameter("overlay_enabled", False)

        self._frames_seen = 0
        self._last_frame_ns: int | None = None

        source_topic = str(self.get_parameter("source_topic").value)
        self._status_pub = self.create_publisher(DiagnosticArray, "/streamer/status", 10)
        self.create_subscription(Image, source_topic, self._on_image, 10)
        self.create_timer(1.0, self._publish_status)

        self.get_logger().info(
            "dggrs_streamer scaffold listening to '%s' in %s mode."
            % (source_topic, self.get_parameter("transport_mode").value)
        )

    def _on_image(self, _: Image) -> None:
        self._frames_seen += 1
        self._last_frame_ns = self.get_clock().now().nanoseconds

    def _publish_status(self) -> None:
        status = DiagnosticStatus()
        status.name = "dggrs_streamer"
        status.hardware_id = "placeholder"
        status.level = DiagnosticStatus.OK if self._last_frame_ns else DiagnosticStatus.WARN
        status.message = (
            "Awaiting source frames" if self._last_frame_ns is None else "Receiving source frames"
        )
        status.values = [
            KeyValue(key="transport_mode", value=str(self.get_parameter("transport_mode").value)),
            KeyValue(key="codec", value=str(self.get_parameter("codec").value)),
            KeyValue(key="frames_seen", value=str(self._frames_seen)),
            KeyValue(key="bind_host", value=str(self.get_parameter("bind_host").value)),
            KeyValue(key="bind_port", value=str(self.get_parameter("bind_port").value)),
        ]

        msg = DiagnosticArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.status = [status]
        self._status_pub.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = StreamerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
