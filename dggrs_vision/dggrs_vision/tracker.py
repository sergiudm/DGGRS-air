from dataclasses import dataclass


@dataclass(frozen=True)
class RobotPoseEstimate:
    x_px: float
    y_px: float
    theta_rad: float


def estimate_robot_pose(image_width: int, image_height: int, theta_rad: float = 0.0) -> RobotPoseEstimate:
    return RobotPoseEstimate(
        x_px=float(image_width) / 2.0,
        y_px=float(image_height) / 2.0,
        theta_rad=theta_rad,
    )
