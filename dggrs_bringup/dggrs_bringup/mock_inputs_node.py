from rclpy.node import Node
import rclpy
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import Float64

from .mock_inputs import MockInputConfig, build_mock_input_state


class MockInputsNode(Node):
    """Publish synthetic camera and altitude inputs for local end-to-end demos."""

    def __init__(self) -> None:
        super().__init__("mock_inputs_node")
        self.declare_parameter("image_width", 1280)
        self.declare_parameter("image_height", 720)
        self.declare_parameter("altitude_m", 8.0)
        self.declare_parameter("frame_id", "camera_optical_frame")
        self.declare_parameter("publish_period_s", 0.5)

        self._image_pub = self.create_publisher(Image, "/camera/image_raw", 10)
        self._camera_info_pub = self.create_publisher(CameraInfo, "/camera/camera_info", 10)
        self._altitude_pub = self.create_publisher(Float64, "/rtk/altitude_m", 10)

        period = float(self.get_parameter("publish_period_s").value)
        self.create_timer(period, self._publish_state)

    def _publish_state(self) -> None:
        state = build_mock_input_state(
            MockInputConfig(
                image_width=int(self.get_parameter("image_width").value),
                image_height=int(self.get_parameter("image_height").value),
                altitude_m=float(self.get_parameter("altitude_m").value),
                frame_id=str(self.get_parameter("frame_id").value),
            )
        )

        stamp = self.get_clock().now().to_msg()

        image = Image()
        image.header.stamp = stamp
        image.header.frame_id = state.frame_id
        image.height = state.image_height
        image.width = state.image_width
        image.encoding = "rgb8"
        image.step = state.image_width * 3
        image.data = bytes(image.height * image.step)
        self._image_pub.publish(image)

        camera_info = CameraInfo()
        camera_info.header.stamp = stamp
        camera_info.header.frame_id = state.frame_id
        camera_info.height = state.image_height
        camera_info.width = state.image_width
        camera_info.k = list(state.camera_matrix)
        camera_info.p = [
            state.camera_matrix[0],
            state.camera_matrix[1],
            state.camera_matrix[2],
            0.0,
            state.camera_matrix[3],
            state.camera_matrix[4],
            state.camera_matrix[5],
            0.0,
            state.camera_matrix[6],
            state.camera_matrix[7],
            state.camera_matrix[8],
            0.0,
        ]
        self._camera_info_pub.publish(camera_info)

        altitude = Float64()
        altitude.data = state.altitude_m
        self._altitude_pub.publish(altitude)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = MockInputsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
