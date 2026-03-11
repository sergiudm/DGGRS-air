from __future__ import annotations

from geometry_msgs.msg import Point, Pose2D, PoseStamped, Vector3Stamped
from rclpy.node import Node
import rclpy
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import Float64

from .core import CameraIntrinsics, GoalRequest, compute_goal


class SpatialMathNode(Node):
    """Compute relative goal positions from clicks, robot pose, altitude, and intrinsics."""

    def __init__(self) -> None:
        super().__init__("spatial_math_node")
        self.declare_parameter("max_click_age_ms", 500)
        self.declare_parameter("max_robot_pose_age_ms", 500)
        self.declare_parameter("min_altitude_m", 0.5)
        self.declare_parameter("max_altitude_m", 100.0)
        self.declare_parameter("goal_frame_id", "odom")
        self.declare_parameter("publish_debug_topics", True)

        self._click: Point | None = None
        self._robot_pose: Pose2D | None = None
        self._altitude_m: float | None = None
        self._camera_info: CameraInfo | None = None
        self._click_stamp_ns: int | None = None
        self._robot_stamp_ns: int | None = None

        self._goal_pub = self.create_publisher(PoseStamped, "/ground_robot/goal_pose", 10)
        self._debug_pub = self.create_publisher(Vector3Stamped, "/spatial_math/debug_vector", 10)

        self.create_subscription(Point, "/ui/target_click", self._on_click, 10)
        self.create_subscription(Pose2D, "/vision/robot_pose_2d", self._on_robot_pose, 10)
        self.create_subscription(Float64, "/rtk/altitude_m", self._on_altitude, 10)
        self.create_subscription(CameraInfo, "/camera/camera_info", self._on_camera_info, 10)

    def _on_click(self, msg: Point) -> None:
        self._click = msg
        self._click_stamp_ns = self.get_clock().now().nanoseconds
        self._publish_goal_if_ready()

    def _on_robot_pose(self, msg: Pose2D) -> None:
        self._robot_pose = msg
        self._robot_stamp_ns = self.get_clock().now().nanoseconds
        self._publish_goal_if_ready()

    def _on_altitude(self, msg: Float64) -> None:
        self._altitude_m = float(msg.data)

    def _on_camera_info(self, msg: CameraInfo) -> None:
        self._camera_info = msg

    def _publish_goal_if_ready(self) -> None:
        if not all((self._click, self._robot_pose, self._altitude_m, self._camera_info)):
            return
        if not self._inputs_are_fresh():
            return

        goal_result = compute_goal(
            GoalRequest(
                click_x=self._click.x,
                click_y=self._click.y,
                robot_x=self._robot_pose.x,
                robot_y=self._robot_pose.y,
                robot_theta=self._robot_pose.theta,
                altitude_m=float(self._altitude_m),
            ),
            intrinsics=CameraIntrinsics(
                fx=float(self._camera_info.k[0]),
                fy=float(self._camera_info.k[4]),
                cx=float(self._camera_info.k[2]),
                cy=float(self._camera_info.k[5]),
            ),
            min_altitude_m=float(self.get_parameter("min_altitude_m").value),
            max_altitude_m=float(self.get_parameter("max_altitude_m").value),
        )
        if goal_result is None:
            self.get_logger().warn("Spatial math inputs were invalid for goal computation.")
            return

        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = str(self.get_parameter("goal_frame_id").value)
        goal.pose.position.x = goal_result.x_m
        goal.pose.position.y = goal_result.y_m
        goal.pose.position.z = 0.0
        goal.pose.orientation.w = 1.0
        self._goal_pub.publish(goal)

        if bool(self.get_parameter("publish_debug_topics").value):
            debug = Vector3Stamped()
            debug.header = goal.header
            debug.vector.x = goal_result.debug_dx_m
            debug.vector.y = goal_result.debug_dy_m
            debug.vector.z = 0.0
            self._debug_pub.publish(debug)

    def _inputs_are_fresh(self) -> bool:
        now_ns = self.get_clock().now().nanoseconds
        click_age_ms = self._age_ms(now_ns, self._click_stamp_ns)
        robot_age_ms = self._age_ms(now_ns, self._robot_stamp_ns)
        if click_age_ms is None or robot_age_ms is None:
            return False
        return (
            click_age_ms <= int(self.get_parameter("max_click_age_ms").value)
            and robot_age_ms <= int(self.get_parameter("max_robot_pose_age_ms").value)
        )

    @staticmethod
    def _age_ms(now_ns: int, stamp_ns: int | None) -> int | None:
        if stamp_ns is None:
            return None
        return int((now_ns - stamp_ns) / 1_000_000)

def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = SpatialMathNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
