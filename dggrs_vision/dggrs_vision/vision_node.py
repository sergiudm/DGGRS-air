from geometry_msgs.msg import Pose2D
from rclpy.node import Node
import rclpy
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import Bool

from .tracker import estimate_robot_pose


class VisionNode(Node):
    """Placeholder vision frontend that exposes the documented interfaces."""

    def __init__(self) -> None:
        super().__init__("vision_node")
        self.declare_parameter("detection_backend", "apriltag")
        self.declare_parameter("marker_family", "tag36h11")
        self.declare_parameter("confidence_threshold", 0.75)
        self.declare_parameter("publish_debug_image", True)
        self.declare_parameter("image_transport", "raw")
        self.declare_parameter("max_detection_age_ms", 250)
        self.declare_parameter("mock_detection_enabled", True)
        self.declare_parameter("default_theta_rad", 0.0)

        self._camera_info: CameraInfo | None = None
        self._pose_pub = self.create_publisher(Pose2D, "/vision/robot_pose_2d", 10)
        self._debug_pub = self.create_publisher(Image, "/vision/debug_image", 10)
        self._visible_pub = self.create_publisher(Bool, "/vision/target_visible", 10)

        self.create_subscription(Image, "/camera/image_raw", self._on_image, 10)
        self.create_subscription(CameraInfo, "/camera/camera_info", self._on_camera_info, 10)

        self.get_logger().info(
            "dggrs_vision scaffold started with backend '%s'."
            % self.get_parameter("detection_backend").value
        )

    def _on_camera_info(self, msg: CameraInfo) -> None:
        self._camera_info = msg

    def _on_image(self, msg: Image) -> None:
        visible = Bool()
        visible.data = bool(self.get_parameter("mock_detection_enabled").value)
        self._visible_pub.publish(visible)
        if not visible.data:
            return

        estimate = estimate_robot_pose(
            image_width=self._camera_info.width if self._camera_info else image.width,
            image_height=self._camera_info.height if self._camera_info else image.height,
            theta_rad=float(self.get_parameter("default_theta_rad").value),
        )
        pose = Pose2D()
        pose.x = estimate.x_px
        pose.y = estimate.y_px
        pose.theta = estimate.theta_rad
        self._pose_pub.publish(pose)

        if bool(self.get_parameter("publish_debug_image").value):
            self._debug_pub.publish(msg)

def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
